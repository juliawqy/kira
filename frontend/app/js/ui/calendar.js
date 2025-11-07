import { CAL_MONTH, setCalMonth, addMonths, fmtYMD, parseYMD, isCurrentUserStaff } from "../state.js";
import { escapeHtml, getSubtasks } from "../state.js";
import { openCalTaskPanel } from "./cards.js";
import { loadReminderSettings, calculateReminderDates, isTaskUpcoming } from "./reminderSettings.js";

function normalizeTaskDate(task, mode){
  const by = mode === "start" ? (task.start_date || task.startDate) : (task.deadline || task.due || task.due_date);
  const fallback = mode === "start" ? (task.deadline || task.due || task.due_date) : (task.start_date || task.startDate);
  return parseYMD(by) || parseYMD(fallback) || null;
}

function isTaskOverdue(task){
  if (!task.deadline) return false;
  const deadline = parseYMD(task.deadline);
  if (!deadline) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return deadline < today && task.status !== "Completed";
}

function flattenTasksWithSubs(tasks){
  const out = [];
  (tasks||[]).forEach(t => {
    out.push({...t, __isSub:false});
    const subs = getSubtasks(t);
    if (Array.isArray(subs)) {
      // Only include subtasks that are not completed
      subs.filter(st => st.status !== "Completed").forEach(st => out.push({...st, __isSub:true, __parentId: t.id, __parentTitle: t.title}));
    }
  });
  return out;
}

export function renderCalendar(tasks, { log, reload, targetCalendarId = "calendar", targetTitleId = "calTitle", dateModeSelector = "#calDateMode" } = {}){
  const calendarPanel = document.getElementById("calendarPanel");
  const calendarEl = document.getElementById(targetCalendarId);
  const calTitle = document.getElementById(targetTitleId);
  const modeEl = document.querySelector(dateModeSelector);
  const mode = modeEl ? modeEl.value : "due";

  const year = CAL_MONTH.getFullYear();
  const month = CAL_MONTH.getMonth();
  const firstDow = new Date(year, month, 1).getDay();
  const start = new Date(year, month, 1 - firstDow);
  const labels = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

  const map = new Map();
  const reminderMap = new Map(); // Map for reminders
  
  // Load reminder settings
  const reminderSettings = loadReminderSettings();
  
  // Filter out completed tasks for calendar view
  const activeTasks = (tasks || []).filter(t => t.status !== "Completed");
  const flat = flattenTasksWithSubs(activeTasks);
  
  // Add tasks to calendar
  flat.forEach(t => {
    const d = normalizeTaskDate(t, mode);
    if (!d) return;
    const key = fmtYMD(d);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(t);
  });
  
  // Calculate and add reminders (only for deadline mode)
  if (mode === "due") {
    const reminderDays = reminderSettings.reminderDays || 0;
    if (reminderDays > 0) {
      flat.forEach(t => {
        if (!t.deadline) return;
        
        // Check if task is upcoming based on reminder settings
        if (isTaskUpcoming(t, reminderSettings)) {
          const reminders = calculateReminderDates(t, reminderSettings);
          reminders.forEach(reminder => {
            const reminderKey = fmtYMD(reminder.date);
            const today = new Date();
            today.setHours(0, 0, 0, 0);
            const reminderDay = new Date(reminder.date);
            reminderDay.setHours(0, 0, 0, 0);
            
            // Only show reminders for future dates (from today onwards)
            // Skip reminders that are in the past
            if (reminderDay >= today) {
              if (!reminderMap.has(reminderKey)) reminderMap.set(reminderKey, []);
              reminderMap.get(reminderKey).push(reminder);
            }
          });
        }
        
        // Also show overdue tasks
        if (isTaskOverdue(t)) {
          const deadlineKey = fmtYMD(parseYMD(t.deadline));
          if (!reminderMap.has(deadlineKey)) reminderMap.set(deadlineKey, []);
          reminderMap.get(deadlineKey).push({
            date: parseYMD(t.deadline),
            days: 0,
            taskId: t.id,
            taskTitle: t.title,
            deadline: parseYMD(t.deadline),
            isOverdue: true
          });
        }
      });
    }
  }

  calTitle.textContent = CAL_MONTH.toLocaleString(undefined, { month: "long", year: "numeric" });

  const frag = document.createDocumentFragment();
  const hdrRow = document.createElement("div");
  hdrRow.className = "cal-grid";
  labels.forEach(lbl => {
    const c = document.createElement("div");
    c.className = "cal-colhdr";
    c.textContent = lbl;
    hdrRow.appendChild(c);
  });
  frag.appendChild(hdrRow);

  let cur = new Date(start);
  for (let i=0; i<6; i++){
    const row = document.createElement("div");
    row.className = "cal-grid cal-row";
    for (let j=0; j<7; j++){
      const cell = document.createElement("div");
      cell.className = "cal-cell";
      if (cur.getMonth() !== month) cell.classList.add("cal-other-month");

      const day = document.createElement("div");
      day.className = "cal-day";
      const today = new Date(); today.setHours(0,0,0,0);
      const isToday = cur.getTime() === today.getTime();
      day.innerHTML = `<span>${cur.getDate()}</span>` + (isToday ? `<span class="pill ok">Today</span>` : `<span></span>`);
      cell.appendChild(day);

      const key = fmtYMD(cur);
      const items = map.get(key) || [];
      const reminders = reminderMap.get(key) || [];
      
      // Render reminders first (up to 3, then show tasks)
      let displayCount = 0;
      const maxDisplay = 5;
      
      reminders.slice(0, Math.min(3, maxDisplay)).forEach(reminder => {
        const el = document.createElement("div");
        el.className = "cal-task cal-task-reminder";
        
        // Check if the reminder is for an overdue task
        const today = new Date();
        today.setHours(0, 0, 0, 0);
        if (reminder.isOverdue || reminder.deadline < today) {
          el.classList.add("cal-task-overdue-reminder");
        }
        
        const title = escapeHtml(reminder.taskTitle || `Task #${reminder.taskId}`);
        let reminderText = "";
        if (reminder.isOverdue) {
          const daysOverdue = Math.floor((today - reminder.deadline) / (24 * 60 * 60 * 1000));
          reminderText = `${daysOverdue} day${daysOverdue !== 1 ? 's' : ''} overdue`;
        } else if (reminder.days !== undefined) {
          reminderText = reminder.days === 1 ? "1 day before" : `${reminder.days} days before`;
        } else {
          reminderText = "reminder";
        }
        el.innerHTML = `🔔 Reminder: ${title} <span class="small">(${reminderText})</span>`;
        el.title = `Reminder: ${title} - ${reminderText}`;
        
        // Find the original task and open it on click
        const originalTask = flat.find(t => t.id === reminder.taskId);
        if (originalTask) {
          el.addEventListener("click", () => openCalTaskPanel(originalTask, { log, reload }));
        }
        cell.appendChild(el);
        displayCount++;
      });
      
      // Render tasks (adjust count based on reminders shown)
      const remainingSlots = maxDisplay - displayCount;
      items.slice(0, remainingSlots).forEach(t => {
        const el = document.createElement("div");
        el.className = "cal-task";
        
        // Add status-based styling
        if (isTaskOverdue(t)) {
          el.classList.add("cal-task-overdue");
        } else if (t.status === "In-progress") {
          el.classList.add("cal-task-inprogress");
        } else if (t.status === "Blocked") {
          el.classList.add("cal-task-blocked");
        } else if (t.status === "To-do") {
          el.classList.add("cal-task-todo");
        }
        
        const title = escapeHtml(t.title || `(untitled #${t.id})`);
        const project = (t.project_id != null) ? `· P${t.project_id}` : "";
        el.innerHTML = `${t.__isSub ? "↳ " : ""}${title} <span class="small">${project}</span>`;
        el.title = `${title}${project ? " " + project : ""}`;
        el.addEventListener("click", () => openCalTaskPanel(t, { log, reload }));
        cell.appendChild(el);
        displayCount++;
      });
      
      const totalItems = items.length + reminders.length;
      if (totalItems > maxDisplay) {
        const more = document.createElement("div");
        more.className = "small muted";
        more.textContent = `+${totalItems - maxDisplay} more`;
        cell.appendChild(more);
      }

      row.appendChild(cell);
      cur.setDate(cur.getDate()+1);
    }
    frag.appendChild(row);
  }

  calendarEl.innerHTML = "";
  calendarEl.appendChild(frag);
}

export function bindCalendarNav(){
  document.getElementById("calPrev").addEventListener("click", () => {
    setCalMonth(addMonths(CAL_MONTH, -1));
    document.dispatchEvent(new Event("redraw-calendar"));
  });
  document.getElementById("calNext").addEventListener("click", () => {
    setCalMonth(addMonths(CAL_MONTH, +1));
    document.dispatchEvent(new Event("redraw-calendar"));
  });
}
