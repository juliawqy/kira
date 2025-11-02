// js/ui/timeline.js
import { parseYMD, escapeHtml, getSubtasks, getAssignees, getPriorityDisplay } from "../state.js";
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
 * Render Timeline view (Jira-style horizontal timeline)
 * @param {Array<object>} tasks - All tasks to display
 * @param {{log?: Function, reload: Function}} ctx
 */
export function renderTimeline(tasks, { log, reload } = {}) {
  const timelineEl = document.getElementById("timeline");
  if (!timelineEl) return;
  
  timelineEl.innerHTML = "";
  
  if (!tasks || tasks.length === 0) {
    timelineEl.innerHTML = `<div class="muted">No tasks to display.</div>`;
    return;
  }
  
  // Filter out completed tasks for timeline (as per requirements)
  const activeTasks = tasks.filter(t => t.status !== "Completed");
  
  if (activeTasks.length === 0) {
    timelineEl.innerHTML = `<div class="muted">No active tasks to display.</div>`;
    return;
  }
  
  // Group tasks by project
  const tasksByProject = {};
  activeTasks.forEach(task => {
    const projectId = task.project_id || "unassigned";
    if (!tasksByProject[projectId]) {
      tasksByProject[projectId] = [];
    }
    tasksByProject[projectId].push(task);
  });
  
  // Create timeline header
  const timelineHeader = document.createElement("div");
  timelineHeader.className = "timeline-header";
  timelineHeader.innerHTML = `
    <div class="timeline-header-left">
      <h3 style="margin: 0;">Projects</h3>
    </div>
    <div class="timeline-header-right">
      <span>Progress</span>
    </div>
  `;
  timelineEl.appendChild(timelineHeader);
  
  // Render each project section
  Object.entries(tasksByProject).forEach(([projectId, projectTasks]) => {
    const projectSection = renderProjectSection(projectId, projectTasks, { log, reload });
    timelineEl.appendChild(projectSection);
  });
}

/**
 * Render a project section with tasks
 */
function renderProjectSection(projectId, tasks, { log, reload }) {
  const section = document.createElement("div");
  section.className = "timeline-project-section";
  
  // Calculate progress (completed vs total)
  const totalTasks = tasks.length;
  const completedSubtasks = tasks.reduce((count, task) => {
    const subs = getSubtasks(task);
    return count + subs.filter(st => st.status === "Completed").length;
  }, 0);
  const totalSubtasks = tasks.reduce((count, task) => {
    const subs = getSubtasks(task);
    return count + subs.length;
  }, 0);
  
  // Overdue tasks count
  const overdueTasks = tasks.filter(t => isTaskOverdue(t));
  
  // Project header
  const projectHeader = document.createElement("div");
  projectHeader.className = "timeline-project-header";
  
  const projectInfo = document.createElement("div");
  projectInfo.className = "timeline-project-info";
  
  const projectTitle = document.createElement("h4");
  projectTitle.textContent = `Project ${projectId === "unassigned" ? "Unassigned" : `#${projectId}`}`;
  projectInfo.appendChild(projectTitle);
  
  const projectMeta = document.createElement("div");
  projectMeta.className = "timeline-project-meta";
  projectMeta.innerHTML = `
    <span>${totalTasks} ${totalTasks === 1 ? "task" : "tasks"}</span>
    ${overdueTasks.length > 0 ? `<span class="timeline-overdue-badge">${overdueTasks.length} overdue</span>` : ""}
  `;
  projectInfo.appendChild(projectMeta);
  
  projectHeader.appendChild(projectInfo);
  
  // Progress bar
  const progressContainer = document.createElement("div");
  progressContainer.className = "timeline-progress-container";
  
  if (totalSubtasks > 0) {
    const progressBar = document.createElement("div");
    progressBar.className = "timeline-progress-bar";
    
    const progressFill = document.createElement("div");
    progressFill.className = "timeline-progress-fill";
    const progressPercent = totalSubtasks > 0 ? (completedSubtasks / totalSubtasks) * 100 : 0;
    progressFill.style.width = `${progressPercent}%`;
    
    progressBar.appendChild(progressFill);
    progressContainer.appendChild(progressBar);
    
    const progressText = document.createElement("span");
    progressText.className = "timeline-progress-text";
    progressText.textContent = `${completedSubtasks}/${totalSubtasks}`;
    progressContainer.appendChild(progressText);
  } else {
    const noSubtasksText = document.createElement("span");
    noSubtasksText.className = "muted";
    noSubtasksText.textContent = "No subtasks";
    progressContainer.appendChild(noSubtasksText);
  }
  
  projectHeader.appendChild(progressContainer);
  
  section.appendChild(projectHeader);
  
  // Tasks list
  const tasksList = document.createElement("div");
  tasksList.className = "timeline-tasks-list";
  
  tasks.forEach(task => {
    const taskCard = renderTimelineTaskCard(task, { log, reload });
    tasksList.appendChild(taskCard);
  });
  
  section.appendChild(tasksList);
  
  return section;
}

/**
 * Render a single task card in timeline
 */
function renderTimelineTaskCard(task, { log, reload }) {
  const card = document.createElement("div");
  card.className = "timeline-task-card";
  
  // Add overdue styling
  if (isTaskOverdue(task)) {
    card.classList.add("timeline-task-overdue");
  }
  
  // Task header
  const taskHeader = document.createElement("div");
  taskHeader.className = "timeline-task-header";
  
  const taskTitle = document.createElement("div");
  taskTitle.className = "timeline-task-title";
  taskTitle.innerHTML = `
    <span class="timeline-task-id">#${task.id}</span>
    <span>${escapeHtml(task.title || "")}</span>
  `;
  taskHeader.appendChild(taskTitle);
  
  const taskBadges = document.createElement("div");
  taskBadges.className = "timeline-task-badges";
  
  // Status badge
  if (task.status) {
    const statusBadge = document.createElement("span");
    statusBadge.className = "task-badge status";
    statusBadge.textContent = task.status;
    taskBadges.appendChild(statusBadge);
  }
  
  // Priority badge
  const priority = getPriorityDisplay(task);
  if (priority && priority !== "—") {
    const priorityBadge = document.createElement("span");
    priorityBadge.className = "task-badge priority";
    priorityBadge.textContent = `P${priority}`;
    taskBadges.appendChild(priorityBadge);
  }
  
  taskHeader.appendChild(taskBadges);
  card.appendChild(taskHeader);
  
  // Task meta (assignees, dates)
  const taskMeta = document.createElement("div");
  taskMeta.className = "timeline-task-meta";
  
  // Assignees
  const assignees = getAssignees(task);
  if (assignees && assignees.length > 0) {
    const assigneesEl = document.createElement("div");
    assigneesEl.className = "timeline-task-assignees";
    const assigneeNames = assignees.map(a => a.name || a.full_name || a.email || `user ${a.user_id ?? a.id}`).join(", ");
    assigneesEl.textContent = `Assigned to: ${assigneeNames}`;
    taskMeta.appendChild(assigneesEl);
  }
  
  // Dates
  const datesEl = document.createElement("div");
  datesEl.className = "timeline-task-dates";
  const dateParts = [];
  if (task.start_date) {
    dateParts.push(`Start: ${task.start_date}`);
  }
  if (task.deadline) {
    dateParts.push(`Due: ${task.deadline}`);
  }
  datesEl.textContent = dateParts.join(" | ");
  taskMeta.appendChild(datesEl);
  
  card.appendChild(taskMeta);
  
  // Subtasks
  const subs = getSubtasks(task);
  if (subs && subs.length > 0) {
    const subtasksSection = document.createElement("div");
    subtasksSection.className = "timeline-subtasks";
    subtasksSection.innerHTML = `
      <div class="timeline-subtasks-label">Subtasks (${subs.length})</div>
    `;
    card.appendChild(subtasksSection);
  }
  
  // Click handler to open detail panel
  card.addEventListener("click", () => {
    openCalTaskPanel(task, { log, reload });
  });
  
  return card;
}

