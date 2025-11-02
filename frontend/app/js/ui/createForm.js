import { apiTask } from "../api.js";
import { CURRENT_USER } from "../state.js";

// simple Y-M-D validation
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

export function bindCreateForm(log, reload) {
  // Grab all fields
  const c_title     = document.getElementById("c_title");
  const c_desc      = document.getElementById("c_desc");
  const c_priority  = document.getElementById("c_priority");
  const c_start     = document.getElementById("c_start");    // <input type="date" id="c_start">
  const c_due       = document.getElementById("c_due");      // <input type="date" id="c_due">
  const c_project   = document.getElementById("c_project");
  const c_parent    = document.getElementById("c_parent");
  const c_tag       = document.getElementById("c_tag");
  const c_recurring = document.getElementById("c_recurring");
  const btnCreate   = document.getElementById("btnCreate");

  // Error slots
  const e_title     = document.getElementById("c_title_err");
  const e_desc      = document.getElementById("c_desc_err");
  const e_priority  = document.getElementById("c_priority_err");
  const e_start     = document.getElementById("c_start_err");
  const e_due       = document.getElementById("c_due_err");
  const e_project   = document.getElementById("c_project_err");
  const e_parent    = document.getElementById("c_parent_err");
  const e_tag       = document.getElementById("c_tag_err");
  const e_recurring = document.getElementById("c_recurring_err");

  // Guard: if the Create form isn’t on this page yet, don’t crash
  const required = [
    ["c_title", c_title],
    ["c_priority", c_priority],
    ["c_project", c_project],
    ["c_recurring", c_recurring],
    ["btnCreate", btnCreate],
  ];
  const missing = required.filter(([_, el]) => !el).map(([id]) => id);
  if (missing.length) {
    console.error("[createForm] Missing required elements:", missing.join(", "));
    return; // Exit gracefully; nothing else to bind.
  }

  // Keep dates in logical range interactively (guarded)
  c_start?.addEventListener("change", () => {
    if (!c_due) return;
    if (c_start.value) c_due.min = c_start.value;
    else c_due.removeAttribute("min");
  });
  c_due?.addEventListener("change", () => {
    if (!c_start) return;
    if (c_due.value) c_start.max = c_due.value;
    else c_start.removeAttribute("max");
  });

  function validate() {
    let ok = true;

    // reset all errors
    [ [c_title,e_title],[c_desc,e_desc],[c_priority,e_priority],
      [c_start,e_start],[c_due,e_due],[c_project,e_project],
      [c_parent,e_parent],[c_tag,e_tag],[c_recurring,e_recurring]
    ].forEach(([i,e]) => setError(i,e,""));

    // priority
    const pb = Number(c_priority.value);
    if (Number.isNaN(pb) || pb < 1 || pb > 10) {
      ok = false; setError(c_priority, e_priority, "Priority must be a number from 1 to 10.");
    }

    // project required
    if (!c_project.value) {
      ok = false; setError(c_project, e_project, "Please select a project.");
    }

    // recurring
    const rec = Number(c_recurring.value || 0);
    if (Number.isNaN(rec) || rec < 0) {
      ok = false; setError(c_recurring, e_recurring, "Recurring must be 0 or a positive number.");
    }
    // deadline required when recurring > 0
    if (rec > 0) {
      if (!c_due?.value) {
        ok = false; setError(c_due, e_due, "Deadline is required for recurring tasks.");
      }
    }

    // start/due format
    if (c_start?.value && !isValidYmd(c_start.value)) {
      ok = false; setError(c_start, e_start, "Start date must be YYYY-MM-DD.");
    }
    if (c_due?.value && !isValidYmd(c_due.value)) {
      ok = false; setError(c_due, e_due, "Deadline must be YYYY-MM-DD.");
    }

    // logical order
    if (c_start?.value && c_due?.value && c_start.value > c_due.value) {
      ok = false;
      setError(c_start, e_start, "Start date cannot be after deadline.");
      setError(c_due, e_due, "Deadline cannot be before start date.");
    }

    return { ok, pb, rec };
  }

  btnCreate.addEventListener("click", async () => {
    const { ok, pb, rec } = validate();
    if (!ok) return;

    if (!CURRENT_USER) {
      alert("No current user set. Please select a user.");
      return;
    }

    const payload = {
      title: c_title.value || "",
      description: c_desc?.value || null,
      start_date: c_start?.value || null,
      deadline: c_due?.value || null,
      priority: Math.min(10, Math.max(1, pb)),
      status: "To-do", // default behind the scenes
      project_id: Number(c_project.value),
      parent_id: c_parent?.value === "" ? null : (c_parent ? Number(c_parent.value) : null),
      tag: c_tag?.value || null,
      recurring: rec,
      creator_id: CURRENT_USER.user_id
    };

    try {
      const res = await apiTask("/", { method: "POST", body: JSON.stringify(payload) });
      log("POST /task/", res);

      // reset form
      c_title.value = "";
      if (c_desc) c_desc.value = "";
      if (c_start) { c_start.value = ""; c_start.removeAttribute("max"); }
      if (c_due)   { c_due.value = "";   c_due.removeAttribute("min"); }
      c_project.value = "";
      if (c_parent) c_parent.value = "";
      if (c_tag) c_tag.value = "";
      c_priority.value = "5";
      c_recurring.value = "0";

      // Close the dialog after successful creation
      const dlgCreate = document.getElementById("dlgCreate");
      if (dlgCreate) {
        dlgCreate.close();
      }

      reload();
    } catch (e) {
      log("Create error", String(e));
      alert(e.message);
    }
  });
}
