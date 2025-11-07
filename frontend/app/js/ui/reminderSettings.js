// Reminder Settings Module
// Handles localStorage-based reminder preferences
import { showToast } from "../state.js";

const REMINDER_STORAGE_KEY = "kira_reminder_preferences";

// Default reminder settings
const DEFAULT_SETTINGS = {
  reminderDays: 0  // Default: 0 days (no reminder)
};

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
  
  const reminderDays = settings.reminderDays || 0;
  
  // If reminderDays is 0, no reminders
  if (reminderDays <= 0) return [];
  
  const reminderDate = new Date(deadline.getTime() - (reminderDays * 24 * 60 * 60 * 1000));
  
  return [{
    date: reminderDate,
    days: reminderDays,
    taskId: task.id,
    taskTitle: task.title,
    deadline: deadline
  }];
}

// Check if a task is upcoming based on reminder settings
export function isTaskUpcoming(task, settings) {
  if (!task.deadline) return false;
  
  const reminderDays = settings.reminderDays || 0;
  if (reminderDays <= 0) return false;
  
  const deadline = new Date(task.deadline);
  if (isNaN(deadline.getTime())) return false;
  
  const now = new Date();
  const reminderDate = new Date(deadline.getTime() - (reminderDays * 24 * 60 * 60 * 1000));
  
  // Task is upcoming if we're within the reminder window (with 1 day tolerance)
  const oneDayMs = 24 * 60 * 60 * 1000;
  return now >= reminderDate && now <= deadline.getTime() + oneDayMs;
}

// Load settings to UI
function loadSettingsToUI() {
  const settings = loadReminderSettings();
  const reminderDaysInput = document.getElementById("reminderDays");
  if (reminderDaysInput) {
    reminderDaysInput.value = settings.reminderDays || 0;
  }
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
  
  // Open settings dialog
  btnSettings.addEventListener("click", () => {
    loadSettingsToUI();
    dlgReminderSettings.showModal();
  });
  
  // Save settings
  btnSave.addEventListener("click", () => {
    const reminderDaysInput = document.getElementById("reminderDays");
    if (!reminderDaysInput) {
      showToast("Reminder days input not found", "error");
      return;
    }
    
    const reminderDays = parseInt(reminderDaysInput.value, 10);
    
    // Validate input
    if (isNaN(reminderDays) || reminderDays < 0 || reminderDays > 365) {
      showToast("Please enter a valid number between 0 and 365", "error");
      return;
    }
    
    const settings = {
      reminderDays: reminderDays
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

// Reset reminder settings to defaults
export function resetReminderSettings() {
  try {
    localStorage.removeItem(REMINDER_STORAGE_KEY);
    console.log("Reminder settings reset to defaults");
  } catch (e) {
    console.warn("Failed to reset reminder settings:", e);
  }
}
