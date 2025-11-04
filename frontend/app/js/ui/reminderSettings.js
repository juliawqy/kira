// Reminder Settings Module
// Handles localStorage-based reminder preferences
import { showToast } from "../state.js";

const REMINDER_STORAGE_KEY = "kira_reminder_preferences";

// Default reminder settings
const DEFAULT_SETTINGS = {
  reminderTimes: ["1day", "1hour"], // Default: 1 day and 1 hour before
  showUpcoming: true,
  showOverdue: true
};

// Convert reminder time string to milliseconds
function reminderTimeToMs(reminderTime) {
  switch(reminderTime) {
    case "1week":
      return 7 * 24 * 60 * 60 * 1000;
    case "1day":
      return 24 * 60 * 60 * 1000;
    case "1hour":
      return 60 * 60 * 1000;
    case "30min":
      return 30 * 60 * 1000;
    default:
      return 0;
  }
}

// Load settings from localStorage
export function loadReminderSettings() {
  try {
    const stored = localStorage.getItem(REMINDER_STORAGE_KEY);
    if (stored) {
      const parsed = JSON.parse(stored);
      return {
        ...DEFAULT_SETTINGS,
        ...parsed
      };
    }
  } catch (e) {
    console.warn("Failed to load reminder settings:", e);
  }
  return { ...DEFAULT_SETTINGS };
}

// Save settings to localStorage
export function saveReminderSettings(settings) {
  try {
    localStorage.setItem(REMINDER_STORAGE_KEY, JSON.stringify(settings));
    return true;
  } catch (e) {
    console.error("Failed to save reminder settings:", e);
    return false;
  }
}

// Calculate reminder dates for a task based on deadline
export function calculateReminderDates(task, settings) {
  if (!task.deadline) return [];
  
  const deadline = new Date(task.deadline);
  if (isNaN(deadline.getTime())) return [];
  
  const reminders = [];
  const reminderTimes = settings.reminderTimes || [];
  
  reminderTimes.forEach(reminderTime => {
    const msOffset = reminderTimeToMs(reminderTime);
    if (msOffset > 0) {
      const reminderDate = new Date(deadline.getTime() - msOffset);
      reminders.push({
        date: reminderDate,
        type: reminderTime,
        taskId: task.id,
        taskTitle: task.title,
        deadline: deadline
      });
    }
  });
  
  return reminders;
}

// Bind reminder settings dialog
export function bindReminderSettings({ log, reload } = {}) {
  const btnSettings = document.getElementById("btnSettings");
  const dlgReminderSettings = document.getElementById("dlgReminderSettings");
  const btnSave = document.getElementById("btnSaveReminderSettings");
  
  if (!btnSettings || !dlgReminderSettings || !btnSave) {
    console.warn("Reminder settings elements not found");
    return;
  }
  
  // Load and display current settings
  function loadSettingsToUI() {
    const settings = loadReminderSettings();
    
    // Set checkboxes for reminder times
    document.getElementById("reminder1day").checked = settings.reminderTimes.includes("1day");
    document.getElementById("reminder1hour").checked = settings.reminderTimes.includes("1hour");
    document.getElementById("reminder30min").checked = settings.reminderTimes.includes("30min");
    document.getElementById("reminder1week").checked = settings.reminderTimes.includes("1week");
    
    // Set checkboxes for show options
    document.getElementById("showUpcoming").checked = settings.showUpcoming !== false;
    document.getElementById("showOverdue").checked = settings.showOverdue !== false;
  }
  
  // Open settings dialog
  btnSettings.addEventListener("click", () => {
    loadSettingsToUI();
    dlgReminderSettings.showModal();
  });
  
  // Save settings
  btnSave.addEventListener("click", () => {
    const reminderTimes = [];
    if (document.getElementById("reminder1day").checked) reminderTimes.push("1day");
    if (document.getElementById("reminder1hour").checked) reminderTimes.push("1hour");
    if (document.getElementById("reminder30min").checked) reminderTimes.push("30min");
    if (document.getElementById("reminder1week").checked) reminderTimes.push("1week");
    
    const settings = {
      reminderTimes,
      showUpcoming: document.getElementById("showUpcoming").checked,
      showOverdue: document.getElementById("showOverdue").checked
    };
    
    if (saveReminderSettings(settings)) {
      showToast("Reminder settings saved successfully", "success");
      dlgReminderSettings.close();
      
      // Trigger calendar redraw if needed
      if (reload) {
        reload();
      } else {
        document.dispatchEvent(new Event("redraw-calendar"));
      }
    } else {
      showToast("Failed to save reminder settings", "error");
    }
  });
  
  // Close dialog on cancel
  dlgReminderSettings.addEventListener("close", (e) => {
    if (e.target.returnValue === "cancel") {
      e.target.close();
    }
  });
}

