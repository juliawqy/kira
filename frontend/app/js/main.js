import { apiTask, apiUser } from "./api.js";
import { USERS, setUsers, LAST_TASKS, setLastTasks, CURRENT_USER, setCurrentUser, getTasksForCurrentUser } from "./state.js";
import { renderTaskCard } from "./ui/cards.js";
import { renderCalendar, bindCalendarNav } from "./ui/calendar.js";
import { bindCreateForm } from "./ui/createForm.js";
import { bindEditDialog } from "./ui/editDialog.js";

function log(label, payload) {
  const logEl = document.getElementById("log");
  const line = `[${new Date().toLocaleTimeString()}] ${label}: ${typeof payload === "string" ? payload : JSON.stringify(payload, null, 2)}`;
  const div = document.createElement("div"); div.textContent = line; logEl.prepend(div);
}

async function loadUsers(){
  try{
    const data = await apiUser("/", { method: "GET" });
    setUsers(Array.isArray(data) ? data : (data.items || []));
    log("GET /user/", USERS);
    
    // Initialize user selection after users are loaded
    initializeUserSelection();
  }catch(e){
    setUsers([]);
    log("GET users error", String(e));
  }
}

function applyFilters() {
  const filterStatus = document.getElementById("filterStatus")?.value || "";
  const filterPriority = document.getElementById("filterPriority")?.value || "";
  const filterProject = document.getElementById("filterProject")?.value || "";
  const filterTag = document.getElementById("filterTag")?.value || "";
  const ongoingEl = document.getElementById("ongoing");
  
  // Filter ongoing tasks (non-completed) from LAST_TASKS
  const ongoingTasks = LAST_TASKS.filter(t => t.status !== "Completed");
  
  // Apply filters
  let filteredTasks = ongoingTasks;
  
  if (filterStatus) {
    filteredTasks = filteredTasks.filter(t => t.status === filterStatus);
  }
  
  if (filterPriority) {
    filteredTasks = filteredTasks.filter(t => {
      const priority = t.priority || 0;
      if (filterPriority === "high") return priority >= 8;
      if (filterPriority === "medium") return priority >= 5 && priority <= 7;
      if (filterPriority === "low") return priority >= 1 && priority <= 4;
      return true;
    });
  }
  
  if (filterProject) {
    filteredTasks = filteredTasks.filter(t => {
      const projectId = t.project_id?.toString() || "";
      return projectId === filterProject;
    });
  }
  
  if (filterTag) {
    filteredTasks = filteredTasks.filter(t => {
      const tag = t.tag?.toString() || "";
      return tag === filterTag;
    });
  }
  
  // Re-render filtered tasks
  ongoingEl.innerHTML = "";
  filteredTasks.forEach(t => ongoingEl.appendChild(renderTaskCard(t, { log, reload: () => autoReload() })));
}

function applyCalendarFilters() {
  const filterStatus = document.getElementById("calFilterStatus")?.value || "";
  const filterPriority = document.getElementById("calFilterPriority")?.value || "";
  const filterProject = document.getElementById("calFilterProject")?.value || "";
  const filterTag = document.getElementById("calFilterTag")?.value || "";
  
  // Filter tasks (non-completed) from LAST_TASKS
  const activeTasks = LAST_TASKS.filter(t => t.status !== "Completed");
  
  // Apply filters
  let filteredTasks = activeTasks;
  
  if (filterStatus) {
    filteredTasks = filteredTasks.filter(t => t.status === filterStatus);
  }
  
  if (filterPriority) {
    filteredTasks = filteredTasks.filter(t => {
      const priority = t.priority || 0;
      if (filterPriority === "high") return priority >= 8;
      if (filterPriority === "medium") return priority >= 5 && priority <= 7;
      if (filterPriority === "low") return priority >= 1 && priority <= 4;
      return true;
    });
  }
  
  if (filterProject) {
    filteredTasks = filteredTasks.filter(t => {
      const projectId = t.project_id?.toString() || "";
      return projectId === filterProject;
    });
  }
  
  if (filterTag) {
    filteredTasks = filteredTasks.filter(t => {
      const tag = t.tag?.toString() || "";
      return tag === filterTag;
    });
  }
  
  // Re-render calendar with filtered tasks
  renderCalendar(filteredTasks);
}

async function loadParents(){
  const ongoingEl = document.getElementById("ongoing");
  const completedEl = document.getElementById("completed");

  ongoingEl.innerHTML = `<div class="muted">Loading…</div>`;
  completedEl.innerHTML = `<div class="muted">Loading…</div>`;
  try{
    await loadUsers();
    
    // Get tasks for current user using API endpoint
    let userTasks = [];
    if (CURRENT_USER && CURRENT_USER.user_id) {
      const data = await apiTask(`/user/${CURRENT_USER.user_id}`, { method: "GET" });
      userTasks = Array.isArray(data) ? data : [];
      setLastTasks(userTasks); // Store for filters
    } else {
      // Fallback: load all tasks if no user selected (shouldn't happen normally)
      const data = await apiTask("/", { method: "GET" });
      userTasks = Array.isArray(data) ? data : [];
      setLastTasks(userTasks);
    }
    
    // Always render both views (they're in tabs now)
    // Render completed tasks for current user
    completedEl.innerHTML = "";
    const completedTasks = userTasks.filter(t => t.status === "Completed");
    completedTasks.forEach(t => completedEl.appendChild(renderTaskCard(t, { log, reload: () => autoReload() })));
    
    // Apply filters for ongoing tasks
    applyFilters();
    
    // Apply calendar filters
    applyCalendarFilters();
    
    log("GET /task/user/", userTasks);
  }catch(e){
    ongoingEl.innerHTML = "";
    completedEl.innerHTML = "";
    log("GET /task/ error", String(e));
    alert("Failed to load tasks: " + e.message);
  }
}

let _reloadTimer = null;
function autoReload(delay=80){ clearTimeout(_reloadTimer); _reloadTimer = setTimeout(loadParents, delay); }

// Wire tabs
function switchTab(tabName) {
  const tabList = document.getElementById("tabList");
  const tabCalendar = document.getElementById("tabCalendar");
  const contentList = document.getElementById("tabContentList");
  const contentCalendar = document.getElementById("tabContentCalendar");
  
  if (tabName === "list") {
    tabList?.classList.add("active");
    tabCalendar?.classList.remove("active");
    contentList?.classList.add("active");
    contentCalendar?.classList.remove("active");
  } else if (tabName === "calendar") {
    tabList?.classList.remove("active");
    tabCalendar?.classList.add("active");
    contentList?.classList.remove("active");
    contentCalendar?.classList.add("active");
  }
}

// Sync filters between views
function syncListFilter(filterName, value) {
  const filterEl = document.getElementById(filterName);
  if (filterEl && filterEl.value !== value) {
    filterEl.value = value;
  }
  applyFilters();
}

function syncCalendarFilter(filterName, value) {
  const filterEl = document.getElementById(filterName);
  if (filterEl && filterEl.value !== value) {
    filterEl.value = value;
  }
  applyCalendarFilters();
}

// Wire all UI elements when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  document.getElementById("tabList")?.addEventListener("click", () => switchTab("list"));
  document.getElementById("tabCalendar")?.addEventListener("click", () => switchTab("calendar"));

  // Wire calendar controls
  document.getElementById("calDateMode")?.addEventListener("change", () => document.dispatchEvent(new Event("redraw-calendar")));
  document.addEventListener("redraw-calendar", () => applyCalendarFilters());

  // Wire filter dropdowns for list view - sync to calendar
  document.getElementById("filterStatus")?.addEventListener("change", (e) => {
    syncCalendarFilter("calFilterStatus", e.target.value);
  });
  document.getElementById("filterPriority")?.addEventListener("change", (e) => {
    syncCalendarFilter("calFilterPriority", e.target.value);
  });
  document.getElementById("filterProject")?.addEventListener("change", (e) => {
    syncCalendarFilter("calFilterProject", e.target.value);
  });
  document.getElementById("filterTag")?.addEventListener("change", (e) => {
    syncCalendarFilter("calFilterTag", e.target.value);
  });

  // Wire filter dropdowns for calendar view - sync to list
  document.getElementById("calFilterStatus")?.addEventListener("change", (e) => {
    syncListFilter("filterStatus", e.target.value);
  });
  document.getElementById("calFilterPriority")?.addEventListener("change", (e) => {
    syncListFilter("filterPriority", e.target.value);
  });
  document.getElementById("calFilterProject")?.addEventListener("change", (e) => {
    syncListFilter("filterProject", e.target.value);
  });
  document.getElementById("calFilterTag")?.addEventListener("change", (e) => {
    syncListFilter("filterTag", e.target.value);
  });

  // Wire user selection buttons
  const congBtn = document.getElementById("userCong");
  const juliaBtn = document.getElementById("userJulia");
  congBtn?.addEventListener("click", () => switchUser(1));
  juliaBtn?.addEventListener("click", () => switchUser(2));

  // Wire create dialog buttons
  const btnToggleCreate = document.getElementById("btnToggleCreate");
  const btnToggleCreateFab = document.getElementById("btnToggleCreateFab");
  btnToggleCreate?.addEventListener("click", () => document.getElementById("dlgCreate")?.showModal());
  btnToggleCreateFab?.addEventListener("click", () => document.getElementById("dlgCreate")?.showModal());

  // First load
  loadParents();
});

// User selection functionality
function initializeUserSelection() {
  // Set default user (Cong) only if no user is currently selected
  if (!CURRENT_USER) {
    const defaultUser = USERS.find(u => u.user_id === 1) || USERS[0];
    if (defaultUser) {
      setCurrentUser(defaultUser);
    }
  }
  updateUserSelectionUI();
}

function updateUserSelectionUI() {
  const congBtn = document.getElementById("userCong");
  const juliaBtn = document.getElementById("userJulia");
  
  if (CURRENT_USER) {
    // Remove active class from all buttons
    congBtn?.classList.remove("active");
    juliaBtn?.classList.remove("active");
    
    // Add active class to current user button
    if (CURRENT_USER.user_id === 1) {
      congBtn?.classList.add("active");
    } else if (CURRENT_USER.user_id === 2) {
      juliaBtn?.classList.add("active");
    }
  }
}

function switchUser(userId) {
  const user = USERS.find(u => u.user_id === userId);
  if (user) {
    setCurrentUser(user);
    updateUserSelectionUI();
    // Reload tasks for the new user
    loadParents();
  }
}

bindCalendarNav();
bindCreateForm(log, () => autoReload());
bindEditDialog(log, () => autoReload());
