// Reminder Settings Module
// Handles localStorage-based reminder preferences
import { showToast } from "../state.js";

const REMINDER_STORAGE_KEY = "kira_reminder_preferences";

// Default reminder settings
const DEFAULT_SETTINGS = {
  reminderDays: 0, // Default: 0 days (no reminders)
  showUpcoming: true
};

// Convert reminder days to milliseconds
function reminderDaysToMs(days) {
  return days * 24 * 60 * 60 * 1000;
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

// Reset reminder settings to defaults
export function resetReminderSettings() {
  try {
    localStorage.removeItem(REMINDER_STORAGE_KEY);
    return true;
  } catch (e) {
    console.error("Failed to reset reminder settings:", e);
    return false;
  }
}

// Calculate reminder dates for a task based on deadline
export function calculateReminderDates(task, settings) {
  if (!task.deadline) return [];
  
  const deadline = new Date(task.deadline);
  if (isNaN(deadline.getTime())) return [];
  
  const reminders = [];
  const reminderDays = settings.reminderDays !== undefined ? settings.reminderDays : 0;
  
  if (reminderDays > 0) {
    const msOffset = reminderDaysToMs(reminderDays);
    const reminderDate = new Date(deadline.getTime() - msOffset);
    reminders.push({
      date: reminderDate,
      days: reminderDays,
      taskId: task.id,
      taskTitle: task.title,
      deadline: deadline
    });
  }
  
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
    
    // Set reminder days input
    const reminderDaysInput = document.getElementById("reminderDays");
    const reminderDaysErr = document.getElementById("reminderDays_err");
    if (reminderDaysInput) {
      reminderDaysInput.value = settings.reminderDays !== undefined ? settings.reminderDays : 0;
    }
    if (reminderDaysErr) {
      reminderDaysErr.textContent = "";
    }
    
    // Set checkbox for show options
    document.getElementById("showUpcoming").checked = settings.showUpcoming !== false;
  }
  
  // Open settings dialog
  btnSettings.addEventListener("click", () => {
    loadSettingsToUI();
    dlgReminderSettings.showModal();
  });
  
  // Save settings
  btnSave.addEventListener("click", () => {
    const reminderDaysInput = document.getElementById("reminderDays");
    const reminderDaysErr = document.getElementById("reminderDays_err");
    
    // Validate reminder days
    const reminderDays = parseInt(reminderDaysInput.value);
    if (isNaN(reminderDays) || reminderDays < 0 || reminderDays > 365) {
      if (reminderDaysErr) {
        reminderDaysErr.textContent = "Please enter a number between 0 and 365";
      }
      reminderDaysInput.focus();
      return;
    }
    
    // Clear error
    if (reminderDaysErr) {
      reminderDaysErr.textContent = "";
    }
    
    const settings = {
      reminderDays,
      showUpcoming: document.getElementById("showUpcoming").checked
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

