// Task Notification Checker Module
// Checks for overdue and upcoming tasks and sends notifications once per day/session
import { apiTask } from "../api.js";
import { loadReminderSettings, calculateReminderDates } from "./reminderSettings.js";
import { parseYMD } from "../state.js";

const NOTIFICATION_STORAGE_KEY = "kira_notifications_sent";
const SESSION_DATE_KEY = "kira_notification_session_date";

/**
 * Get today's date string in YYYY-MM-DD format
 */
function getTodayDateString() {
  const today = new Date();
  return today.toISOString().split('T')[0];
}

/**
 * Load sent notifications from localStorage
 * Returns a Set of notification keys (e.g., "overdue_123" or "upcoming_456_1day")
 */
function loadSentNotifications() {
  try {
    const storedDate = localStorage.getItem(SESSION_DATE_KEY);
    const today = getTodayDateString();
    
    // If session date doesn't match today, reset the sent notifications
    if (storedDate !== today) {
      localStorage.setItem(SESSION_DATE_KEY, today);
      localStorage.removeItem(NOTIFICATION_STORAGE_KEY);
      return new Set();
    }
    
    const stored = localStorage.getItem(NOTIFICATION_STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return new Set(parsed);
    }
  } catch (e) {
    console.warn("Failed to load sent notifications:", e);
  }
  return new Set();
}

/**
 * Mark a notification as sent
 * @param {string} notificationKey - Key like "overdue_123" or "upcoming_456_1day"
 */
function markNotificationSent(notificationKey) {
  try {
    const sent = loadSentNotifications();
    sent.add(notificationKey);
    localStorage.setItem(NOTIFICATION_STORAGE_KEY, JSON.stringify(Array.from(sent)));
    localStorage.setItem(SESSION_DATE_KEY, getTodayDateString());
    return true;
  } catch (e) {
    console.error("Failed to mark notification as sent:", e);
    return false;
  }
}

/**
 * Check if a task is overdue
 */
function isTaskOverdue(task) {
  if (!task.deadline || task.status === "Completed") return false;
  const deadline = parseYMD(task.deadline);
  if (!deadline) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return deadline < today;
}

/**
 * Check if a task is upcoming (deadline is approaching within reminder window)
 * @param {Object} task - Task object
 * @param {Object} settings - Reminder settings
 * @returns {Object|null} - Reminder info if upcoming, null otherwise
 */
function isTaskUpcoming(task, settings) {
  if (!task.deadline || task.status === "Completed") return null;
  
  const deadline = parseYMD(task.deadline);
  if (!deadline) return null;
  
  const now = new Date();
  const timeUntilDeadline = deadline.getTime() - now.getTime();
  
  // Don't check past deadlines (those are overdue)
  if (timeUntilDeadline < 0) return null;
  
  // Get reminder days setting
  const reminderDays = settings.reminderDays !== undefined ? settings.reminderDays : 0;
  if (reminderDays <= 0) return null;
  
  // Calculate reminder time in milliseconds
  const reminderMs = reminderDays * 24 * 60 * 60 * 1000;
  // Allow ±4 hours tolerance for day-based reminders
  const windowTolerance = 4 * 60 * 60 * 1000;
  
  // Check if deadline is approximately at the reminder time away
  // e.g., for 1 day: send if deadline is between 20-28 hours away
  const windowStart = reminderMs - windowTolerance;
  const windowEnd = reminderMs + windowTolerance;
  
  if (timeUntilDeadline >= windowStart && timeUntilDeadline <= windowEnd) {
    return {
      taskId: task.id,
      reminderDays,
      deadline
    };
  }
  
  return null;
}

/**
 * Check tasks and send notifications for overdue/upcoming tasks
 * @param {Array} tasks - Array of task objects
 * @param {Object} options - Options object
 * @param {Function} options.log - Logging function
 */
export async function checkAndSendNotifications(tasks, { log } = {}) {
  console.log("[Notification Checker] Starting notification check...");
  
  if (!tasks || tasks.length === 0) {
    console.log("[Notification Checker] No tasks to check");
    return;
  }
  
  const settings = loadReminderSettings();
  const sentNotifications = loadSentNotifications();
  const today = getTodayDateString();
  
  console.log("[Notification Checker] Settings:", {
    showUpcoming: settings.showUpcoming,
    reminderDays: settings.reminderDays,
    sessionDate: today,
    alreadySentCount: sentNotifications.size
  });
  
  // Ensure session date is set
  localStorage.setItem(SESSION_DATE_KEY, today);
  
  // Check each task
  const upcomingTasks = [];
  
  console.log(`[Notification Checker] Checking ${tasks.length} tasks...`);
  
  for (const task of tasks) {
    // Skip completed tasks
    if (task.status === "Completed") continue;
    
    // Check for upcoming tasks
    if (settings.showUpcoming) {
      const upcoming = isTaskUpcoming(task, settings);
      if (upcoming) {
        // Use reminder days in the key
        const key = `upcoming_${task.id}_${upcoming.reminderDays}days_${today}`;
        if (!sentNotifications.has(key)) {
          upcomingTasks.push({ task, key, reminderDays: upcoming.reminderDays });
          console.log(`[Notification Checker] Found upcoming task:`, {
            taskId: task.id,
            title: task.title,
            deadline: task.deadline,
            reminderDays: upcoming.reminderDays,
            key
          });
        } else {
          console.log(`[Notification Checker] Upcoming notification (${upcoming.reminderDays} days) already sent today for task ${task.id}`);
        }
      }
    }
  }
  
  console.log(`[Notification Checker] Found ${upcomingTasks.length} upcoming tasks to notify`);

  // Send notifications for upcoming tasks
  for (const { task, key, reminderDays } of upcomingTasks) {
    try {
      console.log(`[Notification Checker] 🔔 Triggering UPCOMING notification endpoint for task ${task.id}:`, {
        endpoint: `POST /task/${task.id}/notify-upcoming`,
        taskTitle: task.title,
        deadline: task.deadline,
        reminderDays
      });

      log?.("Checking upcoming notification", { taskId: task.id, taskTitle: task.title, reminderDays });
      const response = await apiTask(`/${task.id}/notify-upcoming`, { method: "POST" });

      console.log(`[Notification Checker] 📧 Upcoming notification API response:`, response);

      if (response && response.success) {
        markNotificationSent(key);
        console.log(`[Notification Checker] ✅ Upcoming notification sent successfully:`, {
          taskId: task.id,
          reminderDays,
          recipients: response.recipients_count,
          emailId: response.email_id || "N/A",
          key
        });
        log?.("Upcoming notification sent", { taskId: task.id, reminderDays, recipients: response.recipients_count });
      } else {
        console.warn(`[Notification Checker] ⚠️ Upcoming notification failed:`, {
          taskId: task.id,
          reminderDays,
          response
        });
        log?.("Upcoming notification failed", { taskId: task.id, response });
      }
    } catch (error) {
      console.error(`[Notification Checker] ❌ Error sending upcoming notification for task ${task.id}:`, error);
      log?.("Error sending upcoming notification", { taskId: task.id, error: error.message });
      // Don't mark as sent if it failed
    }
  }

  // Summary log
  if (upcomingTasks.length > 0) {
    console.log(`[Notification Checker] 📊 Summary:`, {
      upcomingSent: upcomingTasks.length,
      reminderDays: settings.reminderDays
    });
    log?.("Notification check complete", {
      upcoming: upcomingTasks.length
    });
  } else {
    console.log(`[Notification Checker] ✅ No notifications needed (all up to date or already sent today)`);
  }
}

/**
 * Clear all sent notifications (useful for testing or reset)
 */
export function clearSentNotifications() {
  try {
    localStorage.removeItem(NOTIFICATION_STORAGE_KEY);
    localStorage.removeItem(SESSION_DATE_KEY);
    return true;
  } catch (e) {
    console.error("Failed to clear sent notifications:", e);
    return false;
  }
}

/**
 * Reset notification tracking when switching users
 */
export function resetNotificationTracking() {
  return clearSentNotifications();
}

