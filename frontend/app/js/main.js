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
  const ongoingEl = document.getElementById("ongoing");
  
  // Get tasks for current user, then filter ongoing tasks (non-completed)
  const userTasks = getTasksForCurrentUser();
  const ongoingTasks = userTasks.filter(t => t.status !== "Completed");
  
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
  
  // Re-render filtered tasks
  ongoingEl.innerHTML = "";
  filteredTasks.forEach(t => ongoingEl.appendChild(renderTaskCard(t, { log, reload: () => autoReload() })));
}

async function loadParents(){
  const ongoingPanel = document.getElementById("ongoingPanel");
  const ongoingEl = document.getElementById("ongoing");
  const completedPanel = document.getElementById("completedPanel");
  const completedEl = document.getElementById("completed");
  const calendarPanel = document.getElementById("calendarPanel");
  const viewCalendar = document.getElementById("viewCalendar");
  const viewList = document.getElementById("viewList");

  ongoingEl.innerHTML = `<div class="muted">Loading…</div>`;
  completedEl.innerHTML = `<div class="muted">Loading…</div>`;
  try{
    await loadUsers();
    const data = await apiTask("/", { method: "GET" });
    setLastTasks(Array.isArray(data) ? data : []);
    
    const showCalendar = viewCalendar?.checked;
    const showList = viewList?.checked;
    
    // Handle calendar view
    if (showCalendar) {
      renderCalendar(LAST_TASKS);
      calendarPanel.classList.remove("sr");
    } else {
      calendarPanel.classList.add("sr");
    }
    
    // Handle list view
    if (showList) {
      // Render completed tasks for current user
      completedEl.innerHTML = "";
      const userTasks = getTasksForCurrentUser();
      const completedTasks = userTasks.filter(t => t.status === "Completed");
      completedTasks.forEach(t => completedEl.appendChild(renderTaskCard(t, { log, reload: () => autoReload() })));
      
      // Apply filters for ongoing tasks
      applyFilters();
      
      ongoingPanel.classList.remove("sr");
      completedPanel.classList.remove("sr");
    } else {
      ongoingPanel.classList.add("sr");
      completedPanel.classList.add("sr");
    }
    
    log("GET /task/", data);
  }catch(e){
    ongoingEl.innerHTML = "";
    completedEl.innerHTML = "";
    log("GET /task/ error", String(e));
    alert("Failed to load tasks: " + e.message);
  }
}

let _reloadTimer = null;
function autoReload(delay=80){ clearTimeout(_reloadTimer); _reloadTimer = setTimeout(loadParents, delay); }

// Wire global UI
document.getElementById("viewCalendar")?.addEventListener("change", loadParents);
document.getElementById("viewList")?.addEventListener("change", loadParents);
document.getElementById("calDateMode").addEventListener("change", () => document.dispatchEvent(new Event("redraw-calendar")));
document.addEventListener("redraw-calendar", () => renderCalendar(LAST_TASKS));

// Wire filter dropdowns
document.getElementById("filterStatus")?.addEventListener("change", applyFilters);
document.getElementById("filterPriority")?.addEventListener("change", applyFilters);
document.getElementById("filterProject")?.addEventListener("change", applyFilters);

bindCalendarNav();
bindCreateForm(log, () => autoReload());
bindEditDialog(log, () => autoReload());

// Open create dialog
const dlgCreate = document.getElementById("dlgCreate");
const btnToggleCreate = document.getElementById("btnToggleCreate");
const btnToggleCreateFab = document.getElementById("btnToggleCreateFab");

function openCreateDialog() {
  dlgCreate.showModal();
}

btnToggleCreate?.addEventListener("click", openCreateDialog);
btnToggleCreateFab?.addEventListener("click", openCreateDialog);

// User selection functionality
function initializeUserSelection() {
  // Set default user (Cong)
  const defaultUser = USERS.find(u => u.user_id === 1) || USERS[0];
  if (defaultUser) {
    setCurrentUser(defaultUser);
    updateUserSelectionUI();
  }
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

// Wire user selection buttons
document.getElementById("userCong")?.addEventListener("click", () => switchUser(1));
document.getElementById("userJulia")?.addEventListener("click", () => switchUser(2));

// First load
loadParents();
