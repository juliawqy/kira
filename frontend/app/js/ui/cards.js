// js/ui/cards.js
import { apiTask } from "../api.js";
import { USERS, getSubtasks, getAssignees, getPriorityDisplay, escapeHtml, getUsers, isCurrentUserStaff, isCurrentUserManager, isCurrentUserDirector, isCurrentUserManagerOrDirector, CURRENT_USER, LAST_TASKS, parseYMD, showToast } from "../state.js";
import { field } from "./dom.js";

/* ----------------------------- panel state ----------------------------- */
let panelNestLevel = 0;

/* ----------------------------- safe log ----------------------------- */
function asLog(log) {
  return typeof log === "function" ? log : (...args) => console.log(...args);
}

/* ----------------------------- overdue check ----------------------------- */
function isTaskOverdue(task) {
  if (!task.deadline) return false;
  const deadline = parseYMD(task.deadline);
  if (!deadline) return false;
  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return deadline < today && task.status !== "Completed";
}

/**
 * Public entry: render all parent tasks into a container.
 * @param {HTMLElement} container
 * @param {Array<object>} tasks
 * @param {{log?: Function, reload: Function}} ctx
 */
export function renderParents(container, tasks, { log, reload }) {
  container.innerHTML = "";
  if (!Array.isArray(tasks) || tasks.length === 0) {
    container.innerHTML = `<div class="muted">No data. Click "Refresh".</div>`;
    return;
  }
  for (const t of tasks) {
    container.appendChild(renderTaskCard(t, { log, reload }));
  }
}

/* ----------------------------- helpers ----------------------------- */

function btn(label, cls, onClick) {
  const b = document.createElement("button");
  b.className = cls + " small";
  b.textContent = label;
  b.type = "button";
  b.addEventListener("click", (e) => {
    e.preventDefault();
    onClick && onClick();
  });
  return b;
}

async function setStatus(id, action, log, reload, callback) {
  const slog = asLog(log);
  const map = { start: "In-progress", block: "Blocked", complete: "Completed" };
  const newStatus = map[action] || "To-do";
  try {
    const res = await apiTask(`/${id}/status/${encodeURIComponent(newStatus)}`, { method: "POST" });
    slog(`POST /task/${id}/status/${newStatus}`, res);
    showToast(`Status updated to ${newStatus}`, "success");
    if (callback) {
      callback(newStatus);
    } else {
    reload();
    }
  } catch (e) {
    slog("Status error", String(e));
    showToast(e.message || "Failed to update status", "error");
  }
}

async function deleteTask(id, log, reload, callback) {
  const slog = asLog(log);
  try {
    const res = await apiTask(`/${id}/delete`, { method: "POST" });
    slog(`POST /task/${id}/delete`, res);
    showToast("Task deleted successfully", "success");
    if (callback) {
      callback();
    } else {
    reload();
    }
  } catch (e) {
    slog("Delete error", String(e));
    showToast(e.message || "Failed to delete task", "error");
  }
}

async function loadAssigneesForTask(taskId, log) {
  const slog = asLog(log);
  try {
    return await apiTask(`/${taskId}/assignees`, { method: "GET" });
  } catch (e) {
    slog("GET assignees error", String(e));
    return [];
  }
}

/* ----------------------------- cards ----------------------------- */

// Exported so main.js can import by name.
export function renderTaskCard(task, { log, reload }) {
  const slog = asLog(log);

  const el = document.createElement("div");
  el.className = "task";
  el.dataset.id = task.id;

  // Add overdue styling for all users
  if (isTaskOverdue(task)) {
    el.classList.add("task-overdue");
  }

  // Compact header
  const header = document.createElement("div");
  header.className = "task-header";

  const taskId = document.createElement("div");
  taskId.className = "task-id";
  taskId.textContent = `#${task.id}`;
  header.appendChild(taskId);

  const taskTitle = document.createElement("div");
  taskTitle.className = "task-title";
  taskTitle.textContent = task.title || "";
  header.appendChild(taskTitle);

  const meta = document.createElement("div");
  meta.className = "task-meta";

  // Status badge
  if (task.status) {
    const statusBadge = document.createElement("span");
    const statusClass = `task-badge status ${task.status.toLowerCase().replace(' ', '-')}`;
    statusBadge.className = statusClass;
    statusBadge.textContent = task.status;
    meta.appendChild(statusBadge);
  }

  // Priority badge
  const priority = getPriorityDisplay(task);
  if (priority && priority !== "—") {
    const priorityBadge = document.createElement("span");
    priorityBadge.className = "task-badge priority";
    priorityBadge.textContent = `P${priority}`;
    meta.appendChild(priorityBadge);
  }

  header.appendChild(meta);

  // Expander icon
  const expander = document.createElement("div");
  expander.className = "task-expander";
  expander.textContent = "▼";
  header.appendChild(expander);

  el.appendChild(header);

  // Expanded details section
  const details = document.createElement("div");
  details.className = "task-details";

  // Description
  if (task.description) {
  const descBox = document.createElement("div");
    descBox.className = "task-description";
    descBox.textContent = task.description;
    details.appendChild(descBox);
  }

  // Metadata section
  const metadataSection = document.createElement("div");
  metadataSection.className = "task-section";
  
  const metadataLabel = document.createElement("div");
  metadataLabel.className = "task-section-label";
  metadataLabel.textContent = "Details";
  metadataSection.appendChild(metadataLabel);

  const metadata = document.createElement("div");
  metadata.className = "task-details-grid";
  
  const fields = [];
  
  if (task.start_date) {
    fields.push(field("Start Date", task.start_date));
  }
  if (task.deadline) {
    fields.push(field("Deadline", task.deadline));
  }
  if (task.project_id != null) {
    fields.push(field("Project", `#${task.project_id}`));
  }
  if (task.tag) {
    fields.push(field("Tag", task.tag));
  }
  if (task.recurring && task.recurring > 0) {
    fields.push(field("Recurring", `Every ${task.recurring} days`));
  }
  
  // Add fields with separators
  fields.forEach((fieldEl, index) => {
    metadata.appendChild(fieldEl);
    if (index < fields.length - 1) {
      const separator = document.createElement("span");
      separator.textContent = "|";
      separator.style.color = "var(--sub)";
      separator.style.margin = "0 4px";
      metadata.appendChild(separator);
    }
  });
  
  metadataSection.appendChild(metadata);
  details.appendChild(metadataSection);

  // Actions section
  const actionsSection = document.createElement("div");
  actionsSection.className = "task-section";
  
  const actionsLabel = document.createElement("div");
  actionsLabel.className = "task-section-label";
  actionsLabel.textContent = "Actions";
  actionsSection.appendChild(actionsLabel);

  const actionRow = document.createElement("div");
  actionRow.className = "action-buttons";
  
  // Find status badge in header for local updates
  const statusBadge = header.querySelector(".task-badge.status");
  
  actionRow.appendChild(btn("Start", "btn", () => setStatus(task.id, "start", slog, reload, (newStatus) => {
    if (statusBadge) statusBadge.textContent = newStatus;
    el.classList.toggle("expanded");
    // Always reload for status changes to ensure data consistency
    reload();
  })));
  actionRow.appendChild(btn("Block", "btn warn", () => setStatus(task.id, "block", slog, reload, (newStatus) => {
    if (statusBadge) statusBadge.textContent = newStatus;
    el.classList.toggle("expanded");
    // Always reload for status changes to ensure data consistency
    reload();
  })));
  actionRow.appendChild(btn("Complete", "btn success", () => setStatus(task.id, "complete", slog, reload, (newStatus) => {
    if (statusBadge) statusBadge.textContent = newStatus;
    el.classList.toggle("expanded");
    // Always reload after completion (especially for recurring tasks to show new occurrence)
    reload();
  })));
  actionRow.appendChild(btn("Delete", "btn danger", () => deleteTask(task.id, slog, reload, () => {
    el.remove(); // Remove task card from view
  })));
  actionRow.appendChild(btn("Edit", "btn primary", () => {
    document.dispatchEvent(new CustomEvent("open-edit", { detail: task }));
  }));
  
  // Always show actions (including for completed tasks)
  actionsSection.appendChild(actionRow);
  details.appendChild(actionsSection);
  
  // Assignee controls: only for non-completed tasks and non-staff users
  if (task.status !== "Completed" && !isCurrentUserStaff()) {
    details.appendChild(renderAssigneeControls(task, { log, reload }));
  } else {
    // For completed tasks or staff users, show read-only assignees
    details.appendChild(renderAssigneeDisplay(task, { log }));
  }

  // Comments section (always show for all tasks)
  details.appendChild(renderCommentsSection(task, { log, reload }));

  // Subtasks section
  const subs = getSubtasks(task);
  if (Array.isArray(subs) && subs.length > 0) {
    const subtasksSection = document.createElement("div");
    subtasksSection.className = "task-section expanded";
    
    const subtasksHeader = document.createElement("div");
    subtasksHeader.className = "subtasks-header";
    
    const subtasksLabel = document.createElement("div");
    subtasksLabel.className = "task-section-label";
    subtasksLabel.textContent = `Subtasks (${subs.length})`;
    subtasksHeader.appendChild(subtasksLabel);
    
    const expander = document.createElement("div");
    expander.className = "subtask-expander";
    expander.textContent = "▼";
    subtasksHeader.appendChild(expander);
    
    subtasksSection.appendChild(subtasksHeader);

    const subtasksList = document.createElement("div");
    subtasksList.className = "subtasks";
    subs.forEach(st => subtasksList.appendChild(renderSubtaskRow(task.id, st, { log, reload })));
    subtasksSection.appendChild(subtasksList);
    
    // Toggle expansion
    subtasksHeader.addEventListener("click", () => {
      subtasksSection.classList.toggle("expanded");
    });
    
    details.appendChild(subtasksSection);
  }

  el.appendChild(details);

  // Click handler to toggle expansion
  header.addEventListener("click", (e) => {
    // Don't toggle if clicking on a badge or button inside
    if (e.target.classList.contains("task-badge") || e.target.closest("button")) {
      return;
    }
    el.classList.toggle("expanded");
  });

  return el;
}

/* ------------------------- assignee controls ------------------------- */

function renderAssigneeControls(task, { log, reload }) {
  const slog = asLog(log);

  const assWrap = document.createElement("div");
  assWrap.className = "task-section";

  // Section label with assignee count and chips
  const sectionLabel = document.createElement("div");
  sectionLabel.className = "task-section-label";
  const labelText = document.createElement("span");
  labelText.textContent = "Assignees";
  sectionLabel.appendChild(labelText);
  
  const countEl = document.createElement("span");
  countEl.className = "assignee-count";
  countEl.id = `assignee-count-${task.id}`;
  sectionLabel.appendChild(countEl);
  
  const chipsContainer = document.createElement("span");
  chipsContainer.className = "assignee-chips-inline";
  chipsContainer.id = `assignee-chips-${task.id}`;
  sectionLabel.appendChild(chipsContainer);
  
  // Create inline add button
  const addBtn = document.createElement("button");
  addBtn.className = "assignee-add-btn";
  addBtn.innerHTML = "+";
  addBtn.setAttribute("aria-label", "Add assignee");
  sectionLabel.appendChild(addBtn);
  
  assWrap.appendChild(sectionLabel);

  // Hidden add assignee controls
  const addRow = document.createElement("div");
  addRow.className = "assignee-controls-hidden";
  addRow.id = `assignee-controls-${task.id}`;
  addRow.style.display = "none";

  const assSelect = document.createElement("select");
  assSelect.style.minWidth = "220px";
  const placeholder = document.createElement("option");
  placeholder.value = "";
  placeholder.disabled = true;
  placeholder.selected = true;
  placeholder.textContent = "Select a user…";
  assSelect.appendChild(placeholder);
  USERS.forEach(u => {
    const opt = document.createElement("option");
    opt.value = String(u.user_id ?? u.id);
    opt.textContent = u.name || u.full_name || u.email || `user ${opt.value}`;
    assSelect.appendChild(opt);
  });

  addRow.appendChild(assSelect);
  addRow.appendChild(btn("Assign", "btn primary", async () => {
    const val = assSelect.value;
    if (!val) return;
    try {
      const body = JSON.stringify({ user_ids: [Number(val)] });
      const res = await apiTask(`/${task.id}/assignees`, { method: "POST", body });
      slog(`POST /task/${task.id}/assignees`, res);
      assSelect.value = ""; // reset
      addRow.style.display = "none"; // hide controls
      // Reload just the assignees
      const updatedAssignees = await loadAssigneesForTask(task.id, slog);
      renderAssignees(updatedAssignees || []);
      showToast("User assigned successfully", "success");
    } catch (e) { slog("Assign error", String(e)); showToast(e.message || "Failed to assign user", "error"); }
  }));

  // Add cancel button
  addRow.appendChild(btn("Cancel", "btn", () => {
    assSelect.value = "";
    addRow.style.display = "none";
  }));

  // Toggle add button
  addBtn.addEventListener("click", (e) => {
    e.preventDefault();
    e.stopPropagation();
    addRow.style.display = addRow.style.display === "none" ? "flex" : "none";
  });

  assWrap.appendChild(addRow);

  const current = document.createElement("div");
  current.className = "flex";
  current.style.flexWrap = "wrap";
  current.style.gap = "6px";

  const renderAssignees = (list) => {
    // Clear both containers
    current.innerHTML = "";
    chipsContainer.innerHTML = "";
    
    // Update the count in the label
    if (!list || list.length === 0) {
      countEl.textContent = "";
    } else {
      countEl.textContent = ` (${list.length}):`;
    }
    
    if (!list || list.length === 0) {
      const none = document.createElement("span");
      none.className = "assignee-empty";
      none.textContent = "No assignees";
      chipsContainer.appendChild(none);
      return;
    }
    
    // Render chips inline with the label
    list.forEach(a => {
      const chip = document.createElement("span");
      chip.className = "assignee-chip";
      chip.textContent = a.name || a.full_name || a.email || `user ${a.user_id ?? a.id}`;

      const remove = document.createElement("button");
      remove.className = "assignee-remove";
      remove.innerHTML = "×";
      remove.setAttribute("aria-label", "Remove assignee");
      remove.addEventListener("click", async (e) => {
        e.preventDefault();
        e.stopPropagation();
        try {
          const body = JSON.stringify({ user_ids: [Number(a.user_id ?? a.id)] });
          await apiTask(`/${task.id}/assignees`, { method: "DELETE", body });
          slog(`DELETE /task/${task.id}/assignees`, body);
          // Reload just the assignees
          const updatedAssignees = await loadAssigneesForTask(task.id, slog);
          renderAssignees(updatedAssignees || []);
          showToast("User unassigned successfully", "success");
        } catch (err) { slog("Unassign error", String(err)); showToast(err.message || "Failed to unassign user", "error"); }
      });

      chip.appendChild(remove);
      
      // Add to inline container
      chipsContainer.appendChild(chip);
    });
  };

  const assignees = getAssignees(task);
  if (assignees && assignees.length) {
    renderAssignees(assignees);
  } else {
    loadAssigneesForTask(task.id, slog).then(list => renderAssignees(list || []));
  }

  assWrap.appendChild(current);
  return assWrap;
}

/* ------------------------- read-only assignee display ------------------------- */

function renderAssigneeDisplay(task, { log }) {
  const slog = asLog(log);

  const assWrap = document.createElement("div");
  assWrap.className = "task-section";

  // Section label with assignee count
  const sectionLabel = document.createElement("div");
  sectionLabel.className = "task-section-label";
  const labelText = document.createElement("span");
  labelText.textContent = "Assignees";
  sectionLabel.appendChild(labelText);
  
  const countEl = document.createElement("span");
  countEl.className = "assignee-count";
  countEl.id = `assignee-count-${task.id}`;
  sectionLabel.appendChild(countEl);
  
  const chipsContainer = document.createElement("span");
  chipsContainer.className = "assignee-chips-inline";
  chipsContainer.id = `assignee-chips-${task.id}`;
  sectionLabel.appendChild(chipsContainer);
  
  assWrap.appendChild(sectionLabel);

  const renderAssignees = (list) => {
    chipsContainer.innerHTML = "";
    
    // Update the count in the label
    if (countEl) {
      if (!list || list.length === 0) {
        countEl.textContent = "";
      } else {
        countEl.textContent = ` (${list.length})`;
      }
    }
    
    if (!list || list.length === 0) {
      const none = document.createElement("span");
      none.className = "assignee-empty";
      none.textContent = "No assignees";
      chipsContainer.appendChild(none);
      return;
    }
    
    // Render chips inline with the label (read-only, no remove buttons)
    list.forEach(a => {
      const chip = document.createElement("span");
      chip.className = "assignee-chip";
      chip.textContent = a.name || a.full_name || a.email || `user ${a.user_id ?? a.id}`;
      chipsContainer.appendChild(chip);
    });
  };

  const assignees = getAssignees(task);
  if (assignees && assignees.length) {
    renderAssignees(assignees);
  } else {
    loadAssigneesForTask(task.id, slog).then(list => renderAssignees(list || []));
  }

  return assWrap;
}

/* --------------------------- subtask rows --------------------------- */

function renderSubtaskRow(parentId, st, { log, reload }) {
  const slog = asLog(log);

  const row = document.createElement("div");
  row.className = "subtask-row";

  // Add overdue styling for staff members
  if (isCurrentUserStaff() && isTaskOverdue(st)) {
    row.classList.add("subtask-overdue");
  }

  // Compact header (matching parent task structure)
  const header = document.createElement("div");
  header.className = "subtask-header";

  const taskId = document.createElement("div");
  taskId.className = "subtask-id";
  taskId.textContent = `#${st.id}`;
  header.appendChild(taskId);

  const taskTitle = document.createElement("div");
  taskTitle.className = "subtask-title";
  taskTitle.textContent = st.title || "";
  header.appendChild(taskTitle);

  const meta = document.createElement("div");
  meta.className = "subtask-meta";

  // Status badge
  if (st.status) {
    const statusBadge = document.createElement("span");
    statusBadge.className = "subtask-badge status";
    statusBadge.textContent = st.status;
    meta.appendChild(statusBadge);
  }

  // Priority badge
  const priority = getPriorityDisplay(st);
  if (priority && priority !== "—") {
    const priorityBadge = document.createElement("span");
    priorityBadge.className = "subtask-badge priority";
    priorityBadge.textContent = `P${priority}`;
    meta.appendChild(priorityBadge);
  }

  header.appendChild(meta);
  
  row.appendChild(header);

  // Create content for right-side panel
  const panelInner = document.createElement("div");
  
  const panelHeader = document.createElement("div");
  panelHeader.className = "subtask-panel-header";
  panelHeader.innerHTML = `<h3>#${st.id} - ${escapeHtml(st.title || "")}</h3>`;
  
  const closeBtn = document.createElement("button");
  closeBtn.className = "subtask-panel-close";
  closeBtn.innerHTML = "×";
  closeBtn.addEventListener("click", () => closeSubtaskPanel());
  panelHeader.appendChild(closeBtn);
  
  panelInner.appendChild(panelHeader);
  
  const details = document.createElement("div");
  details.className = "subtask-details";

  // Description
  if (st.description) {
    const descBox = document.createElement("div");
    descBox.className = "task-description";
    descBox.textContent = st.description;
    details.appendChild(descBox);
  }

  // Metadata section
  const metadataSection = document.createElement("div");
  metadataSection.className = "task-section";
  
  const metadataLabel = document.createElement("div");
  metadataLabel.className = "task-section-label";
  metadataLabel.textContent = "Details";
  metadataSection.appendChild(metadataLabel);

  const metadata = document.createElement("div");
  metadata.className = "task-details-grid";
  
  const fields = [];
  
  // Parent task
  if (parentId) {
    const parentTask = LAST_TASKS.find(t => t.id === parentId);
    if (parentTask) {
      fields.push(field("Parent Task", `#${parentId} - ${parentTask.title}`));
    } else {
      fields.push(field("Parent Task", `#${parentId}`));
    }
  }
  
  if (st.start_date) {
    fields.push(field("Start Date", st.start_date));
  }
  if (st.deadline) {
    fields.push(field("Deadline", st.deadline));
  }
  if (st.project_id != null) {
    fields.push(field("Project", `#${st.project_id}`));
  }
  if (st.tag) {
    fields.push(field("Tag", st.tag));
  }
  if (st.recurring && st.recurring > 0) {
    fields.push(field("Recurring", `Every ${st.recurring} days`));
  }
  
  // Add fields with separators
  fields.forEach((fieldEl, index) => {
    metadata.appendChild(fieldEl);
    if (index < fields.length - 1) {
      const separator = document.createElement("span");
      separator.textContent = "|";
      separator.style.color = "var(--sub)";
      separator.style.margin = "0 4px";
      metadata.appendChild(separator);
    }
  });
  
  metadataSection.appendChild(metadata);
  details.appendChild(metadataSection);

  // Actions section
  const actionsSection = document.createElement("div");
  actionsSection.className = "task-section";
  
  const actionsLabel = document.createElement("div");
  actionsLabel.className = "task-section-label";
  actionsLabel.textContent = "Actions";
  actionsSection.appendChild(actionsLabel);

  const actionRow = document.createElement("div");
  actionRow.className = "action-buttons";
  
  // Find status badge in header for local updates
  const statusBadge = header.querySelector(".subtask-badge.status");
  
  actionRow.appendChild(btn("Start", "btn", async () => {
    try { 
      await setStatus(st.id, "start", slog, reload, (newStatus) => {
        if (statusBadge) statusBadge.textContent = newStatus;
        closeSubtaskPanel();
        // Always reload after status changes
        reload();
      }); 
    } catch (e) { showToast(e.message || "Failed to update status", "error"); }
  }));
  actionRow.appendChild(btn("Block", "btn warn", async () => {
    try { 
      await setStatus(st.id, "block", slog, reload, (newStatus) => {
        if (statusBadge) statusBadge.textContent = newStatus;
        closeSubtaskPanel();
        // Always reload after status changes
        reload();
      }); 
    } catch (e) { showToast(e.message || "Failed to update status", "error"); }
  }));
  actionRow.appendChild(btn("Complete", "btn success", async () => {
    try { 
      await setStatus(st.id, "complete", slog, reload, (newStatus) => {
        if (statusBadge) statusBadge.textContent = newStatus;
        closeSubtaskPanel();
        // Always reload after completion
        reload();
      }); 
    } catch (e) { showToast(e.message || "Failed to update status", "error"); }
  }));
  actionRow.appendChild(btn("Delete", "btn danger", async () => {
    try { 
      await deleteTask(st.id, slog, reload, () => {
        row.remove(); // Remove subtask from view
        closeSubtaskPanel();
        // Reload to ensure parent task subtask count is updated
        reload();
      }); 
    } catch (e) { slog("Subtask delete error", String(e)); showToast(e.message || "Failed to delete task", "error"); }
  }));
  actionRow.appendChild(btn("Edit", "btn primary", () => {
    document.dispatchEvent(new CustomEvent("open-edit", { detail: st }));
  }));
  actionRow.appendChild(btn("Detach", "btn danger", async () => {
    try {
      await apiTask(`/${parentId}/subtasks/${st.id}`, { method: "DELETE" });
      slog(`DELETE /task/${parentId}/subtasks/${st.id}`, "204");
      row.remove(); // Remove subtask from view
      closeSubtaskPanel();
      showToast("Subtask detached successfully", "success");
      // Reload to ensure parent task subtask count is updated
      reload();
    } catch (e) { slog("Detach error", String(e)); showToast(e.message || "Failed to detach subtask", "error"); }
  }));

  // Always show actions (including for completed subtasks)
  actionsSection.appendChild(actionRow);
  details.appendChild(actionsSection);

  // Assignee controls: only for non-completed subtasks and non-staff users
  if (!isCurrentUserStaff() && st.status !== "Completed") {
    details.appendChild(renderAssigneeControls(st, { log, reload }));
  } else {
    // For completed subtasks or staff users, show read-only assignees
    details.appendChild(renderAssigneeDisplay(st, { log }));
  }
  
  // Comments section (always show for all subtasks)
  details.appendChild(renderCommentsSection(st, { log, reload }));
  
  // Subtasks section (check if this subtask has its own subtasks)
  const subtasks = getSubtasks(st);
  if (Array.isArray(subtasks) && subtasks.length > 0) {
    const subtasksSection = document.createElement("div");
    subtasksSection.className = "task-section expanded";
    
    const subtasksHeader = document.createElement("div");
    subtasksHeader.className = "subtasks-header";
    
    const subtasksLabel = document.createElement("div");
    subtasksLabel.className = "task-section-label";
    subtasksLabel.textContent = `Subtasks (${subtasks.length})`;
    subtasksHeader.appendChild(subtasksLabel);
    
    const expander = document.createElement("div");
    expander.className = "subtask-expander";
    expander.textContent = "▼";
    subtasksHeader.appendChild(expander);
    
    subtasksSection.appendChild(subtasksHeader);

    const subtasksList = document.createElement("div");
    subtasksList.className = "subtasks";
    subtasks.forEach(subtask => subtasksList.appendChild(renderSubtaskRow(st.id, subtask, { log, reload })));
    subtasksSection.appendChild(subtasksList);
    
    // Toggle expansion
    subtasksHeader.addEventListener("click", () => {
      subtasksSection.classList.toggle("expanded");
    });
    
    details.appendChild(subtasksSection);
  }
  
  panelInner.appendChild(details);
  
  // Open panel on header click
  header.addEventListener("click", () => {
    openSubtaskPanel(panelInner);
  });

  return row;
}

// Panel open/close functions
function openSubtaskPanel(content) {
  const panel = document.getElementById("subtaskPanel");
  const panelInner = document.getElementById("subtaskPanelInner");
  
  if (panel && panelInner) {
    panelInner.innerHTML = "";
    panelInner.appendChild(content);
    
    // Check if calendar task panel is open - if so, nest the subtask on the left
    const calPanel = document.getElementById("calTaskPanel");
    
    if (calPanel && calPanel.classList.contains("active")) {
      panelNestLevel++;
      
      if (panelNestLevel === 1) {
        panel.classList.add("nested");
        panel.classList.remove("nested-again");
      } else if (panelNestLevel >= 2) {
        panel.classList.add("nested", "nested-again");
      }
    } else {
      panelNestLevel = 0;
      panel.classList.remove("nested", "nested-again");
    }
    
    panel.classList.add("active");
    
    // Close on backdrop click
    const backdrop = panel.querySelector(".subtask-panel-backdrop");
    if (backdrop) {
      backdrop.addEventListener("click", closeSubtaskPanel, { once: true });
    }
  }
}

function closeSubtaskPanel() {
  const panel = document.getElementById("subtaskPanel");
  if (panel) {
    panel.classList.remove("active");
    
    // Reset nest level when closing all panels
    if (panelNestLevel > 0) {
      panelNestLevel--;
    }
  }
}

// Panel functions for calendar task details (exported)
export function openCalTaskPanel(task, { log, reload }) {
  const panel = document.getElementById("calTaskPanel");
  const panelInner = document.getElementById("calTaskPanelInner");
  
  if (panel && panelInner) {
    panelInner.innerHTML = "";
    
    // Create header
    const header = document.createElement("div");
    header.className = "cal-task-panel-header";
    header.innerHTML = `<h3>#${task.id} - ${escapeHtml(task.title || "")}</h3>`;
    
    const closeBtn = document.createElement("button");
    closeBtn.className = "cal-task-panel-close";
    closeBtn.innerHTML = "×";
    closeBtn.addEventListener("click", () => closeCalTaskPanel());
    header.appendChild(closeBtn);
    
    panelInner.appendChild(header);
    
    // Build details from scratch (similar to subtask panel)
    const details = document.createElement("div");
    details.className = "task-details";
    details.style.display = "block";
    
    // Description
    if (task.description) {
      const descBox = document.createElement("div");
      descBox.className = "task-description";
      descBox.textContent = task.description;
      details.appendChild(descBox);
    }
    
    // Metadata section
    const metadataSection = document.createElement("div");
    metadataSection.className = "task-section";
    
    const metadataLabel = document.createElement("div");
    metadataLabel.className = "task-section-label";
    metadataLabel.textContent = "Details";
    metadataSection.appendChild(metadataLabel);
    
    const metadata = document.createElement("div");
    metadata.className = "task-details-grid";
    
    const fields = [];
    
    // Parent task info (for subtasks)
    if (task.__isSub && task.__parentId && task.__parentTitle) {
      fields.push(field("Parent Task", `#${task.__parentId} - ${escapeHtml(task.__parentTitle)}`));
    }
    
    if (task.start_date) {
      fields.push(field("Start Date", task.start_date));
    }
    if (task.deadline) {
      fields.push(field("Deadline", task.deadline));
    }
    if (task.project_id != null) {
      fields.push(field("Project", `#${task.project_id}`));
    }
    if (task.tag) {
      fields.push(field("Tag", task.tag));
    }
    if (task.recurring && task.recurring > 0) {
      fields.push(field("Recurring", `Every ${task.recurring} days`));
    }
    
    fields.forEach((fieldEl, index) => {
      metadata.appendChild(fieldEl);
      if (index < fields.length - 1) {
        const separator = document.createElement("span");
        separator.textContent = "|";
        separator.style.color = "var(--sub)";
        separator.style.margin = "0 4px";
        metadata.appendChild(separator);
      }
    });
    
    metadataSection.appendChild(metadata);
    details.appendChild(metadataSection);
    
    // Actions section
    const actionsSection = document.createElement("div");
    actionsSection.className = "task-section";
    
    const actionsLabel = document.createElement("div");
    actionsLabel.className = "task-section-label";
    actionsLabel.textContent = "Actions";
    actionsSection.appendChild(actionsLabel);
    
    const actionRow = document.createElement("div");
    actionRow.className = "action-buttons";
    
    actionRow.appendChild(btn("Start", "btn", () => setStatus(task.id, "start", log, reload, (newStatus) => {
      closeCalTaskPanel();
      reload();
    })));
    actionRow.appendChild(btn("Block", "btn warn", () => setStatus(task.id, "block", log, reload, (newStatus) => {
      closeCalTaskPanel();
      reload();
    })));
    actionRow.appendChild(btn("Complete", "btn success", () => setStatus(task.id, "complete", log, reload, (newStatus) => {
      closeCalTaskPanel();
      reload();
    })));
    actionRow.appendChild(btn("Delete", "btn danger", () => deleteTask(task.id, log, reload, () => {
      closeCalTaskPanel();
      reload();
    })));
    actionRow.appendChild(btn("Edit", "btn primary", () => {
      document.dispatchEvent(new CustomEvent("open-edit", { detail: task }));
    }));
    
    actionsSection.appendChild(actionRow);
    details.appendChild(actionsSection);
    
    // Assignee controls: only for non-completed tasks and non-staff users
    if (task.status !== "Completed" && !isCurrentUserStaff()) {
      details.appendChild(renderAssigneeControls(task, { log, reload }));
    } else {
      details.appendChild(renderAssigneeDisplay(task, { log }));
    }
    
    // Comments section
    details.appendChild(renderCommentsSection(task, { log, reload }));
    
    // Subtasks section
    const subs = getSubtasks(task);
    if (Array.isArray(subs) && subs.length > 0) {
      const subtasksSection = document.createElement("div");
      subtasksSection.className = "task-section expanded";
      
      const subtasksHeader = document.createElement("div");
      subtasksHeader.className = "subtasks-header";
      
      const subtasksLabel = document.createElement("div");
      subtasksLabel.className = "task-section-label";
      subtasksLabel.textContent = `Subtasks (${subs.length})`;
      subtasksHeader.appendChild(subtasksLabel);
      
      const expander = document.createElement("div");
      expander.className = "subtask-expander";
      expander.textContent = "▼";
      subtasksHeader.appendChild(expander);
      
      subtasksSection.appendChild(subtasksHeader);
      
      const subtasksList = document.createElement("div");
      subtasksList.className = "subtasks";
      subs.forEach(st => subtasksList.appendChild(renderSubtaskRow(task.id, st, { log, reload })));
      subtasksSection.appendChild(subtasksList);
      
      subtasksHeader.addEventListener("click", () => {
        subtasksSection.classList.toggle("expanded");
      });
      
      details.appendChild(subtasksSection);
    }
    
    panelInner.appendChild(details);
    
    panel.classList.add("active");
    
    // Close on backdrop click
    const backdrop = panel.querySelector(".cal-task-panel-backdrop");
    if (backdrop) {
      backdrop.addEventListener("click", closeCalTaskPanel, { once: true });
    }
  }
}

export function closeCalTaskPanel() {
  const panel = document.getElementById("calTaskPanel");
  if (panel) {
    panel.classList.remove("active");
    // Reset nest level when the task panel closes
    panelNestLevel = 0;
  }
}

/* ------------------------- Comments Section ------------------------- */

function renderCommentsSection(task, { log, reload }) {
  const slog = asLog(log);

  const commentsWrap = document.createElement("div");
  commentsWrap.className = "task-section";

  // Section label with comment count
  const sectionLabel = document.createElement("div");
  sectionLabel.className = "task-section-label";
  const labelText = document.createElement("span");
  labelText.textContent = "Comments";
  sectionLabel.appendChild(labelText);
  
  const countEl = document.createElement("span");
  countEl.className = "comment-count";
  countEl.id = `comment-count-${task.id}`;
  sectionLabel.appendChild(countEl);
  
  commentsWrap.appendChild(sectionLabel);

  // Comments container
  const commentsContainer = document.createElement("div");
  commentsContainer.className = "comments-container";
  commentsContainer.id = `comments-${task.id}`;
  commentsWrap.appendChild(commentsContainer);

  // Create a local renderComments function that uses closure variables
  const renderComments = (comments) => {
    // Update count
    if (!comments || comments.length === 0) {
      countEl.textContent = "";
    } else {
      countEl.textContent = ` (${comments.length})`;
    }
    
    // Clear container
    commentsContainer.innerHTML = "";
    
    if (!comments || comments.length === 0) {
      const empty = document.createElement("div");
      empty.className = "comment-empty";
      empty.textContent = "No comments yet";
      commentsContainer.appendChild(empty);
      return;
    }
    
    // Sort comments by timestamp (newest first)
    const sortedComments = [...comments].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
    
    sortedComments.forEach(comment => {
      const commentEl = renderCommentCard(comment);
      commentsContainer.appendChild(commentEl);
    });
  };
  
  // Load comments function using closure
  async function loadComments() {
    try {
      const comments = await apiTask(`/${task.id}/comment`, { method: "GET" });
      renderComments(comments || []);
      slog("Loaded comments for task", task.id, comments);
    } catch (error) {
      slog("Failed to load comments", error);
      renderComments([]);
    }
  }

  // Add comment form (always show for all tasks, including completed)
  const addCommentForm = document.createElement("div");
  addCommentForm.className = "add-comment-form";
  
  const textarea = document.createElement("textarea");
  textarea.placeholder = "Add a comment...";
  textarea.className = "comment-input";
  textarea.id = `comment-input-${task.id}`;
  
  const userSelect = document.createElement("select");
  userSelect.className = "comment-user-select";
  userSelect.id = `comment-user-${task.id}`;
  
  // Populate user dropdown
  const users = getUsers();
  let selectedUserId = null;
  
  if (users && users.length > 0) {
    users.forEach(user => {
      const option = document.createElement("option");
      option.value = user.user_id || user.id;
      option.textContent = user.name || user.full_name || user.email;
      
      // Auto-select current user for staff, managers, and directors
      if (CURRENT_USER && (user.user_id || user.id) === CURRENT_USER.user_id) {
        option.selected = true;
        selectedUserId = option.value;
      }
      
      userSelect.appendChild(option);
    });
    
    // Hide the dropdown for staff, managers, and directors since they're auto-selected
    if (isCurrentUserStaff() || isCurrentUserManagerOrDirector()) {
      userSelect.style.display = "none";
    }
  }
  
  const mentionSelect = document.createElement("select");
  mentionSelect.className = "comment-mention-select";
  mentionSelect.id = `comment-mentions-${task.id}`;
  mentionSelect.multiple = true;
  mentionSelect.setAttribute("size", "3");
  
  // Add label for mentions dropdown
  const mentionLabel = document.createElement("label");
  mentionLabel.textContent = "Tag users (optional):";
  mentionLabel.className = "comment-mention-label";
  mentionLabel.setAttribute("for", mentionSelect.id);
  
  // Populate mentions dropdown with all users except the commenter
  // Reuse the users list already fetched above
  if (users && users.length > 0) {
    users.forEach(user => {
      // Skip current user (commenter)
      if (CURRENT_USER && (user.user_id || user.id) === CURRENT_USER.user_id) {
        return;
      }
      
      const option = document.createElement("option");
      option.value = user.email;
      option.textContent = user.name || user.full_name || user.email;
      mentionSelect.appendChild(option);
    });
  }
  
  const submitBtn = document.createElement("button");
  submitBtn.textContent = "Add Comment";
  submitBtn.className = "btn primary comment-submit";
  submitBtn.addEventListener("click", async () => {
    const commentText = textarea.value.trim();
    const userId = parseInt(userSelect.value);
    
    if (!commentText || !userId) {
      showToast("Please enter a comment and select a user", "warning");
      return;
    }
    
    // Get selected mention emails and user names
    const mentionedEmails = Array.from(mentionSelect.selectedOptions).map(opt => opt.value);
    const mentionedUsers = Array.from(mentionSelect.selectedOptions).map(opt => {
      const user = users.find(u => u.email === opt.value);
      return user ? (user.name || user.full_name || user.email) : opt.value;
    });
    
    // Append @mentions to comment text
    let finalCommentText = commentText;
    if (mentionedUsers.length > 0) {
      const mentionString = mentionedUsers.map(name => `@${name}`).join(" ");
      finalCommentText = `${commentText} ${mentionString}`;
    }
    
    try {
      await addCommentToTask(task.id, userId, finalCommentText, mentionedEmails, slog);
      textarea.value = "";
      mentionSelect.selectedIndex = -1; // Clear selections
      await loadComments();
      showToast("Comment added successfully", "success");
      // Don't reload - just refresh comments locally to keep task expanded
    } catch (error) {
      showToast("Failed to add comment", "error");
    }
  });
  
  addCommentForm.appendChild(textarea);
  addCommentForm.appendChild(mentionLabel);
  addCommentForm.appendChild(mentionSelect);
  addCommentForm.appendChild(userSelect);
  addCommentForm.appendChild(submitBtn);
  commentsWrap.appendChild(addCommentForm);

  // Load and render comments
  loadComments();

  return commentsWrap;
}

async function loadCommentsForTask(taskId, log) {
  const slog = asLog(log);
  
  try {
    const comments = await apiTask(`/${taskId}/comment`, { method: "GET" });
    renderComments(comments || [], taskId);
    slog("Loaded comments for task", taskId, comments);
  } catch (error) {
    slog("Failed to load comments", error);
    renderComments([], taskId);
  }
}

function renderComments(comments, taskId) {
  const container = document.getElementById(`comments-${taskId}`);
  const countEl = document.getElementById(`comment-count-${taskId}`);
  
  if (!container) return;
  
  // Update count
  if (countEl) {
    if (!comments || comments.length === 0) {
      countEl.textContent = "";
    } else {
      countEl.textContent = ` (${comments.length})`;
    }
  }
  
  container.innerHTML = "";
  
  if (!comments || comments.length === 0) {
    const empty = document.createElement("div");
    empty.className = "comment-empty";
    empty.textContent = "No comments yet";
    container.appendChild(empty);
      return;
    }
  
  // Sort comments by timestamp (newest first)
  const sortedComments = [...comments].sort((a, b) => new Date(b.timestamp) - new Date(a.timestamp));
  
  sortedComments.forEach(comment => {
    const commentEl = renderCommentCard(comment);
    container.appendChild(commentEl);
  });
}

/**
 * Parses comment text and renders @mentions as highlighted spans
 * @param {string} commentText - The comment text to parse
 * @param {HTMLElement} container - The container element to append fragments to
 */
function parseAndRenderMentions(commentText, container) {
  if (!commentText) {
    container.textContent = "";
    return;
  }
  
  const mentionRegex = /@(\S+)/g;
  let lastIndex = 0;
  const fragments = [];
  let match;
  
  while ((match = mentionRegex.exec(commentText)) !== null) {
    // Add text before mention
    if (match.index > lastIndex) {
      const textNode = document.createTextNode(commentText.substring(lastIndex, match.index));
      fragments.push(textNode);
    }
    
    // Add mention as highlighted span
    const mentionSpan = document.createElement("span");
    mentionSpan.className = "comment-mention";
    mentionSpan.textContent = match[0]; // @username
    mentionSpan.title = `Mentioned: ${match[1]}`;
    fragments.push(mentionSpan);
    
    lastIndex = match.index + match[0].length;
  }
  
  // Add remaining text
  if (lastIndex < commentText.length) {
    const textNode = document.createTextNode(commentText.substring(lastIndex));
    fragments.push(textNode);
  }
  
  // If no mentions found, just add the text as-is
  if (fragments.length === 0) {
    container.textContent = commentText;
  } else {
    fragments.forEach(fragment => container.appendChild(fragment));
  }
}

function renderCommentCard(comment) {
  const card = document.createElement("div");
  card.className = "comment-card";
  card.setAttribute("data-comment-id", comment.comment_id);
  
  const header = document.createElement("div");
  header.className = "comment-header";
  
  // User info
  const userInfo = document.createElement("div");
  userInfo.className = "comment-user";
  
  const user = getUsers()?.find(u => (u.user_id || u.id) === comment.user_id);
  const userName = user?.name || user?.full_name || user?.email || `User ${comment.user_id}`;
  
  const userAvatar = document.createElement("div");
  userAvatar.className = "comment-avatar";
  userAvatar.textContent = userName.charAt(0).toUpperCase();
  
  const userDetails = document.createElement("div");
  userDetails.className = "comment-user-details";
  
  const userNameEl = document.createElement("span");
  userNameEl.className = "comment-user-name";
  userNameEl.textContent = userName;
  
  const timestampEl = document.createElement("span");
  timestampEl.className = "comment-timestamp";
  timestampEl.textContent = formatTimestamp(comment.timestamp);
  
  userDetails.appendChild(userNameEl);
  userDetails.appendChild(timestampEl);
  
  userInfo.appendChild(userAvatar);
  userInfo.appendChild(userDetails);
  header.appendChild(userInfo);
  
  // Actions (edit) - only show for comment author
  const actions = document.createElement("div");
  actions.className = "comment-actions";
  
  // Check if current user is the comment author
  const canEdit = CURRENT_USER && (CURRENT_USER.user_id === comment.user_id);
  
  if (canEdit) {
    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.className = "btn-small comment-edit";
    editBtn.addEventListener("click", () => {
      editComment(comment, card);
    });
    
    actions.appendChild(editBtn);
  }
  
  header.appendChild(actions);
  
  const content = document.createElement("div");
  content.className = "comment-content";
  
  // Parse and render comment with @mentions highlighted
  parseAndRenderMentions(comment.comment || "", content);
  
  card.appendChild(header);
  card.appendChild(content);
  
  return card;
}

async function addCommentToTask(taskId, userId, commentText, mentionedEmails = [], log) {
  const slog = asLog(log);
  
  const payload = {
    user_id: userId,
    comment: commentText,
    recipient_emails: mentionedEmails.length > 0 ? mentionedEmails : null
  };
  
  try {
    const result = await apiTask(`/${taskId}/comment`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    slog("Added comment", result);
    return result;
  } catch (error) {
    slog("Failed to add comment", error);
    throw error;
  }
}

function formatTimestamp(timestamp) {
  const date = new Date(timestamp);
  const now = new Date();
  const diffMs = now - date;
  const diffHours = Math.floor(diffMs / (1000 * 60 * 60));
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffHours < 1) {
    return "Just now";
  } else if (diffHours < 24) {
    return `${diffHours} hour${diffHours > 1 ? 's' : ''} ago`;
  } else if (diffDays < 7) {
    return `${diffDays} day${diffDays > 1 ? 's' : ''} ago`;
  } else {
    return date.toLocaleDateString();
  }
}

async function editComment(comment, commentCard) {
  const contentEl = commentCard.querySelector('.comment-content');
  const actionsEl = commentCard.querySelector('.comment-actions');
  
  // Create edit form
  const editForm = document.createElement('div');
  editForm.className = 'comment-edit-form';
  
  const textarea = document.createElement('textarea');
  textarea.value = comment.comment;
  textarea.className = 'comment-edit-input';
  
  const buttonRow = document.createElement('div');
  buttonRow.className = 'comment-edit-buttons';
  
  const saveBtn = document.createElement('button');
  saveBtn.textContent = 'Save';
  saveBtn.className = 'btn primary btn-small';
  saveBtn.addEventListener('click', async () => {
    const newText = textarea.value.trim();
    if (!newText) {
      showToast('Comment cannot be empty', "warning");
      return;
    }
    
    try {
      await updateComment(comment.comment_id, newText);
      // Replace the content with parsed mentions
      contentEl.innerHTML = '';
      parseAndRenderMentions(newText, contentEl);
      // Show content again
      contentEl.style.display = 'block';
      // Remove edit form
      commentCard.removeChild(editForm);
      // Show actions again
      actionsEl.style.display = 'flex';
      showToast("Comment updated successfully", "success");
    } catch (error) {
      showToast('Failed to update comment', "error");
    }
  });
  
  const cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel';
  cancelBtn.className = 'btn btn-small';
  cancelBtn.addEventListener('click', () => {
    // Show content again
    contentEl.style.display = 'block';
    // Remove edit form
    commentCard.removeChild(editForm);
    // Show actions again
    actionsEl.style.display = 'flex';
  });
  
  buttonRow.appendChild(saveBtn);
  buttonRow.appendChild(cancelBtn);
  
  editForm.appendChild(textarea);
  editForm.appendChild(buttonRow);
  
  // Hide actions and content, show edit form
  actionsEl.style.display = 'none';
  contentEl.style.display = 'none';
  commentCard.appendChild(editForm);
  
  // Focus the textarea
  textarea.focus();
  textarea.select();
}

async function deleteComment(commentId) {
  if (!CURRENT_USER) {
    showToast('No current user set', "warning");
    return;
  }
  
  const payload = {
    requesting_user_id: CURRENT_USER.user_id
  };
  
  try {
    await apiTask(`/comment/${commentId}`, { 
      method: "DELETE",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    // Find and remove the comment card from DOM
    const commentCard = document.querySelector(`[data-comment-id="${commentId}"]`);
    if (commentCard) {
      commentCard.remove();
      
      // Update comment count
      const taskId = commentCard.closest('.task').dataset.taskId;
      if (taskId) {
        await loadCommentsForTask(taskId, console.log);
      }
      showToast("Comment deleted successfully", "success");
    }
  } catch (error) {
    showToast('Failed to delete comment', "error");
  }
}

async function updateComment(commentId, newText) {
  if (!CURRENT_USER) {
    throw new Error("No current user set");
  }
  
  const payload = {
    comment: newText,
    requesting_user_id: CURRENT_USER.user_id
  };
  
  try {
    const result = await apiTask(`/comment/${commentId}`, {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload)
    });
    
    return result;
  } catch (error) {
    throw error;
  }
}
