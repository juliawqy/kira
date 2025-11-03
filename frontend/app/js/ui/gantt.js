// js/ui/gantt.js
import { parseYMD } from "../state.js";
import { openCalTaskPanel } from "./cards.js";

function isTaskOverdue(task) {
  if (!task.deadline) return false;
  const deadline = parseYMD(task.deadline);
  if (!deadline) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return deadline < today && task.status !== "Completed";
}

/**
 * Render Gantt view (horizontal timeline chart)
 * @param {Array<object>} tasks - All tasks to display
 * @param {{log?: Function, reload: Function}} ctx
 */
export function renderGantt(tasks, { log, reload } = {}) {
  const ganttEl = document.getElementById("timelineGantt");
  if (!ganttEl) return;
  
  ganttEl.innerHTML = "";
  
  if (!tasks || tasks.length === 0) {
    ganttEl.innerHTML = `<div class="muted">No tasks to display.</div>`;
    return;
  }
  
  // Include all tasks (including completed)
  const allTasks = tasks;
  
  if (allTasks.length === 0) {
    ganttEl.innerHTML = `<div class="muted">No tasks to display.</div>`;
    return;
  }
  
  // Group tasks by project
  const tasksByProject = {};
  allTasks.forEach(task => {
    const projectId = task.project_id || "unassigned";
    if (!tasksByProject[projectId]) {
      tasksByProject[projectId] = [];
    }
    tasksByProject[projectId].push(task);
  });
  
  // Calculate date range for timeline
  const allDates = allTasks
    .flatMap(t => [t.start_date, t.deadline])
    .filter(Boolean)
    .map(parseYMD)
    .filter(Boolean);
  
  if (allDates.length === 0) {
    ganttEl.innerHTML = `<div class="muted">No tasks with dates to display.</div>`;
    return;
  }
  
  const minDate = new Date(Math.min(...allDates));
  const maxDate = new Date(Math.max(...allDates));
  
  // Extend range a bit for better visualization
  minDate.setDate(minDate.getDate() - 2);
  maxDate.setDate(maxDate.getDate() + 5);
  
  // Generate date headers
  const dates = generateDateRange(minDate, maxDate);
  
  // Container
  const container = document.createElement("div");
  container.className = "gantt-container";
  
  // Header
  const header = document.createElement("div");
  header.className = "gantt-header";
  const headerWidth = 200 + dates.length * 50; // 200px project col + N × 50px date cols
  header.style.minWidth = `${headerWidth}px`;
  
  const projectHeaderCol = document.createElement("div");
  projectHeaderCol.className = "gantt-project-header";
  projectHeaderCol.textContent = "Projects";
  header.appendChild(projectHeaderCol);
  
  dates.forEach(date => {
    const dateHeader = document.createElement("div");
    dateHeader.className = "gantt-date-header" + (isWeekend(date) ? " gantt-date-header-weekend" : "");
    
    const month = dateHeader.appendChild(document.createElement("div"));
    month.className = "gantt-date-month";
    month.textContent = date.toLocaleDateString("en-US", { month: "short" });
    
    const day = dateHeader.appendChild(document.createElement("div"));
    day.className = "gantt-date-day";
    day.textContent = date.getDate();
    
    header.appendChild(dateHeader);
  });
  
  container.appendChild(header);
  
  // Body
  const body = document.createElement("div");
  body.className = "gantt-body";
  
  // Render each project
  Object.entries(tasksByProject).forEach(([projectId, projectTasks]) => {
    const projectSection = renderGanttProject(projectId, projectTasks, dates, minDate, { log, reload });
    body.appendChild(projectSection);
  });
  
  container.appendChild(body);
  
  // Legend
  const legend = document.createElement("div");
  legend.className = "gantt-legend";
  legend.innerHTML = `
    <div class="gantt-legend-item">
      <div class="gantt-legend-box gantt-task-bar-todo"></div>
      <span>To-do</span>
    </div>
    <div class="gantt-legend-item">
      <div class="gantt-legend-box gantt-task-bar-inprogress"></div>
      <span>In-progress</span>
    </div>
    <div class="gantt-legend-item">
      <div class="gantt-legend-box gantt-task-bar-blocked"></div>
      <span>Blocked</span>
    </div>
    <div class="gantt-legend-item">
      <div class="gantt-legend-box gantt-task-bar-completed"></div>
      <span>Completed</span>
    </div>
    <div class="gantt-legend-item">
      <div class="gantt-legend-box gantt-task-bar-overdue"></div>
      <span>Overdue</span>
    </div>
  `;
  container.appendChild(legend);
  
  ganttEl.appendChild(container);
}

/**
 * Render a Gantt project section
 */
function renderGanttProject(projectId, tasks, dates, timelineStart, { log, reload }) {
  const section = document.createElement("div");
  section.className = "gantt-project-section";
  const sectionWidth = 200 + dates.length * 50; // 200px project col + N × 50px date cols
  section.style.width = `${sectionWidth}px`;
  
  // Project header row
  const headerRow = document.createElement("div");
  headerRow.className = "gantt-project-row";
  
  // Project info column
  const projectInfo = document.createElement("div");
  projectInfo.className = "gantt-project-info";
  
  const projectName = document.createElement("div");
  projectName.className = "gantt-project-name";
  projectName.textContent = projectId === "unassigned" ? "Unassigned" : `Project #${projectId}`;
  
  const projectMeta = document.createElement("div");
  projectMeta.className = "gantt-project-meta";
  const overdueTasks = tasks.filter(t => isTaskOverdue(t));
  projectMeta.textContent = `${tasks.length} tasks${overdueTasks.length > 0 ? ` • ${overdueTasks.length} overdue` : ""}`;
  
  projectInfo.appendChild(projectName);
  projectInfo.appendChild(projectMeta);
  headerRow.appendChild(projectInfo);
  
  // Empty timeline cell for header
  const headerTimeline = document.createElement("div");
  headerTimeline.className = "gantt-timeline";
  const timelineWidth = dates.length * 50; // Each date is 50px wide
  headerTimeline.style.width = `${timelineWidth}px`;
  headerRow.appendChild(headerTimeline);
  section.appendChild(headerRow);
  
  // Create a row for EACH task
  tasks.forEach((task, index) => {
    const taskRow = document.createElement("div");
    taskRow.className = "gantt-project-row";
    
    // Empty project info cell (spacer)
    const spacerInfo = document.createElement("div");
    spacerInfo.className = "gantt-project-info";
    taskRow.appendChild(spacerInfo);
    
    // Timeline for this task
    const timeline = document.createElement("div");
    timeline.className = "gantt-timeline";
    timeline.style.width = `${timelineWidth}px`;
    
    const taskBar = renderGanttTaskBar(task, timelineStart, { log, reload });
    if (taskBar) {
      timeline.appendChild(taskBar);
    }
    
    taskRow.appendChild(timeline);
    section.appendChild(taskRow);
  });
  
  return section;
}

/**
 * Render a single Gantt task bar
 */
function renderGanttTaskBar(task, timelineStart, { log, reload }) {
  if (!task.start_date && !task.deadline) {
    return null; // Skip tasks without dates
  }
  
  const startDate = task.start_date ? parseYMD(task.start_date) : null;
  const endDate = task.deadline ? parseYMD(task.deadline) : null;
  
  if (!startDate && !endDate) return null;
  
  // Use deadline if no start date, or vice versa
  const actualStart = startDate || endDate;
  const actualEnd = endDate || startDate;
  
  // Calculate position and width
  const daysFromStart = Math.floor((actualStart - timelineStart) / (1000 * 60 * 60 * 24));
  const taskDuration = Math.max(1, Math.ceil((actualEnd - actualStart) / (1000 * 60 * 60 * 24)));
  
  const dayWidth = 50; // pixels per day (this would be configurable with zoom)
  
  const bar = document.createElement("div");
  bar.className = "gantt-task-bar";
  bar.style.left = `${daysFromStart * dayWidth}px`;
  bar.style.width = `${taskDuration * dayWidth}px`;
  
  // Apply status-based styling
  if (isTaskOverdue(task)) {
    bar.classList.add("gantt-task-bar-overdue");
  } else if (task.status === "In-progress") {
    bar.classList.add("gantt-task-bar-inprogress");
  } else if (task.status === "Blocked") {
    bar.classList.add("gantt-task-bar-blocked");
  } else if (task.status === "Completed") {
    bar.classList.add("gantt-task-bar-completed");
  } else {
    bar.classList.add("gantt-task-bar-todo");
  }
  
  // Task title
  const title = document.createElement("span");
  title.textContent = `#${task.id} ${task.title || ""}`;
  bar.appendChild(title);
  
  // Click handler
  bar.addEventListener("click", (e) => {
    e.stopPropagation();
    openCalTaskPanel(task, { log, reload });
  });
  
  return bar;
}

/**
 * Generate array of dates between start and end
 */
function generateDateRange(start, end) {
  const dates = [];
  const current = new Date(start);
  
  while (current <= end) {
    dates.push(new Date(current));
    current.setDate(current.getDate() + 1);
  }
  
  return dates;
}

/**
 * Check if date is weekend
 */
function isWeekend(date) {
  const day = date.getDay();
  return day === 0 || day === 6;
}

