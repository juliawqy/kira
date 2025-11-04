import { apiTask } from "../api.js";
import { showToast } from "../state.js";

const YMD = /^\d{4}-\d{2}-\d{2}$/;
const isValidYmd = (s) => !!(s && YMD.test(s));

function setError(inputEl, errorEl, message) {
  if (!errorEl) return;
  if (message) {
    errorEl.textContent = message;
    inputEl && inputEl.classList && inputEl.classList.add("invalid");
  } else {
    errorEl.textContent = "";
    inputEl && inputEl.classList && inputEl.classList.remove("invalid");
  }
}

export function bindEditDialog(log, reload) {
  const dlgEdit     = document.getElementById("dlgEdit");
  const e_title     = document.getElementById("e_title");
  const e_desc      = document.getElementById("e_desc");
  const e_priority  = document.getElementById("e_priority");
  const e_start     = document.getElementById("e_start");
  const e_due       = document.getElementById("e_due");
  const e_project   = document.getElementById("e_project");
  const e_tag       = document.getElementById("e_tag");
  const e_recurring = document.getElementById("e_recurring");
  const hint        = document.getElementById("e_hint");

  // error elements
  const er_title     = document.getElementById("e_title_err");
  const er_desc      = document.getElementById("e_desc_err");
  const er_priority  = document.getElementById("e_priority_err");
  const er_start     = document.getElementById("e_start_err");
  const er_due       = document.getElementById("e_due_err");
  const er_project   = document.getElementById("e_project_err");
  const er_tag       = document.getElementById("e_tag_err");
  const er_recurring = document.getElementById("e_recurring_err");

  let editingTaskId = null;

  // keep date constraints in sync
  function syncMinMax() {
    if (e_start.value) e_due.min = e_start.value; else e_due.removeAttribute("min");
    if (e_due.value) e_start.max = e_due.value; else e_start.removeAttribute("max");
  }
  e_start.addEventListener("change", syncMinMax);
  e_due.addEventListener("change", syncMinMax);

  document.addEventListener("open-edit", (ev) => {
    const task = ev.detail;
    editingTaskId = task.id;

    [ [e_title,er_title], [e_desc,er_desc], [e_priority,er_priority], [e_start,er_start],
      [e_due,er_due], [e_project,er_project], [e_tag,er_tag], [e_recurring,er_recurring] ]
      .forEach(([i,e]) => setError(i,e,""));

    e_title.value = task.title || "";
    e_desc.value = task.description || "";
    e_priority.value = (typeof task.priority === "number" ? task.priority : "") || "";
    e_start.value = task.start_date || "";
    e_due.value = task.deadline || "";
    e_project.value = task.project_id != null ? String(task.project_id) : "";
    e_tag.value = task.tag || "";
    e_recurring.value = (typeof task.recurring === "number" ? task.recurring : "") || "";
    hint.textContent = `Editing #${task.id} (status updates are separate actions)`;

    syncMinMax();
    dlgEdit.showModal();
  });

  function validate() {
    let ok = true;

    [ [e_title,er_title],[e_desc,er_desc],[e_priority,er_priority],[e_start,er_start],
      [e_due,er_due],[e_project,er_project],[e_tag,er_tag],[e_recurring,er_recurring] ]
      .forEach(([i,e]) => setError(i,e,""));

    if (e_priority.value !== "") {
      const pb = Number(e_priority.value);
      if (Number.isNaN(pb) || pb < 1 || pb > 10) {
        ok = false; setError(e_priority, er_priority, "Priority must be 1–10.");
      }
    }

    if (e_project.value !== "" && Number.isNaN(Number(e_project.value))) {
      ok = false; setError(e_project, er_project, "Project must be a valid selection.");
    }

    const recVal = e_recurring.value === "" ? null : Number(e_recurring.value);
    if (recVal != null && (Number.isNaN(recVal) || recVal < 0)) {
      ok = false; setError(e_recurring, er_recurring, "Recurring must be 0 or a positive number.");
    }
    if (recVal != null && recVal > 0) {
      if (!e_due.value) {
        ok = false; setError(e_due, er_due, "Deadline is required for recurring tasks.");
      }
    }

    if (e_start.value && !isValidYmd(e_start.value)) {
      ok = false; setError(e_start, er_start, "Start date must be YYYY-MM-DD.");
    }
    if (e_due.value && !isValidYmd(e_due.value)) {
      ok = false; setError(e_due, er_due, "Deadline must be YYYY-MM-DD.");
    }
    if (e_start.value && e_due.value && e_start.value > e_due.value) {
      ok = false;
      setError(e_start, er_start, "Start date cannot be after deadline.");
      setError(e_due, er_due, "Deadline cannot be before start date.");
    }

    return ok;
  }

  document.getElementById("btnSaveEdit").addEventListener("click", async (ev) => {
    ev.preventDefault();
    if (!editingTaskId) return;
    if (!validate()) return;

    const payload = {};
    if (e_title.value !== "") payload.title = e_title.value;
    if (e_desc.value !== "") payload.description = e_desc.value;
    if (e_priority.value !== "") payload.priority = Number(e_priority.value);
    if (e_start.value !== "") payload.start_date = e_start.value || null;
    if (e_due.value !== "") payload.deadline = e_due.value || null;
    if (e_project.value !== "") payload.project_id = Number(e_project.value);
    if (e_tag.value !== "") payload.tag = e_tag.value;
    if (e_recurring.value !== "") payload.recurring = Number(e_recurring.value);

    try {
      const res = await apiTask(`/${editingTaskId}`, { method: "PATCH", body: JSON.stringify(payload) });
      log(`PATCH /task/${editingTaskId}`, res);
      dlgEdit.close();
      showToast("Task updated successfully!", "success");
      reload();
    } catch (e) {
      log("PATCH error", String(e));
      showToast(e.message || "Failed to update task", "error");
    }
  });
}
