// js/ui/timeline.js
import { parseYMD, escapeHtml, getSubtasks, getAssignees, getPriorityDisplay } from "../state.js";
import { PROJECT_NAMES } from "../main.js";
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
  
  // Show all tasks including completed
  const allTasks = tasks;
  
  if (allTasks.length === 0) {
    timelineEl.innerHTML = `<div class="muted">No tasks to display.</div>`;
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
  
  // Calculate progress based on parent tasks only (completed/all)
  const totalTasks = tasks.length;
  const completedTasks = tasks.filter(t => t.status === "Completed").length;
  
  // Overdue tasks count
  const overdueTasks = tasks.filter(t => isTaskOverdue(t));
  
  // Project header
  const projectHeader = document.createElement("div");
  projectHeader.className = "timeline-project-header";
  
  const projectInfo = document.createElement("div");
  projectInfo.className = "timeline-project-info";
  
  const projectTitle = document.createElement("h4");
  const projectName = projectId === "unassigned" ? "Unassigned" : (PROJECT_NAMES[projectId] || `Project #${projectId}`);
  const displayName = projectId === "unassigned" ? projectName : `Project ${projectId}: ${projectName}`;
  projectTitle.innerHTML = `
    <span>${escapeHtml(displayName)}</span>
    <span class="timeline-project-meta">${totalTasks} ${totalTasks === 1 ? "task" : "tasks"}</span>
    ${overdueTasks.length > 0 ? `<span class="timeline-overdue-badge">${overdueTasks.length} overdue</span>` : ""}
  `;
  projectInfo.appendChild(projectTitle);
  
  projectHeader.appendChild(projectInfo);
  
  // Progress bar
  const progressContainer = document.createElement("div");
  progressContainer.className = "timeline-progress-container";
  
  if (totalTasks > 0) {
    const progressBar = document.createElement("div");
    progressBar.className = "timeline-progress-bar";
    
    const progressFill = document.createElement("div");
    progressFill.className = "timeline-progress-fill";
    const progressPercent = (completedTasks / totalTasks) * 100;
    progressFill.style.width = `${progressPercent}%`;
    
    progressBar.appendChild(progressFill);
    progressContainer.appendChild(progressBar);
    
    const progressText = document.createElement("span");
    progressText.className = "timeline-progress-text";
    progressText.textContent = `${completedTasks}/${totalTasks}`;
    progressContainer.appendChild(progressText);
  } else {
    const noProgressText = document.createElement("span");
    noProgressText.className = "muted";
    noProgressText.textContent = "No tasks";
    progressContainer.appendChild(noProgressText);
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
  
  // Subtasks progress (inline if subtasks exist) - moved to front
  const subs = getSubtasks(task);
  if (subs && subs.length > 0) {
    const completedSubs = subs.filter(st => st.status === "Completed").length;
    const taskProgressContainer = document.createElement("div");
    taskProgressContainer.className = "timeline-task-inline-progress";
    
    const taskProgressBar = document.createElement("div");
    taskProgressBar.className = "timeline-task-inline-progress-bar";
    
    const taskProgressFill = document.createElement("div");
    taskProgressFill.className = "timeline-task-inline-progress-fill";
    const progressPercent = (completedSubs / subs.length) * 100;
    taskProgressFill.style.width = `${progressPercent}%`;
    
    taskProgressBar.appendChild(taskProgressFill);
    taskProgressContainer.appendChild(taskProgressBar);
    
    const taskProgressText = document.createElement("span");
    taskProgressText.className = "timeline-task-inline-progress-text";
    taskProgressText.textContent = `${completedSubs}/${subs.length}`;
    taskProgressContainer.appendChild(taskProgressText);
    
    taskBadges.appendChild(taskProgressContainer);
  }
  
  // Status badge
  if (task.status) {
    const statusBadge = document.createElement("span");
    const statusClass = `task-badge status ${task.status.toLowerCase().replace(' ', '-')}`;
    statusBadge.className = statusClass;
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
  
  // Task description (if available)
  if (task.description) {
    const taskDescription = document.createElement("div");
    taskDescription.className = "timeline-task-description";
    taskDescription.textContent = task.description;
    card.appendChild(taskDescription);
  }
  
  // Task meta (assignees, dates)
  const taskMeta = document.createElement("div");
  taskMeta.className = "timeline-task-meta";
  
  // Assignees with better formatting (limit to prevent overflow)
  const assignees = getAssignees(task);
  if (assignees && assignees.length > 0) {
    const assigneesEl = document.createElement("div");
    assigneesEl.className = "timeline-task-assignees";
    const MAX_VISIBLE = 5;
    const visibleAssignees = assignees.slice(0, MAX_VISIBLE);
    const remainingCount = assignees.length - MAX_VISIBLE;
    
    let assigneeNames = visibleAssignees.map(a => a.name || a.full_name || a.email || `user ${a.user_id ?? a.id}`).join(", ");
    if (remainingCount > 0) {
      assigneeNames += `, +${remainingCount} more`;
      const allNames = assignees.map(a => a.name || a.full_name || a.email || `user ${a.user_id ?? a.id}`).join(", ");
      assigneesEl.title = allNames;
    }
    assigneesEl.innerHTML = `<span class="timeline-meta-label">Assigned:</span> <span>${escapeHtml(assigneeNames)}</span>`;
    taskMeta.appendChild(assigneesEl);
  }
  
  // Dates with better formatting
  const datesEl = document.createElement("div");
  datesEl.className = "timeline-task-dates";
  const dateParts = [];
  if (task.start_date) {
    dateParts.push(`<span class="timeline-meta-label">Start:</span> <span>${task.start_date}</span>`);
  }
  if (task.deadline) {
    dateParts.push(`<span class="timeline-meta-label">Due:</span> <span>${task.deadline}</span>`);
  }
  datesEl.innerHTML = dateParts.join(" | ");
  taskMeta.appendChild(datesEl);
  
  card.appendChild(taskMeta);
  
  // Click handler to open detail panel
  card.addEventListener("click", () => {
    openCalTaskPanel(task, { log, reload });
  });
  
  return card;
}

