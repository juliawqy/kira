// js/ui/cards.js
import { apiTask } from "../api.js";
import { USERS, getSubtasks, getAssignees, getPriorityDisplay, escapeHtml, getUsers } from "../state.js";
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

  // Comments section (always show for all tasks)
  details.appendChild(renderCommentsSection(task, { log, reload }));

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

  // Add comment form (only for non-completed tasks)
  if (task.status !== "Completed") {
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
    if (users && users.length > 0) {
      users.forEach(user => {
        const option = document.createElement("option");
        option.value = user.user_id || user.id;
        option.textContent = user.name || user.full_name || user.email;
        userSelect.appendChild(option);
      });
    }
    
    const submitBtn = document.createElement("button");
    submitBtn.textContent = "Add Comment";
    submitBtn.className = "btn primary comment-submit";
    submitBtn.addEventListener("click", async () => {
      const commentText = textarea.value.trim();
      const userId = parseInt(userSelect.value);
      
      if (!commentText || !userId) {
        alert("Please enter a comment and select a user");
        return;
      }
      
      try {
        await addCommentToTask(task.id, userId, commentText, slog);
        textarea.value = "";
        await loadCommentsForTask(task.id, slog);
        // Don't reload - just refresh comments locally to keep task expanded
      } catch (error) {
        alert("Failed to add comment: " + error.message);
      }
    });
    
    addCommentForm.appendChild(textarea);
    addCommentForm.appendChild(userSelect);
    addCommentForm.appendChild(submitBtn);
    commentsWrap.appendChild(addCommentForm);
  }

  // Load and render comments
  loadCommentsForTask(task.id, slog);

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
  
  // Actions (edit/delete) - only show for non-completed tasks
  const actions = document.createElement("div");
  actions.className = "comment-actions";
  
  // Check if current user can edit this comment (for now, allow all users)
  // In a real app, you'd check if current user is the comment author
  const canEdit = true; // TODO: Implement proper user authentication
  
  if (canEdit) {
    const editBtn = document.createElement("button");
    editBtn.textContent = "Edit";
    editBtn.className = "btn-small comment-edit";
    editBtn.addEventListener("click", () => {
      editComment(comment, card);
    });
    
    const deleteBtn = document.createElement("button");
    deleteBtn.textContent = "Delete";
    deleteBtn.className = "btn-small comment-delete";
    deleteBtn.addEventListener("click", () => {
      if (confirm("Are you sure you want to delete this comment?")) {
        deleteComment(comment.comment_id);
      }
    });
    
    actions.appendChild(editBtn);
    actions.appendChild(deleteBtn);
  }
  
  header.appendChild(actions);
  
  const content = document.createElement("div");
  content.className = "comment-content";
  content.textContent = comment.comment;
  
  card.appendChild(header);
  card.appendChild(content);
  
  return card;
}

async function addCommentToTask(taskId, userId, commentText, log) {
  const slog = asLog(log);
  
  const payload = {
    user_id: userId,
    comment: commentText
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
      alert('Comment cannot be empty');
      return;
    }
    
    try {
      await updateComment(comment.comment_id, newText);
      // Replace the content
      contentEl.textContent = newText;
      // Remove edit form
      commentCard.removeChild(editForm);
      // Show actions again
      actionsEl.style.display = 'flex';
    } catch (error) {
      alert('Failed to update comment: ' + error.message);
    }
  });
  
  const cancelBtn = document.createElement('button');
  cancelBtn.textContent = 'Cancel';
  cancelBtn.className = 'btn btn-small';
  cancelBtn.addEventListener('click', () => {
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
  try {
    await apiTask(`/comment/${commentId}`, { method: "DELETE" });
    
    // Find and remove the comment card from DOM
    const commentCard = document.querySelector(`[data-comment-id="${commentId}"]`);
    if (commentCard) {
      commentCard.remove();
      
      // Update comment count
      const taskId = commentCard.closest('.task').dataset.taskId;
      if (taskId) {
        await loadCommentsForTask(taskId, console.log);
      }
    }
  } catch (error) {
    alert('Failed to delete comment: ' + error.message);
  }
}

async function updateComment(commentId, newText) {
  const payload = {
    comment: newText
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
