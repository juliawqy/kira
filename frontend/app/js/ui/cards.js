// js/ui/cards.js
import { apiTask } from "../api.js";
import { USERS, getSubtasks, getAssignees, getPriorityDisplay, escapeHtml } from "../state.js";
import { field } from "./dom.js";

/* ----------------------------- safe log ----------------------------- */
function asLog(log) {
  return typeof log === "function" ? log : (...args) => console.log(...args);
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
    if (callback) {
      callback(newStatus);
    } else {
      reload();
    }
  } catch (e) {
    slog("Status error", String(e));
    alert(e.message);
  }
}

async function deleteTask(id, log, reload, callback) {
  const slog = asLog(log);
  try {
    const res = await apiTask(`/${id}/delete`, { method: "POST" });
    slog(`POST /task/${id}/delete`, res);
    if (callback) {
      callback();
    } else {
      reload();
    }
  } catch (e) {
    slog("Delete error", String(e));
    alert(e.message);
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
    statusBadge.className = "task-badge status";
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
  
  // Only show actions for non-completed tasks
  if (task.status !== "Completed") {
    actionsSection.appendChild(actionRow);
    details.appendChild(actionsSection);
    
    // Assignee controls with add/remove functionality
    details.appendChild(renderAssigneeControls(task, { log, reload }));
  } else {
    // For completed tasks, show read-only assignees
    details.appendChild(renderAssigneeDisplay(task, { log }));
  }

  // Subtasks section
  const subs = getSubtasks(task);
  if (Array.isArray(subs) && subs.length > 0) {
    const subtasksSection = document.createElement("div");
    subtasksSection.className = "task-section";
    
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
    } catch (e) { slog("Assign error", String(e)); alert(e.message); }
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
    const chipsInlineEl = document.getElementById(`assignee-chips-${task.id}`);
    if (chipsInlineEl) chipsInlineEl.innerHTML = "";
    
    // Update the count in the label
    const countEl = document.getElementById(`assignee-count-${task.id}`);
    if (countEl) {
      if (!list || list.length === 0) {
        countEl.textContent = "";
      } else {
        countEl.textContent = ` (${list.length}):`;
      }
    }
    
    if (!list || list.length === 0) {
      const none = document.createElement("span");
      none.className = "assignee-empty";
      none.textContent = "No assignees";
      // Add to inline container instead of main container
      if (chipsInlineEl) {
        chipsInlineEl.appendChild(none);
      } else {
        current.appendChild(none);
      }
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
        } catch (err) { slog("Unassign error", String(err)); alert(err.message); }
      });

      chip.appendChild(remove);
      
      // Add to inline container
      if (chipsInlineEl) {
        chipsInlineEl.appendChild(chip);
      }
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

  // Compact header
  const header = document.createElement("div");
  header.className = "subtask-header";
  
  const left = document.createElement("div");
  left.className = "subtask-info";
  const bits = [
    `<strong>#${st.id}</strong>`,
    escapeHtml(st.title || ""),
    `<span class="subtask-badge status">${st.status}</span>`
  ];
  left.innerHTML = bits.join(" &nbsp; ");
  header.appendChild(left);

  const expander = document.createElement("div");
  expander.className = "subtask-expander-icon";
  expander.textContent = "▼";
  header.appendChild(expander);
  
  row.appendChild(header);

  // Create popup dialog for subtask details
  const dialog = document.createElement("dialog");
  dialog.className = "subtask-dialog";
  
  const dialogContent = document.createElement("div");
  dialogContent.className = "subtask-dialog-content";
  
  const dialogHeader = document.createElement("div");
  dialogHeader.className = "subtask-dialog-header";
  dialogHeader.innerHTML = `<h3>#${st.id} - ${escapeHtml(st.title || "")}</h3>`;
  
  const closeBtn = document.createElement("button");
  closeBtn.className = "subtask-dialog-close";
  closeBtn.innerHTML = "×";
  closeBtn.addEventListener("click", () => dialog.close());
  dialogHeader.appendChild(closeBtn);
  
  dialogContent.appendChild(dialogHeader);
  
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
        dialog.close();
        // Always reload after status changes
        reload();
      }); 
    } catch (e) { alert(e.message); }
  }));
  actionRow.appendChild(btn("Block", "btn warn", async () => {
    try { 
      await setStatus(st.id, "block", slog, reload, (newStatus) => {
        if (statusBadge) statusBadge.textContent = newStatus;
        dialog.close();
        // Always reload after status changes
        reload();
      }); 
    } catch (e) { alert(e.message); }
  }));
  actionRow.appendChild(btn("Complete", "btn success", async () => {
    try { 
      await setStatus(st.id, "complete", slog, reload, (newStatus) => {
        if (statusBadge) statusBadge.textContent = newStatus;
        dialog.close();
        // Always reload after completion
        reload();
      }); 
    } catch (e) { alert(e.message); }
  }));
  actionRow.appendChild(btn("Delete", "btn danger", async () => {
    try { 
      await deleteTask(st.id, slog, reload, () => {
        row.remove(); // Remove subtask from view
        dialog.close();
        // Reload to ensure parent task subtask count is updated
        reload();
      }); 
    } catch (e) { slog("Subtask delete error", String(e)); alert(e.message); }
  }));
  actionRow.appendChild(btn("Edit", "btn primary", () => {
    document.dispatchEvent(new CustomEvent("open-edit", { detail: st }));
  }));
  actionRow.appendChild(btn("Detach", "btn danger", async () => {
    try {
      await apiTask(`/${parentId}/subtasks/${st.id}`, { method: "DELETE" });
      slog(`DELETE /task/${parentId}/subtasks/${st.id}`, "204");
      row.remove(); // Remove subtask from view
      dialog.close();
      // Reload to ensure parent task subtask count is updated
      reload();
    } catch (e) { slog("Detach error", String(e)); alert(e.message); }
  }));
  
  actionsSection.appendChild(actionRow);
  details.appendChild(actionsSection);

  // Assignee controls
  details.appendChild(renderAssigneeControls(st, { log, reload }));
  
  dialogContent.appendChild(details);
  dialog.appendChild(dialogContent);
  
  // Don't append dialog to row, keep it separate
  row.appendChild(dialog);
  
  // Open dialog on header click
  header.addEventListener("click", () => {
    dialog.showModal();
  });

  return row;
}
