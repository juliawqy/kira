/*************************************************
 * Uses MockDB from mock-data.js for now.
 * Later: swap out MockDB with API fetches inside Backend methods.
 *************************************************/

// import the mock backend (script.js and mock-data.js are in the same /api folder)
import { MockDB } from "./mock-data.js";

const API_BASE = "/api/v1"; // for future API use

/* ====================== Backend ====================== */
/* Calls the mock backend now. Later, just replace with fetch(...) calls */
const Backend = {
  async list(args) { return MockDB.list(args); },
  async create(payload) { return MockDB.create(payload); },
  async patch(id, updates) { return MockDB.patch(id, updates); },
  async setStatus(id, status) { return MockDB.setStatus(id, status); },
  async delete(id) { return MockDB.delete(id); }
};

/* ====================== DOM, State & Utils ====================== */
const $ = (id)=>document.getElementById(id);
const grid = $("dashboard");
const emptyEl = $("empty");
const detailModal = $("detailModal");
const detailTitle = $("detailTitle");
const detailBody = $("detailBody");
const overlay = $("modalOverlay");
const modalCreate = $("modal-create");
const modalUpdate = $("modal-update");
const modalStatus = $("modal-status");

let LOCK_CREATE_PARENT_ID = null;
const COLLAPSE_KEY = "kira_collapsed_parents";
let COLLAPSED = loadCollapsed();

function escapeHtml(str){
  return String(str ?? "").replace(/[&<>"]/g, c => ({ "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;" }[c]));
}
function highlightText(s, q){
  s = String(s ?? ""); if (!q) return escapeHtml(s);
  const re = new RegExp(q.replace(/[.*+?^${}()|[\]\\]/g,"\\$&"), "gi");
  let out = "", last = 0, m;
  while ((m = re.exec(s))){
    out += escapeHtml(s.slice(last, m.index));
    out += `<mark class="highlight">${escapeHtml(m[0])}</mark>`;
    last = m.index + m[0].length;
  }
  return out + escapeHtml(s.slice(last));
}
function chip(status, id){
  const map = { "to-do":"todo", "in progress":"progress", "completed":"done", "blocked":"blocked" };
  const cls = map[(status||"").toLowerCase()] || "todo";
  const safe = escapeHtml(status || "To-do");
  return `<span class="badge status ${cls}" data-open="status" data-id="${String(id)}" role="button" tabindex="0" aria-label="Change status">
            ${safe} ▾
          </span>`;
}
function subChip(status, id){
  const map = { "to-do":"todo", "in progress":"progress", "completed":"done", "blocked":"blocked" };
  const cls = map[(status||"").toLowerCase()] || "todo";
  const safe = escapeHtml(status || "To-do");
  return `<span class="sub-badge status ${cls}" data-open="status" data-id="${String(id)}" role="button" tabindex="0" aria-label="Change status">
            ${safe} ▾
          </span>`;
}
function fmt(d){ return d ? new Date(d).toLocaleDateString() : "—"; }
function toInputDate(iso){
  if (!iso) return "";
  const d = new Date(iso);
  return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,"0")}-${String(d.getDate()).padStart(2,"0")}`;
}
function setBodyModalOpen(open){ document.body.classList.toggle("modal-open", !!open); }
function loadCollapsed(){ try{ return JSON.parse(localStorage.getItem(COLLAPSE_KEY)||"{}"); }catch{ return {}; } }
function saveCollapsed(){ try{ localStorage.setItem(COLLAPSE_KEY, JSON.stringify(COLLAPSED)); }catch{} }

/* ====================== Update Prefill ====================== */
function prefillUpdateForm(item, parent){
  populateParentPickers(window.__TASKS || []);
  $("u_taskId").value = item.id;
  $("u_taskInfo").textContent = `${item.title || "Untitled"} (#${item.id})`;
  $("u_title").value        = item.title || "";
  $("u_description").value  = item.description || "";
  $("u_notes").value        = item.notes || "";
  $("u_collab").value       = item.collaborators || "";
  $("u_comments").value     = ""; // append-only
  $("u_start").value        = toInputDate(item.start_date);
  $("u_deadline").value     = toInputDate(item.deadline);
  $("u_priority").value     = item.priority || "";
  $("u_status").value       = item.status || "";
  $("u_parentTaskId").value = parent ? String(parent.id) : "";
}

/* ====================== Rendering ====================== */
function renderDashboard(tasks){
  const q = ($("q")?.value || "").trim();
  grid.innerHTML = "";
  if (!tasks || !tasks.length){ emptyEl.style.display = ""; return; }
  emptyEl.style.display = "none";

  for (const t of tasks){
    const subsCount = (t.subtasks || []).length;
    const stored = COLLAPSED[t.id];
    const isCollapsed = stored === undefined ? true : !!stored;

    const titleHtml = highlightText(t.title || "Untitled task", q);
    const assigneeHtml = highlightText(t.collaborators || "—", q);

    const card = document.createElement("article");
    card.className = "card-task";
    card.setAttribute("data-view","parent");
    card.setAttribute("data-id", String(t.id));
    card.innerHTML = `
      <div>
        <h3 class="title">${titleHtml}</h3>
        <div class="meta">
          ${chip(t.status, t.id)}
          <span class="badge">Task ID: #${t.id}</span>
          <span class="badge">Due: ${fmt(t.deadline)}</span>
          <span class="badge priority ${t.priority ? t.priority.toLowerCase() : ''}">
            Priority: ${escapeHtml(t.priority || "—")}
          </span>
          <span class="badge">Assigned to: ${assigneeHtml}</span>
          <button class="badge subtoggle" data-toggle="subs" data-id="${t.id}" aria-expanded="${!isCollapsed}">
            ${isCollapsed ? "▸" : "▾"} Subtasks (${subsCount})
          </button>
        </div>
      </div>
      <div class="subs-wrap" id="subs-${t.id}" style="${isCollapsed ? "display:none" : ""}">
        ${ renderSubtasksInline(t, q) }
      </div>
      <div class="row-end">
        <div class="meta"></div>
        <div class="actions">
          <button class="btn tiny secondary" data-open="update" data-id="${t.id}" data-tooltip="Edit">✏️</button>
          <button class="btn tiny" data-open="create" data-parent="${t.id}" data-tooltip="Add subtask">＋</button>
          <button class="btn tiny danger" data-open="delete" data-id="${t.id}" data-tooltip="Delete">🗑</button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  }
  populateParentPickers(tasks);
}

function renderSubtasksInline(parent, q){
  const subs = parent.subtasks || [];
  if (!subs.length) return `<div class="subtasks-inline" style="opacity:.7">No subtasks</div>`;
  return `<div class="subtasks-inline">
    ${subs.map(s => {
      const th = highlightText(s.title || "", q);
      const assignee = highlightText(s.collaborators || "—", q);
      return `
      <div class="sub-item" data-view="subtask" data-id="${s.id}">
        <div>
          <div class="meta"><strong>${th}</strong> ${subChip(s.status, s.id)}</div>
          <div class="meta">
            <span class="sub-badge">Subtask ID: #${s.id}</span>
            <span class="sub-badge">Due: ${fmt(s.deadline)}</span>
            <span class="sub-badge priority ${s.priority ? s.priority.toLowerCase() : ''}">
              Priority: ${escapeHtml(s.priority || "—")}
            </span>
            <span class="sub-badge">Assigned to: ${assignee}</span>
          </div>
        </div>
        <div class="actions">
          <button class="btn tiny secondary" data-open="update" data-id="${s.id}" data-tooltip="Edit">✏️</button>
          <button class="btn tiny danger" data-open="delete" data-id="${s.id}" data-tooltip="Delete">🗑</button>
        </div>
      </div>`;
    }).join("")}
  </div>`;
}

/* ====================== Detail Modal ====================== */
function openDetail(item, parentTitle){
  const q = ($("q")?.value || "").trim();
  detailTitle.innerHTML = highlightText(item.title || "Task details", q);
  detailBody.innerHTML = `
    <div class="row">
      ${parentTitle ? `<div class="kv"><strong>Parent:</strong> ${escapeHtml(parentTitle)}</div>` : ""}
      <div class="kv"><strong>ID:</strong> ${item.id}</div>
      <div class="kv"><strong>Status:</strong> ${escapeHtml(item.status||"To-do")}</div>
      <div class="kv"><strong>Priority:</strong> ${escapeHtml(item.priority||"—")}</div>
      <div class="kv"><strong>Start:</strong> ${fmt(item.start_date)}</div>
      <div class="kv"><strong>Deadline:</strong> ${fmt(item.deadline)}</div>
    </div>
    <div class="row"><div class="kv"><strong>Collaborators:</strong> ${highlightText(item.collaborators||"—", q)}</div></div>
    <div class="row"><div class="kv"><strong>Description:</strong> ${highlightText(item.description||"—", q)}</div></div>
    <div class="row"><div class="kv"><strong>Notes:</strong> ${highlightText(item.notes||"—", q)}</div></div>
  `;
  detailModal.hidden = false;
  setBodyModalOpen(true);
}
function closeDetail(){ detailModal.hidden = true; setBodyModalOpen(false); }

/* ====================== Modals ====================== */
function openModal(which){
  overlay.hidden = false; setBodyModalOpen(true);
  [modalCreate, modalUpdate, modalStatus].forEach(m => m.hidden = true);
  ({ create:modalCreate, update:modalUpdate, status:modalStatus }[which]).hidden = false;
}
function closeModal(){
  overlay.hidden = true; setBodyModalOpen(false);
  [modalCreate, modalUpdate, modalStatus].forEach(m => m.hidden = true);
  unlockCreateParent();
}
overlay.addEventListener("click", closeModal);
document.addEventListener("keydown",(e)=>{
  if (e.key==="Escape") {
    if (!detailModal.hidden) closeDetail();
    closeModal();
  }
});

/* ====================== Lookups & Parent Lock ====================== */
function findTaskById(id){
  const data = window.__TASKS || [];
  for (const p of data){
    if (p.id === id) return { item:p, parent:null };
    const s = (p.subtasks||[]).find(x=>x.id===id);
    if (s) return { item:s, parent:p };
  }
  return { item:null, parent:null };
}
function lockCreateToParent(parentId, parentTitle){
  LOCK_CREATE_PARENT_ID = Number(parentId);
  $("isSubtask").value = "yes"; $("isSubtask").disabled = true;
  $("parentPicker").style.display = ""; $("parentTaskId").value = String(parentId);
  $("parentTaskId").disabled = true; $("parentTaskId").style.pointerEvents = "none"; $("parentTaskId").style.opacity = "0.65";
  let pill = document.getElementById("parentInfoPill");
  if (!pill) { pill = document.createElement("div"); pill.id = "parentInfoPill"; pill.className = "pill"; $("parentPicker").appendChild(pill); }
  pill.textContent = `${parentTitle || "Selected parent"} (#${parentId})`;
}
function unlockCreateParent(){
  if (LOCK_CREATE_PARENT_ID == null) return;
  LOCK_CREATE_PARENT_ID = null;
  $("isSubtask").disabled = false; $("parentTaskId").disabled = false;
  $("parentTaskId").style.pointerEvents = ""; $("parentTaskId").style.opacity = "";
  const pill = document.getElementById("parentInfoPill"); if (pill?.parentNode) pill.parentNode.removeChild(pill);
  $("isSubtask").value = "no"; $("parentPicker").style.display = "none";
}
function populateParentPickers(tasks){
  const parents = Array.isArray(tasks) ? tasks : [];
  const selects = [ $("parentTaskId"), $("u_parentTaskId") ].filter(Boolean);
  for (const sel of selects){
    const current = sel.value; sel.innerHTML = "";
    if (sel.id === "u_parentTaskId") { const opt0=document.createElement("option"); opt0.value=""; opt0.textContent="(no change)"; sel.appendChild(opt0); }
    for (const p of parents){ const o=document.createElement("option"); o.value=String(p.id); o.textContent=`${p.title||"Untitled"} (#${p.id})`; sel.appendChild(o); }
    if (current && [...sel.options].some(o=>o.value===current)) sel.value=current;
  }
}

/* ====================== Events ====================== */
// header
document.getElementById("openCreate").addEventListener("click", ()=>{
  document.getElementById("formCreate").reset();
  unlockCreateParent();
  $("isSubtask").value = "no";
  $("parentPicker").style.display = "none";
  openModal("create");
});
document.getElementById("refreshBtn").addEventListener("click", hydrate);
document.getElementById("q").addEventListener("input", hydrate);
document.getElementById("filterStatus").addEventListener("change", hydrate);

// global delegated clicks
document.addEventListener("click", async (e)=>{
  if (e.target.closest("[data-close-modal]")) { closeModal(); return; }
  if (e.target.closest("[data-close-detail]")) { closeDetail(); return; }

  // A) handle explicit opens FIRST (status, update, create, delete)
  const btn = e.target.closest("[data-open]");
  if (btn) {
    const which = btn.dataset.open;
    const id = Number(btn.dataset.id || btn.dataset.parent);

    if (which==="create"){
      document.getElementById("formCreate").reset();
      if (btn.dataset.parent){
        const { item: parentItem } = findTaskById(Number(btn.dataset.parent));
        lockCreateToParent(btn.dataset.parent, parentItem ? parentItem.title : "");
      } else { unlockCreateParent(); }
      openModal("create"); return;
    }

    if (which==="update"){
      const { item, parent } = findTaskById(id);
      if (!item) return;
      prefillUpdateForm(item, parent);
      openModal("update"); return;
    }

    if (which==="status"){
      const { item } = findTaskById(id);
      if (!item) return;
      $("s_taskId").value = item.id;
      $("s_taskInfo").textContent = `${item.title || "Untitled"} (#${item.id})`;
      updateStatusChoices();
      openModal("status"); return;
    }

    if (which==="delete"){
      const { item, parent } = findTaskById(id);
      if (!item) return;
      const isParent = !parent;
      const msg = isParent
        ? `Delete parent task "${item.title}" (#${item.id})?\n\nIts subtasks will be promoted to top-level tasks.`
        : `Delete subtask "${item.title}" (#${item.id})?`;
      if (confirm(msg)) { await Backend.delete(id); await hydrate(); }
      return;
    }
  }

  // B) subtasks collapse toggle
  const toggleBtn = e.target.closest("[data-toggle='subs']");
  if (toggleBtn) {
    const pid = Number(toggleBtn.dataset.id);
    const wrap = document.getElementById(`subs-${pid}`);
    const collapsed = wrap && wrap.style.display !== "none";
    if (wrap) wrap.style.display = collapsed ? "none" : "";
    COLLAPSED[pid] = collapsed ? true : false;
    const count = wrap ? wrap.querySelectorAll(".sub-item").length : 0;
    toggleBtn.innerText = (collapsed ? "▸" : "▾") + ` Subtasks (${count})`;
    toggleBtn.setAttribute("aria-expanded", String(!collapsed));
    saveCollapsed();
    return;
  }

  // C) open detail ONLY if click wasn’t on actions or any [data-open]
  const card = e.target.closest("[data-view]");
  if (card && !e.target.closest(".actions") && !e.target.closest("[data-open]")) {
    const id = Number(card.dataset.id);
    const { item, parent } = findTaskById(id);
    if (item) openDetail(item, parent ? parent.title : null);
    return;
  }
});

// keyboard support for pills/spans with data-open
document.addEventListener("keydown", (e)=>{
  const t = e.target;
  if (!t || !(t instanceof HTMLElement)) return;
  if (!t.matches("[data-open]")) return;
  if (e.key === "Enter" || e.key === " ") {
    e.preventDefault();
    t.click();
  }
});

/* create */
$("formCreate").addEventListener("change",(e)=>{
  if (e.target.id==="isSubtask" && LOCK_CREATE_PARENT_ID != null){
    $("isSubtask").value = "yes"; $("parentPicker").style.display = "";
  } else if (e.target.id==="isSubtask"){
    $("parentPicker").style.display = e.target.value==="yes" ? "" : "none";
  }
});
$("formCreate").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const lockedParent = LOCK_CREATE_PARENT_ID != null;
  const isSub = lockedParent ? true : ($("isSubtask").value==="yes");
  const parentId = lockedParent ? LOCK_CREATE_PARENT_ID : (Number($("parentTaskId").value)||null);

  const payload = {
    title: $("c_title").value.trim(),
    description: $("c_description").value.trim()||null,
    start_date: $("c_start").value||null,
    deadline: $("c_deadline").value||null,
    notes: $("c_notes").value.trim()||null,
    collaborators: $("c_collab").value.trim()||null,
    status: $("c_status").value,
    priority: $("c_priority").value,
    parent_id: isSub ? parentId : null,
  };
  await Backend.create(payload);
  closeModal(); await hydrate();
});

/* update */
$("formUpdate").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const id = Number($("u_taskId").value); if (!id) return;
  const updates = {};
  const put=(k,v)=>{ if(v && v.trim && v.trim()!=="") updates[k]=v; else if (v && !v.trim) updates[k]=v; };
  put("title",$("u_title").value);
  put("description",$("u_description").value);
  put("start_date",$("u_start").value);
  put("deadline",$("u_deadline").value);
  put("notes",$("u_notes").value);
  put("collaborators",$("u_collab").value);
  if($("u_status").value) updates.status=$("u_status").value;
  put("comments",$("u_comments").value); // blank unless user types
  if($("u_priority").value) updates.priority=$("u_priority").value;
  if($("u_parentTaskId").value) updates.parent_id=Number($("u_parentTaskId").value);
  await Backend.patch(id,updates);
  closeModal(); await hydrate();
});

/* status */
function updateStatusChoices(){
  const id = Number($("s_taskId").value);
  const { item } = findTaskById(id);
  if (!item) return;
  const statuses = ["To-do", "In progress", "Completed", "Blocked"];
  $("s_status").innerHTML = statuses
    .map(s => `<option ${s === (item.status || "To-do") ? "selected" : ""}>${s}</option>`).join("");
}
$("formStatus").addEventListener("submit", async (e)=>{
  e.preventDefault();
  await Backend.setStatus(Number($("s_taskId").value), $("s_status").value);
  closeModal(); await hydrate();
});

/* hydration */
async function hydrate(){
  const q=($("q")?.value||"").trim();
  const status=($("filterStatus")?.value||"");
  const tasks=await Backend.list({ q,status });
  window.__TASKS=tasks;
  renderDashboard(tasks);
}
hydrate();
