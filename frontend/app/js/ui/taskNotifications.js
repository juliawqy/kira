// Task Notifications Module
// Handles client-side notification logic for overdue and upcoming tasks
import { apiTask } from "../api.js";
import { LAST_TASKS, CURRENT_USER } from "../state.js";
import { loadReminderSettings, isTaskUpcoming } from "./reminderSettings.js";

const NOTIFICATION_TRACKING_KEY = "kira_notification_tracking";
const LAST_CHECK_DATE_KEY = "kira_last_notification_check_date";

// Check if a task is overdue
function isTaskOverdue(task) {
  if (!task.deadline || task.status === "Completed") return false;
  
  const deadline = new Date(task.deadline);
  if (isNaN(deadline.getTime())) return false;
  
  const now = new Date();
  // Set to start of day for comparison
  const deadlineDate = new Date(deadline.getFullYear(), deadline.getMonth(), deadline.getDate());
  const today = new Date(now.getFullYear(), now.getMonth(), now.getDate());
  
  return deadlineDate < today;
}

// Get notification tracking data
function getNotificationTracking() {
  try {
    const stored = localStorage.getItem(NOTIFICATION_TRACKING_KEY);
    if (stored) {
      return JSON.parse(stored);
    }
  } catch (e) {
    console.warn("Failed to load notification tracking:", e);
  }
  return {};
}

// Save notification tracking data
function saveNotificationTracking(tracking) {
  try {
    localStorage.setItem(NOTIFICATION_TRACKING_KEY, JSON.stringify(tracking));
    return true;
  } catch (e) {
    console.error("Failed to save notification tracking:", e);
    return false;
  }
}

// Check if we should reset tracking (new day)
function shouldResetTracking() {
  try {
    const lastCheckDate = localStorage.getItem(LAST_CHECK_DATE_KEY);
    const today = new Date().toDateString();
    
    if (lastCheckDate !== today) {
      localStorage.setItem(LAST_CHECK_DATE_KEY, today);
      return true;
    }
    return false;
  } catch (e) {
    console.warn("Failed to check reset tracking:", e);
    return false;
  }
}

// Mark notification as sent
function markNotificationSent(taskId, type) {
  const tracking = getNotificationTracking();
  const key = `${taskId}_${type}`;
  tracking[key] = true;
  saveNotificationTracking(tracking);
  console.log(`[Notification] Marked ${type} notification as sent for task ${taskId}`);
}

// Check if notification was already sent
function wasNotificationSent(taskId, type) {
  const tracking = getNotificationTracking();
  const key = `${taskId}_${type}`;
  return tracking[key] === true;
}

// Send upcoming task notification
async function sendUpcomingNotification(task) {
  try {
    console.log(`[Notification] Sending upcoming notification for task ${task.id}: ${task.title}`);
    const response = await apiTask(`/${task.id}/notify-upcoming`, {
      method: "POST"
    });
    console.log(`[Notification] Upcoming notification response:`, response);
    markNotificationSent(task.id, "upcoming");
    return response;
  } catch (e) {
    console.error(`[Notification] Failed to send upcoming notification for task ${task.id}:`, e);
    return null;
  }
}

// Send overdue task notification
async function sendOverdueNotification(task) {
  try {
    console.log(`[Notification] Sending overdue notification for task ${task.id}: ${task.title}`);
    const response = await apiTask(`/${task.id}/notify-overdue`, {
      method: "POST"
    });
    console.log(`[Notification] Overdue notification response:`, response);
    markNotificationSent(task.id, "overdue");
    return response;
  } catch (e) {
    console.error(`[Notification] Failed to send overdue notification for task ${task.id}:`, e);
    return null;
  }
}

// Check and send notifications for all tasks
export async function checkAndSendNotifications() {
  if (!CURRENT_USER) {
    console.log("[Notification] No current user, skipping notification check");
    return;
  }
  
  console.log(`[Notification] Starting notification check for user: ${CURRENT_USER.name} (${CURRENT_USER.user_id})`);
  
  // Reset tracking if it's a new day
  if (shouldResetTracking()) {
    console.log("[Notification] New day detected, resetting notification tracking");
    resetNotificationTracking();
  }
  
  const settings = loadReminderSettings();
  console.log(`[Notification] Reminder settings:`, settings);
  
  if (!LAST_TASKS || LAST_TASKS.length === 0) {
    console.log("[Notification] No tasks available for notification check");
    return;
  }
  
  // Filter tasks assigned to current user
  const userTasks = LAST_TASKS.filter(task => {
    if (!task.assignments || !Array.isArray(task.assignments)) return false;
    return task.assignments.some(assignment => assignment.user_id === CURRENT_USER.user_id);
  });
  
  console.log(`[Notification] Found ${userTasks.length} tasks assigned to current user`);
  
  const reminderDays = settings.reminderDays || 0;
  console.log(`[Notification] Reminder days setting: ${reminderDays}`);
  
  // Check for upcoming tasks
  if (reminderDays > 0) {
    const upcomingTasks = userTasks.filter(task => {
      if (task.status === "Completed") return false;
      if (wasNotificationSent(task.id, "upcoming")) {
        console.log(`[Notification] Upcoming notification already sent for task ${task.id}`);
        return false;
      }
      return isTaskUpcoming(task, settings);
    });
    
    console.log(`[Notification] Found ${upcomingTasks.length} upcoming tasks`);
    
    for (const task of upcomingTasks) {
      await sendUpcomingNotification(task);
    }
  } else {
    console.log("[Notification] Reminder days is 0, skipping upcoming task notifications");
  }
  
  // Check for overdue tasks
  const overdueTasks = userTasks.filter(task => {
    if (task.status === "Completed") return false;
    if (wasNotificationSent(task.id, "overdue")) {
      console.log(`[Notification] Overdue notification already sent for task ${task.id}`);
      return false;
    }
    return isTaskOverdue(task);
  });
  
  console.log(`[Notification] Found ${overdueTasks.length} overdue tasks`);
  
  for (const task of overdueTasks) {
    await sendOverdueNotification(task);
  }
  
  console.log("[Notification] Notification check completed");
}

// Reset notification tracking
export function resetNotificationTracking() {
  try {
    localStorage.removeItem(NOTIFICATION_TRACKING_KEY);
    console.log("[Notification] Notification tracking reset");
  } catch (e) {
    console.warn("[Notification] Failed to reset notification tracking:", e);
  }
}

