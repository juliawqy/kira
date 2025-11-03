// js/ui/team-management.js
import { parseYMD, getSubtasks, getUsers, getAssignees } from "../state.js";
import { apiTask } from "../api.js";
import { renderTaskCard } from "./cards.js";

function isTaskOverdue(task) {
  if (!task.deadline) return false;
  const deadline = parseYMD(task.deadline);
  if (!deadline) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return deadline < today && task.status !== "Completed";
}

function daysUntilDeadline(task) {
  if (!task.deadline) return null;
  const deadline = parseYMD(task.deadline);
  if (!deadline) return null;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return Math.floor((deadline - today) / (1000 * 60 * 60 * 24));
}

/**
 * Main function to render the team management dashboard
 * @param {Object} data - Dictionary of team_number -> list of tasks
 * @param {Object} options - { log, reload }
 * @returns {Promise<HTMLElement>} - Container with all team sections
 */
export async function renderTeamManagement(data, { log, reload } = {}) {
  const container = document.createElement("div");
  container.className = "team-management-container";
  
  if (!data || typeof data !== 'object' || Object.keys(data).length === 0) {
    container.innerHTML = '<div class="muted">No team tasks to display.</div>';
    return container;
  }
  
  // Debug/summary header to ensure something renders
  try {
    const teamKeys = Object.keys(data || {});
    const summary = document.createElement("div");
    summary.className = "muted";
    summary.style.marginBottom = "8px";
    summary.textContent = `Teams loaded: ${teamKeys.length} (${teamKeys.join(", ")})`;
    container.appendChild(summary);
    if (typeof log === "function") log("TeamManagement keys", teamKeys);
  } catch {}
  
  // Render each team's section
  for (const [teamNumber, tasks] of Object.entries(data)) {
    try {
      if (Array.isArray(tasks) && tasks.length > 0) {
        const teamSection = await renderTeamSection(teamNumber, tasks, { log, reload });
        container.appendChild(teamSection);
      }
    } catch (e) {
      if (typeof log === "function") log("renderTeamSection error", String(e));
    }
  }
  
  if (container.children.length === 0) {
    container.innerHTML = '<div class="muted">No tasks found for any team.</div>';
  }
  
  return container;
}

/**
 * Render a single team section with all metrics and tasks
 */
async function renderTeamSection(teamNumber, tasks, { log, reload }) {
  const section = document.createElement("div");
  section.className = "team-section";
  
  // Fetch assignees for metrics calculation
  const tasksNeedingAssignees = tasks.filter(t => !getAssignees(t) || getAssignees(t).length === 0);
  if (tasksNeedingAssignees.length > 0) {
    try {
      await Promise.all(
        tasksNeedingAssignees.map(async (t) => {
          try {
            const list = await apiTask(`/${t.id}/assignees`, { method: "GET" });
            if (Array.isArray(list)) {
              t.assignees = list;
            }
          } catch (e) {
            if (typeof log === "function") log("load assignees for metrics error", String(e));
          }
        })
      );
    } catch {}
  }
  
  const metrics = calculateTeamMetrics(tasks);
  
  // Team header with title and key stats
  const header = document.createElement("div");
  header.className = "team-header";
  
  const titleRow = document.createElement("div");
  titleRow.className = "team-title-row";
  
  const teamTitle = document.createElement("div");
  teamTitle.className = "team-title";
  teamTitle.innerHTML = `<h3>Team ${teamNumber}</h3>`;
  
  const teamStats = document.createElement("div");
  teamStats.className = "team-stats";
  
  // Members count
  const memberStat = document.createElement("div");
  memberStat.className = "team-stat-group";
  memberStat.innerHTML = `
    <div class="team-stat">
      <span class="team-stat-label">Members:</span>
      <span class="team-stat-value">${metrics.memberCount}</span>
    </div>
  `;
  teamStats.appendChild(memberStat);
  
  // Task count
  const taskStat = document.createElement("div");
  taskStat.className = "team-stat-group";
  taskStat.innerHTML = `
    <div class="team-stat">
      <span class="team-stat-label">Tasks:</span>
      <span class="team-stat-value">${metrics.total}</span>
    </div>
  `;
  teamStats.appendChild(taskStat);
  
  // Progress bar
  const progressGroup = document.createElement("div");
  progressGroup.className = "team-stat-group";
  if (metrics.total > 0) {
    const progressContainer = document.createElement("div");
    progressContainer.className = "team-progress-container";
    
    const progressBar = document.createElement("div");
    progressBar.className = "team-progress-bar";
    
    const progressFill = document.createElement("div");
    progressFill.className = "team-progress-fill";
    progressFill.style.width = `${metrics.completionRate}%`;
    progressBar.appendChild(progressFill);
    progressContainer.appendChild(progressBar);
    
    const progressText = document.createElement("span");
    progressText.className = "team-progress-text";
    progressText.textContent = `${metrics.completionRate.toFixed(0)}%`;
    progressContainer.appendChild(progressText);
    
    progressGroup.appendChild(progressContainer);
  } else {
    const noProgress = document.createElement("span");
    noProgress.className = "muted";
    noProgress.textContent = "No tasks";
    progressGroup.appendChild(noProgress);
  }
  
  teamStats.appendChild(progressGroup);
  
  titleRow.appendChild(teamTitle);
  titleRow.appendChild(teamStats);
  header.appendChild(titleRow);
  
  // Warning indicators
  if (metrics.overdue > 0 || metrics.highPriority > 0 || metrics.urgent > 0) {
    const warningRow = document.createElement("div");
    warningRow.className = "team-warnings";
    
    if (metrics.overdue > 0) {
      const overdueBadge = document.createElement("span");
      overdueBadge.className = "warning-badge warning-overdue";
      overdueBadge.innerHTML = `⚠️ ${metrics.overdue} overdue`;
      warningRow.appendChild(overdueBadge);
    }
    
    if (metrics.highPriority > 0) {
      const highPriorityBadge = document.createElement("span");
      highPriorityBadge.className = "warning-badge warning-high-priority";
      highPriorityBadge.innerHTML = `🔴 ${metrics.highPriority} high priority`;
      warningRow.appendChild(highPriorityBadge);
    }
    
    if (metrics.urgent > 0) {
      const urgentBadge = document.createElement("span");
      urgentBadge.className = "warning-badge warning-urgent";
      urgentBadge.innerHTML = `⏰ ${metrics.urgent} due soon (0-7 days)`;
      warningRow.appendChild(urgentBadge);
    }
    
    header.appendChild(warningRow);
  }
  
  // Status breakdown
  const statusRow = document.createElement("div");
  statusRow.className = "team-status-breakdown";
  
  const breakdownTitle = document.createElement("span");
  breakdownTitle.className = "breakdown-title";
  breakdownTitle.textContent = "Status:";
  statusRow.appendChild(breakdownTitle);
  
  // Status bars
  const statusBarContainer = document.createElement("div");
  statusBarContainer.className = "status-bar-container";
  
  const statuses = [
    { name: "Completed", count: metrics.statusCounts.completed, color: "var(--accent-2)" },
    { name: "In-progress", count: metrics.statusCounts.inprogress, color: "#3b82f6" },
    { name: "To-do", count: metrics.statusCounts.todo, color: "#94a3b8" },
    { name: "Blocked", count: metrics.statusCounts.blocked, color: "var(--warn)" }
  ];
  
  statuses.forEach(status => {
    if (status.count === 0) return;
    
    const percentage = (status.count / metrics.total) * 100;
    const statusBar = document.createElement("div");
    statusBar.className = "status-bar";
    statusBar.innerHTML = `
      <div class="status-bar-fill" style="width: ${percentage}%; background: ${status.color};"></div>
      <span class="status-bar-label">${status.name}: ${status.count}</span>
    `;
    statusBarContainer.appendChild(statusBar);
  });
  
  statusRow.appendChild(statusBarContainer);
  header.appendChild(statusRow);
  
  // Additional metrics row
  const metricsRow = document.createElement("div");
  metricsRow.className = "team-details-row";
  
  // Priority distribution
  const prioritySection = document.createElement("div");
  prioritySection.className = "team-metric-section";
  prioritySection.innerHTML = `
    <div class="metric-label">Priority:</div>
    <div class="metric-values">
      <span class="metric-badge priority-high">🔴 High: ${metrics.highPriority}</span>
      <span class="metric-badge priority-medium">🟡 Med: ${metrics.mediumPriority}</span>
      <span class="metric-badge priority-low">🟢 Low: ${metrics.lowPriority}</span>
    </div>
  `;
  metricsRow.appendChild(prioritySection);
  
  // Deadline distribution
  const deadlineSection = document.createElement("div");
  deadlineSection.className = "team-metric-section";
  deadlineSection.innerHTML = `
    <div class="metric-label">Due:</div>
    <div class="metric-values">
      ${metrics.due03Days > 0 ? `<span class="metric-badge deadline-urgent">⚡ 0-3 days: ${metrics.due03Days}</span>` : ''}
      ${metrics.due47Days > 0 ? `<span class="metric-badge deadline-soon">⏰ 4-7 days: ${metrics.due47Days}</span>` : ''}
      ${metrics.due7PlusDays > 0 ? `<span class="metric-badge deadline-far">📅 7+ days: ${metrics.due7PlusDays}</span>` : ''}
      ${metrics.due03Days === 0 && metrics.due47Days === 0 && metrics.due7PlusDays === 0 ? '<span class="muted">No deadlines</span>' : ''}
    </div>
  `;
  metricsRow.appendChild(deadlineSection);
  
  // Task load per member
  if (metrics.memberCount > 0) {
    const loadSection = document.createElement("div");
    loadSection.className = "team-metric-section";
    loadSection.innerHTML = `
      <div class="metric-label">Workload:</div>
      <div class="metric-values">
        <span class="metric-badge">Avg: ${metrics.avgTasksPerMember} tasks/member</span>
        ${metrics.maxTasks > 0 ? `<span class="metric-badge workload-heavy">Most: ${metrics.maxTasks} tasks</span>` : ''}
        ${metrics.minTasks < 999 ? `<span class="metric-badge workload-light">Least: ${metrics.minTasks} tasks</span>` : ''}
      </div>
    `;
    metricsRow.appendChild(loadSection);
  }
  
  header.appendChild(metricsRow);
  section.appendChild(header);
  
  // Task cards grouped by project
  const tasksByProject = {};
  tasks.forEach(task => {
    const projectId = task.project_id || "unassigned";
    if (!tasksByProject[projectId]) {
      tasksByProject[projectId] = [];
    }
    tasksByProject[projectId].push(task);
  });
  
  const tasksContainer = document.createElement("div");
  tasksContainer.className = "team-tasks-container";
  
  Object.entries(tasksByProject).forEach(([projectId, projectTasks]) => {
    // Project label
    const projectLabel = document.createElement("div");
    projectLabel.className = "team-project-label";
    const projectNames = new Set(projectTasks.map(t => t.project?.name || `Project ${projectId}`));
    projectLabel.textContent = Array.from(projectNames).join(", ");
    tasksContainer.appendChild(projectLabel);
    
    // Task cards for this project
    projectTasks.forEach(task => {
      try {
        const taskCard = renderTaskCard(task, { log, reload });
        tasksContainer.appendChild(taskCard);
      } catch (e) {
        if (typeof log === "function") log("renderTaskCard error", String(e));
      }
    });
  });
  
  // Grouping controls
  const controls = document.createElement("div");
  controls.style.display = "flex";
  controls.style.gap = "8px";
  controls.style.alignItems = "center";
  controls.style.margin = "8px 0";
  const label = document.createElement("span");
  label.className = "muted";
  label.textContent = "Group by:";
  const btnProject = document.createElement("button");
  btnProject.className = "btn";
  btnProject.textContent = "Project";
  const btnMember = document.createElement("button");
  btnMember.className = "btn";
  btnMember.textContent = "Member";
  controls.appendChild(label);
  controls.appendChild(btnProject);
  controls.appendChild(btnMember);

  section.appendChild(controls);

  const renderByProject = () => {
    tasksContainer.innerHTML = "";
    const tasksByProject = {};
    tasks.forEach(task => {
      const projectId = task.project_id || "unassigned";
      if (!tasksByProject[projectId]) tasksByProject[projectId] = [];
      tasksByProject[projectId].push(task);
    });
    Object.entries(tasksByProject).forEach(([projectId, projectTasks]) => {
      const projectLabel = document.createElement("div");
      projectLabel.className = "team-project-label";
      const projectNames = new Set(projectTasks.map(t => t.project?.name || `Project ${projectId}`));
      projectLabel.textContent = Array.from(projectNames).join(", ");
      tasksContainer.appendChild(projectLabel);
      projectTasks.forEach(task => {
        try {
          const taskCard = renderTaskCard(task, { log, reload });
          tasksContainer.appendChild(taskCard);
        } catch (e) { if (typeof log === "function") log("renderTaskCard error", String(e)); }
      });
    });
  };

  const renderByMember = async () => {
    tasksContainer.innerHTML = "";
    const loading = document.createElement("div");
    loading.className = "muted";
    loading.textContent = "Loading assignees…";
    tasksContainer.appendChild(loading);

    // Fetch assignees for tasks missing them
    const tasksNeedingAssignees = tasks.filter(t => !getAssignees(t) || getAssignees(t).length === 0);
    if (tasksNeedingAssignees.length) {
      try {
        await Promise.all(
          tasksNeedingAssignees.map(async (t) => {
            try {
              const list = await apiTask(`/${t.id}/assignees`, { method: "GET" });
              if (Array.isArray(list)) {
                // attach to task so subsequent renders have it
                t.assignees = list;
              }
            } catch (e) {
              if (typeof log === "function") log("load assignees error", String(e));
            }
          })
        );
      } catch {}
    }

    // Build groups
    const byMember = {};
    const unassigned = [];
    tasks.forEach(task => {
      const assignees = getAssignees(task);
      if (!assignees || assignees.length === 0) {
        unassigned.push(task);
        return;
      }
      assignees.forEach(a => {
        const key = a.name || a.full_name || a.email || `User ${a.user_id ?? a.id}`;
        if (!byMember[key]) byMember[key] = [];
        byMember[key].push(task);
      });
    });

    // Render
    tasksContainer.innerHTML = "";
    Object.entries(byMember).forEach(([memberName, memberTasks]) => {
      const memberLabel = document.createElement("div");
      memberLabel.className = "team-project-label";
      memberLabel.textContent = memberName;
      tasksContainer.appendChild(memberLabel);
      memberTasks.forEach(task => {
        try {
          const taskCard = renderTaskCard(task, { log, reload });
          tasksContainer.appendChild(taskCard);
        } catch (e) { if (typeof log === "function") log("renderTaskCard error", String(e)); }
      });
    });
    if (unassigned.length) {
      const unl = document.createElement("div");
      unl.className = "team-project-label";
      unl.textContent = "Unassigned";
      tasksContainer.appendChild(unl);
      unassigned.forEach(task => {
        try {
          const taskCard = renderTaskCard(task, { log, reload });
          tasksContainer.appendChild(taskCard);
        } catch (e) { if (typeof log === "function") log("renderTaskCard error", String(e)); }
      });
    }
  };

  // Default view
  renderByProject();

  btnProject.addEventListener("click", renderByProject);
  btnMember.addEventListener("click", () => { void renderByMember(); });

  section.appendChild(tasksContainer);
  
  return section;
}

/**
 * Calculate team-level metrics
 */
function calculateTeamMetrics(tasks) {
  const total = tasks.length;
  const completed = tasks.filter(t => t.status === "Completed").length;
  const overdue = tasks.filter(t => isTaskOverdue(t)).length;
  
  // Priority distribution
  const highPriority = tasks.filter(t => t.priority >= 8).length;
  const mediumPriority = tasks.filter(t => t.priority >= 5 && t.priority <= 7).length;
  const lowPriority = tasks.filter(t => t.priority >= 1 && t.priority <= 4).length;
  
  // Time to deadline breakdown
  const due03Days = tasks.filter(t => {
    const days = daysUntilDeadline(t);
    return days !== null && days >= 0 && days <= 3 && t.status !== "Completed";
  }).length;
  const due47Days = tasks.filter(t => {
    const days = daysUntilDeadline(t);
    return days !== null && days >= 4 && days <= 7 && t.status !== "Completed";
  }).length;
  const due7PlusDays = tasks.filter(t => {
    const days = daysUntilDeadline(t);
    return days !== null && days > 7 && t.status !== "Completed";
  }).length;
  
  // Urgent (0-7 days combined)
  const urgent = due03Days + due47Days;
  
  // Status breakdown
  const statusCounts = {
    completed: tasks.filter(t => t.status === "Completed").length,
    inprogress: tasks.filter(t => t.status === "In-progress").length,
    todo: tasks.filter(t => t.status === "To-do").length,
    blocked: tasks.filter(t => t.status === "Blocked").length
  };
  
  // Task load per member
  const memberTasks = {}; // user_id -> count
  tasks.forEach(task => {
    if (task.assignees && Array.isArray(task.assignees)) {
      task.assignees.forEach(a => {
        const userId = a.user_id || a.id;
        memberTasks[userId] = (memberTasks[userId] || 0) + 1;
      });
    }
  });
  
  const uniqueMembers = Object.keys(memberTasks);
  const memberCount = uniqueMembers.length;
  const avgTasksPerMember = memberCount > 0 ? (total / memberCount).toFixed(1) : 0;
  
  const memberTaskCounts = Object.values(memberTasks);
  const maxTasks = Math.max(...memberTaskCounts, 0);
  const minTasks = Math.min(...memberTaskCounts, 999);
  
  const completionRate = total > 0 ? (completed / total) * 100 : 0;
  const overdueRate = total > 0 ? (overdue / total) * 100 : 0;
  
  return {
    total,
    completed,
    overdue,
    highPriority,
    mediumPriority,
    lowPriority,
    due03Days,
    due47Days,
    due7PlusDays,
    urgent,
    statusCounts,
    memberCount,
    memberTasks,
    avgTasksPerMember,
    maxTasks,
    minTasks,
    completionRate,
    overdueRate
  };
}

