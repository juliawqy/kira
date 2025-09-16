/*************************************************
 * Kira Task Dashboard — API-first, modal UX
 * - Mock-friendly
 * - Update/Status modals locked to clicked task
 * - Create modal locks to clicked parent for subtasks
 * - Set Status modal = dropdown only (no quick buttons)
 * - Subtasks use .sub-badge pills (lighter, smaller)
 *************************************************/
const USE_MOCK = true;                 // set false when backend APIs go live
const API_BASE = "/api/v1";            // adjust if your backend prefix differs
const JSON_HEADERS = { "Content-Type": "application/json" };

/* ----------------------- Real Service ----------------------- */
const RealService = {
  async list({ q = "", status = "" } = {}) {
    const url = new URL(`${API_BASE}/tasks`, window.location.origin);
    if (q) url.searchParams.set("q", q);
    if (status) url.searchParams.set("status", status);
    const res = await fetch(url);
    if (!res.ok) throw new Error(`List failed: ${res.status}`);
    return res.json();
  },
  async create(payload) {
    const r = await fetch(`${API_BASE}/tasks`, { method:"POST", headers:JSON_HEADERS, body:JSON.stringify(payload) });
    if (!r.ok) throw new Error(`Create failed: ${r.status}`);
    return r.json();
  },
  async patch(id, updates) {
    const r = await fetch(`${API_BASE}/tasks/${id}`, { method:"PATCH", headers:JSON_HEADERS, body:JSON.stringify(updates) });
    if (!r.ok) throw new Error(`Update failed: ${r.status}`);
    return r.json();
  },
  async setStatus(id, status) {
    const r = await fetch(`${API_BASE}/tasks/${id}/status`, { method:"POST", headers:JSON_HEADERS, body:JSON.stringify({ status }) });
    if (!r.ok) throw new Error(`Status failed: ${r.status}`);
    return r.json();
  },
};

/* ----------------------- Mock Service ----------------------- */
const MockService = (() => {
  let seq = 1000;
  const today = new Date();
  const iso = (d) => d ? new Date(d).toISOString() : null;

  const store = [
    { id:1, title:"Prepare Q4 report", status:"To-do", priority:"High",
      start_date:null, deadline:iso(new Date(today.getFullYear(), today.getMonth(), today.getDate()+7)),
      collaborators:"julia@kira.ai, alex@kira.ai", notes:"Include churn", description:"Compile metrics & slides", parent_id:null,
      subtasks:[
        { id:2, title:"Pull revenue data", status:"In progress", priority:"Medium", deadline:null, parent_id:1, description:"BQ export", collaborators:"alex@kira.ai", notes:"partition by quarter" },
        { id:3, title:"Build charts",      status:"To-do",       priority:"Low",    deadline:null, parent_id:1, description:"Looker + Slides", collaborators:"", notes:"" },
      ]},
    { id:4, title:"Security review", status:"Blocked", priority:"Medium",
      start_date:null, deadline:null, collaborators:"", notes:"Waiting on approval", description:"Vendor risk", parent_id:null, subtasks:[]},
  ];

  function parents(){ return store; }
  function flat(){ const a=[]; for(const p of store){ a.push(p); (p.subtasks||[]).forEach(s=>a.push(s)); } return a; }
  const findParent = (id) => store.find(x=>x.id===id);
  const findAny = (id) => flat().find(x=>x.id===id);

  return {
    async list({ q = "", status = "" } = {}) {
      let out = parents().map(p => ({ ...p, subtasks:[...(p.subtasks||[])] }));
      if (q) { const Q = q.toLowerCase(); out = out.filter(t => (t.title||"").toLowerCase().includes(Q) || (t.collaborators||"").toLowerCase().includes(Q)); }
      if (status) out = out.filter(t => (t.status||"").toLowerCase() === status.toLowerCase());
      await sleep(100);
      return out;
    },
    async create(payload){
      const id = ++seq;
      const base = { id, title:payload.title, status:payload.status||"To-do", priority:payload.priority||"Medium",
        start_date:payload.start_date||null, deadline:payload.deadline||null,
        collaborators:payload.collaborators||"", notes:payload.notes||"", description:payload.description||"",
        parent_id:payload.parent_id||null, subtasks:[] };
      if (payload.parent_id){
        const par = findParent(payload.parent_id); if (!par) throw new Error("Parent not found");
        par.subtasks.push(base);
      } else store.push(base);
      await sleep(60);
      return { id };
    },
    async patch(id, updates){
      const t = findAny(Number(id)); if (!t) throw new Error("Task not found");

      // Handle re-parenting if provided
      if ("parent_id" in updates && updates.parent_id !== t.parent_id){
        // remove from old parent if it was a subtask
        for (const p of store){
          const idx = (p.subtasks||[]).findIndex(s => s.id === t.id);
          if (idx >= 0) p.subtasks.splice(idx,1);
        }
        if (updates.parent_id){
          const target = findParent(updates.parent_id);
          if (target) target.subtasks.push(t);
          t.parent_id = updates.parent_id;
        } else {
          // promote to parent
          t.parent_id = null;
          if (!store.find(p => p.id === t.id)) store.push(t);
        }
      }

      Object.assign(t, updates);
      await sleep(40);
      return { id:t.id, updated:true };
    },
    async setStatus(id, status){
      const t = findAny(Number(id)); if(!t) throw new Error("Task not found");
      t.status = status; await sleep(30); return { id:t.id, status };
    },
  };
})();
function sleep(ms){ return new Promise(r=>setTimeout(r,ms)); }
const SVC = USE_MOCK ? MockService : RealService;

/* ----------------------- DOM ----------------------- */
const $ = (id)=>document.getElementById(id);
const grid = $("dashboard");
const emptyEl = $("empty");
const detailModal = $("detailModal");
const detailTitle = $("detailTitle");
const detailBody = $("detailBody");
const detailClose = $("detailClose");
const overlay = $("modalOverlay");
const modalCreate = $("modal-create");
const modalUpdate = $("modal-update");
const modalStatus = $("modal-status");

/* Create-lock state (when adding a subtask from a parent card) */
let LOCK_CREATE_PARENT_ID = null;

/* ----------------------- Utils ----------------------- */
function escapeHtml(str){
  return String(str ?? "").replace(/[&<>"]/g, c => ({
    "&":"&amp;","<":"&lt;",">":"&gt;","\"":"&quot;"
  }[c]));
}
function chip(status){
  const map = { "to-do":"todo", "in progress":"progress", "completed":"done", "blocked":"blocked" };
  const key = (status||"").toLowerCase();
  const cls = map[key] || "todo";
  return `<span class="badge status ${cls}">${escapeHtml(status||"To-do")}</span>`;
}
function subChip(status){
  const map = { "to-do":"todo", "in progress":"progress", "completed":"done", "blocked":"blocked" };
  const key = (status||"").toLowerCase();
  const cls = map[key] || "todo";
  return `<span class="sub-badge status ${cls}">${escapeHtml(status||"To-do")}</span>`;
}
function fmt(d){ return d ? new Date(d).toLocaleDateString() : "—"; }
function setBodyModalOpen(open){ document.body.classList.toggle("modal-open", !!open); }

/* ----------------------- Render ----------------------- */
function renderDashboard(tasks){
  grid.innerHTML = "";
  if (!tasks || !tasks.length){ emptyEl.style.display = ""; return; }
  emptyEl.style.display = "none";

  for (const t of tasks){
    const card = document.createElement("article");
    card.className = "card-task";
    card.setAttribute("data-view","parent");
    card.setAttribute("data-id", String(t.id));
    card.innerHTML = `
      <div>
        <h3 class="title">${escapeHtml(t.title || "Untitled task")}</h3>
        <div class="meta">
          ${chip(t.status)}
          <span class="badge">Due: ${fmt(t.deadline)}</span>
          <span class="badge">Priority: ${escapeHtml(t.priority || "—")}</span>
          <span class="badge">#${t.id}</span>
        </div>
      </div>
      ${ renderSubtasksInline(t) }
      <div class="row-end">
        <div class="meta" style="opacity:.85">${escapeHtml(t.collaborators||"")}</div>
        <div class="actions">
          <button class="btn tiny secondary" data-open="update" data-id="${t.id}">✎</button>
          <button class="btn tiny secondary" data-open="status" data-id="${t.id}">✓</button>
          <button class="btn tiny" data-open="create" data-parent="${t.id}">＋</button>
        </div>
      </div>
    `;
    grid.appendChild(card);
  }
}

function renderSubtasksInline(parent){
  const subs = parent.subtasks || [];
  if (!subs.length) return `<div class="subtasks-inline" style="opacity:.7">No subtasks</div>`;
  return `<div class="subtasks-inline">
    ${subs.map(s => `
      <div class="sub-item" data-view="subtask" data-id="${s.id}">
        <div>
          <div class="meta"><strong>${escapeHtml(s.title)}</strong> ${subChip(s.status)}</div>
          <div class="meta">
            <span class="sub-badge">Due: ${fmt(s.deadline)}</span>
            <span class="sub-badge">Priority: ${escapeHtml(s.priority || "—")}</span>
            <span class="sub-badge">#${s.id}</span>
          </div>
        </div>
        <div class="actions">
          <button class="btn tiny secondary" data-open="update" data-id="${s.id}">✎</button>
          <button class="btn tiny secondary" data-open="status" data-id="${s.id}">✓</button>
        </div>
      </div>`).join("")}
  </div>`;
}

function openDetail(item, parentTitle){
  detailTitle.textContent = item.title || "Task details";
  detailBody.innerHTML = `
    <div class="row">
      ${parentTitle ? `<div class="kv"><strong>Parent:</strong> ${escapeHtml(parentTitle)}</div>` : ""}
      <div class="kv"><strong>ID:</strong> ${item.id}</div>
      <div class="kv"><strong>Status:</strong> ${escapeHtml(item.status||"To-do")}</div>
      <div class="kv"><strong>Priority:</strong> ${escapeHtml(item.priority||"—")}</div>
      <div class="kv"><strong>Start:</strong> ${fmt(item.start_date)}</div>
      <div class="kv"><strong>Deadline:</strong> ${fmt(item.deadline)}</div>
    </div>
    <div class="row"><div class="kv"><strong>Collaborators:</strong> ${escapeHtml(item.collaborators||"—")}</div></div>
    <div class="row"><div class="kv"><strong>Description:</strong> ${escapeHtml(item.description||"—")}</div></div>
    <div class="row"><div class="kv"><strong>Notes:</strong> ${escapeHtml(item.notes||"—")}</div></div>
  `;
  detailModal.hidden = false;
  setBodyModalOpen(true);
}

function closeDetail(){
  detailModal.hidden = true;
  setBodyModalOpen(false);
}

detailClose.addEventListener("click", closeDetail);

// Escape key
document.addEventListener("keydown",(e)=>{
  if(e.key==="Escape" && !detailModal.hidden){
    closeDetail();
  }
});

/* ----------------------- Modals ----------------------- */
function openModal(which){
  overlay.hidden = false; setBodyModalOpen(true);
  [modalCreate, modalUpdate, modalStatus].forEach(m => m.hidden = true);
  ({ create:modalCreate, update:modalUpdate, status:modalStatus }[which]).hidden = false;
}
function closeModal(){
  overlay.hidden = true; setBodyModalOpen(false);
  [modalCreate, modalUpdate, modalStatus].forEach(m => m.hidden = true);
  // also unlock Create if it was locked
  unlockCreateParent();
}
overlay.addEventListener("click", closeModal);
document.addEventListener("keydown", (e)=>{ if(e.key === "Escape") closeModal(); });
document.querySelectorAll("[data-close-modal]").forEach(b => b.addEventListener("click", closeModal));

/* ----------------------- Task lookup ----------------------- */
function findTaskById(id){
  const data = window.__TASKS || [];
  for (const p of data){
    if (p.id === id) return { item:p, parent:null };
    const s = (p.subtasks||[]).find(x=>x.id===id);
    if (s) return { item:s, parent:p };
  }
  return { item:null, parent:null };
}

/* ----------------------- Create Lock Helpers ----------------------- */
function lockCreateToParent(parentId, parentTitle){
  LOCK_CREATE_PARENT_ID = Number(parentId);
  $("isSubtask").value = "yes";
  $("isSubtask").disabled = true;

  $("parentPicker").style.display = "";
  $("parentTaskId").value = String(parentId);
  $("parentTaskId").disabled = true;
  $("parentTaskId").style.pointerEvents = "none";
  $("parentTaskId").style.opacity = "0.65";

  let pill = document.getElementById("parentInfoPill");
  if (!pill) {
    pill = document.createElement("div");
    pill.id = "parentInfoPill";
    pill.className = "pill";
    $("parentPicker").appendChild(pill);
  }
  pill.textContent = `${parentTitle || "Selected parent"} (#${parentId})`;
}
function unlockCreateParent(){
  if (LOCK_CREATE_PARENT_ID == null) return;
  LOCK_CREATE_PARENT_ID = null;
  $("isSubtask").disabled = false;
  $("parentTaskId").disabled = false;
  $("parentTaskId").style.pointerEvents = "";
  $("parentTaskId").style.opacity = "";
  const pill = document.getElementById("parentInfoPill");
  if (pill && pill.parentNode) pill.parentNode.removeChild(pill);
  $("isSubtask").value = "no";
  $("parentPicker").style.display = "none";
}

/* ----------------------- Events ----------------------- */
document.getElementById("openCreate").addEventListener("click", ()=>{
  document.getElementById("formCreate").reset();
  unlockCreateParent(); // ensure it's unlocked for top-level create
  $("isSubtask").value = "no";
  $("parentPicker").style.display = "none";
  openModal("create");
});
document.getElementById("refreshBtn").addEventListener("click", hydrate);
document.getElementById("q").addEventListener("input", hydrate);
document.getElementById("filterStatus").addEventListener("change", hydrate);

// click handling for view/update/status/create
document.addEventListener("click", (e)=>{
  const card = e.target.closest("[data-view]");
  if (card && !e.target.closest(".actions")){
    const id = Number(card.dataset.id);
    const { item, parent } = findTaskById(id);
    if (item) openDetail(item, parent ? parent.title : null);
  }

  const btn = e.target.closest("[data-open]");
  if (!btn) return;
  const which = btn.dataset.open;
  const id = Number(btn.dataset.id || btn.dataset.parent);

  if (which==="create"){
    document.getElementById("formCreate").reset();
    if (btn.dataset.parent){
      const { item: parentItem } = findTaskById(Number(btn.dataset.parent));
      lockCreateToParent(btn.dataset.parent, parentItem ? parentItem.title : "");
    } else {
      unlockCreateParent();
    }
    openModal("create");
  }

  if (which==="update"){
    const { item } = findTaskById(id);
    if (!item) return;
    $("u_taskId").value = item.id;
    $("u_taskInfo").textContent = `${item.title || "Untitled"} (#${item.id})`;
    openModal("update");
  }

  if (which==="status"){
    const { item } = findTaskById(id);
    if (!item) return;
    $("s_taskId").value = item.id;
    $("s_taskInfo").textContent = `${item.title || "Untitled"} (#${item.id})`;
    updateStatusChoices(); // preselect current status in dropdown
    openModal("status");
  }
});

/* ----------------------- Create ----------------------- */
$("formCreate").addEventListener("change",(e)=>{
  if (e.target.id==="isSubtask" && LOCK_CREATE_PARENT_ID != null){
    $("isSubtask").value = "yes";
    $("parentPicker").style.display = "";
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
  await SVC.create(payload);
  closeModal(); await hydrate();
});

/* ----------------------- Update ----------------------- */
$("formUpdate").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const id = Number($("u_taskId").value);
  if (!id) return;
  const updates = {};
  const put=(k,v)=>{ if(v && v.trim()!=="") updates[k]=v; };
  put("title",$("u_title").value);
  put("description",$("u_description").value);
  put("start_date",$("u_start").value);
  put("deadline",$("u_deadline").value);
  put("notes",$("u_notes").value);
  put("collaborators",$("u_collab").value);
  put("status",$("u_status").value);
  put("comments",$("u_comments").value);
  if($("u_priority").value) updates.priority=$("u_priority").value;
  if($("u_parentTaskId").value) updates.parent_id=Number($("u_parentTaskId").value);
  await SVC.patch(id,updates);
  closeModal(); await hydrate();
});

/* ----------------------- Status (dropdown only) ----------------------- */
function updateStatusChoices(){
  const id = Number($("s_taskId").value);
  const { item } = findTaskById(id);
  if (!item) return;

  // Full list; preselect current status
  const statuses = ["To-do", "In progress", "Completed", "Blocked"];
  const sel = $("s_status");
  sel.innerHTML = statuses.map(s => `<option ${s === (item.status || "To-do") ? "selected" : ""}>${s}</option>`).join("");
}
$("formStatus").addEventListener("submit", async (e)=>{
  e.preventDefault();
  const id=Number($("s_taskId").value);
  const status=$("s_status").value;
  await SVC.setStatus(id,status);
  closeModal(); await hydrate();
});

/* ----------------------- Hydration ----------------------- */
async function hydrate(){
  const q=($("q")?.value||"").trim();
  const status=($("filterStatus")?.value||"");
  const tasks=await SVC.list({ q,status });
  window.__TASKS=tasks;
  renderDashboard(tasks);
}
hydrate();
