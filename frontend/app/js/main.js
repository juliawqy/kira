import { apiTask, apiUser } from "./api.js";
import { USERS, setUsers, LAST_TASKS, setLastTasks, CURRENT_USER, setCurrentUser, getTasksForCurrentUser, isCurrentUserStaff, isCurrentUserManager, isCurrentUserDirector, isCurrentUserManagerOrDirector, CAL_MONTH, setCalMonth, addMonths, showToast } from "./state.js";
import { renderTaskCard } from "./ui/cards.js";
import { renderCalendar, bindCalendarNav } from "./ui/calendar.js";
import { bindCreateForm } from "./ui/createForm.js";
import { bindEditDialog } from "./ui/editDialog.js";
import { renderTimeline } from "./ui/timeline.js";
import { renderGantt } from "./ui/gantt.js";

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
  renderCalendar(filteredTasks, { log, reload: () => autoReload() });
}

function updateTeamProjectFilter(userTasks) {
  const projectSelect = document.getElementById("teamCalFilterProject");
  if (!projectSelect) return;
  
  // Extract unique project IDs from user's tasks
  const userProjectIds = new Set();
  userTasks.forEach(task => {
    if (task.project_id) {
      userProjectIds.add(task.project_id.toString());
    }
    // Also check subtasks
    if (task.subTasks && Array.isArray(task.subTasks)) {
      task.subTasks.forEach(subtask => {
        if (subtask.project_id) {
          userProjectIds.add(subtask.project_id.toString());
        }
      });
    }
  });
  
  // Get all option elements
  const options = Array.from(projectSelect.options);
  const currentValue = projectSelect.value;
  
  // Filter and re-populate options
  projectSelect.innerHTML = "";
  let validCurrentValue = null;
  
  options.forEach(option => {
    const projectId = option.value;
    if (userProjectIds.has(projectId)) {
      const newOption = document.createElement("option");
      newOption.value = projectId;
      newOption.textContent = option.textContent;
      if (option.selected || projectId === currentValue) {
        newOption.selected = true;
        validCurrentValue = projectId;
      }
      projectSelect.appendChild(newOption);
    }
  });
  
  // If current selection is invalid, select first available
  if (!validCurrentValue && projectSelect.options.length > 0) {
    projectSelect.options[0].selected = true;
  }
  
  // If no projects available, show message
  if (projectSelect.options.length === 0) {
    const noProjectsOption = document.createElement("option");
    noProjectsOption.value = "";
    noProjectsOption.textContent = "No projects available";
    noProjectsOption.disabled = true;
    projectSelect.appendChild(noProjectsOption);
  }
}

async function renderTeamCalendar() {
  const teamCalendarEl = document.getElementById("teamCalendar");
  const teamCalTitle = document.getElementById("teamCalTitle");
  const mode = document.getElementById("teamCalDateMode")?.value || "due";
  const filterProject = document.getElementById("teamCalFilterProject")?.value || "1";
  const filterStatus = document.getElementById("teamCalFilterStatus")?.value || "";
  const filterPriority = document.getElementById("teamCalFilterPriority")?.value || "";
  const filterTag = document.getElementById("teamCalFilterTag")?.value || "";
  
  if (!teamCalendarEl || !isCurrentUserStaff()) return;
  
  // Don't fetch if no valid project selected
  if (!filterProject) {
    teamCalendarEl.innerHTML = `<div class="muted">No project selected.</div>`;
    return;
  }
  
  teamCalendarEl.innerHTML = `<div class="muted">Loading…</div>`;
  
  try {
    // Fetch all tasks for the selected project (includes all team members' tasks)
    const projectTasks = await apiTask(`/project/${filterProject}`, { method: "GET" });
    log(`GET /task/project/${filterProject}`, projectTasks);
    
    // Apply filters
    let filteredTasks = projectTasks || [];
    
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
    
    if (filterTag) {
      filteredTasks = filteredTasks.filter(t => {
        const tag = t.tag?.toString() || "";
        return tag === filterTag;
      });
    }
    
    // Render calendar with filtered tasks
    renderCalendar(filteredTasks, { 
      log, 
      reload: () => renderTeamCalendar(),
      targetCalendarId: "teamCalendar",
      targetTitleId: "teamCalTitle",
      dateModeSelector: "#teamCalDateMode"
    });
    
  } catch (e) {
    teamCalendarEl.innerHTML = `<div class="muted">Error loading team schedule.</div>`;
    log("Team calendar error", String(e));
  }
}

async function renderTimelineView() {
  const timelineEl = document.getElementById("timeline");
  if (!timelineEl || !isCurrentUserManagerOrDirector()) return;
  
  timelineEl.innerHTML = `<div class="muted">Loading…</div>`;
  
  try {
    const filterProject = document.getElementById("timelineFilterProject")?.value || "";
    const sortBy = document.getElementById("timelineSortBy")?.value || "";
    
    // Get all tasks (already loaded in LAST_TASKS for managers/directors)
    let filteredTasks = LAST_TASKS || [];
    
    // Apply project filter
    if (filterProject) {
      filteredTasks = filteredTasks.filter(t => {
        const projectId = t.project_id?.toString() || "";
        return projectId === filterProject;
      });
    }
    
    // Apply sorting
    if (sortBy === "status") {
      const statusOrder = { "To-do": 1, "In-progress": 2, "Blocked": 3, "Completed": 4 };
      filteredTasks.sort((a, b) => {
        const aStatus = statusOrder[a.status] || 999;
        const bStatus = statusOrder[b.status] || 999;
        return aStatus - bStatus;
      });
    } else if (sortBy === "priority") {
      filteredTasks.sort((a, b) => {
        const aPriority = a.priority || 0;
        const bPriority = b.priority || 0;
        return bPriority - aPriority; // Higher priority first
      });
    }
    
    // Render timeline with filtered and sorted tasks
    renderTimeline(filteredTasks, { log, reload: () => autoReload() });
    
  } catch (e) {
    timelineEl.innerHTML = `<div class="muted">Error loading timeline.</div>`;
    log("Timeline error", String(e));
  }
}

async function renderGanttView() {
  const ganttEl = document.getElementById("timelineGantt");
  if (!ganttEl || !isCurrentUserManagerOrDirector()) return;
  
  ganttEl.innerHTML = `<div class="muted">Loading…</div>`;
  
  try {
    const filterProject = document.getElementById("ganttFilterProject")?.value || "";
    const filterStatus = document.getElementById("ganttFilterStatus")?.value || "";
    const filterPriority = document.getElementById("ganttFilterPriority")?.value || "";
    
    // Get all tasks (already loaded in LAST_TASKS for managers/directors)
    let filteredTasks = LAST_TASKS || [];
    
    // Apply filters
    if (filterProject) {
      filteredTasks = filteredTasks.filter(t => {
        const projectId = t.project_id?.toString() || "";
        return projectId === filterProject;
      });
    }
    
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
    
    // Render gantt with filtered tasks
    renderGantt(filteredTasks, { log, reload: () => autoReload() });
    
  } catch (e) {
    ganttEl.innerHTML = `<div class="muted">Error loading gantt.</div>`;
    log("Gantt error", String(e));
  }
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
      // For managers, load tasks from their managed projects
      if (isCurrentUserManager() && !isCurrentUserDirector()) {
        const data = await apiTask(`/manager/${CURRENT_USER.user_id}`, { method: "GET" });
        userTasks = Array.isArray(data) ? data : [];
        setLastTasks(userTasks);
      } else if (isCurrentUserDirector()) {
        // For directors, load tasks from their managed departments
        const data = await apiTask(`/director/${CURRENT_USER.user_id}`, { method: "GET" });
        userTasks = Array.isArray(data) ? data : [];
        setLastTasks(userTasks);
      } else {
        // For staff, load only their assigned tasks
        const data = await apiTask(`/user/${CURRENT_USER.user_id}`, { method: "GET" });
        userTasks = Array.isArray(data) ? data : [];
        setLastTasks(userTasks);
      }
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
    
    // Apply team calendar filters if staff user
    if (isCurrentUserStaff()) {
      updateTeamProjectFilter(userTasks);
      renderTeamCalendar();
    }
    
    // Apply timeline and gantt views if manager/director
    if (isCurrentUserManagerOrDirector()) {
      renderTimelineView();
      renderGanttView();
    }
    
    log("GET /task/user/", userTasks);
  }catch(e){
    ongoingEl.innerHTML = "";
    completedEl.innerHTML = "";
    log("GET /task/ error", String(e));
    showToast("Failed to load tasks", "error");
  }
}

let _reloadTimer = null;
function autoReload(delay=80){ clearTimeout(_reloadTimer); _reloadTimer = setTimeout(loadParents, delay); }

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
  
  // Show/hide staff-only tab
  const staffOnlyTab = document.getElementById("tabTeamSchedule");
  if (staffOnlyTab && isCurrentUserStaff()) {
    staffOnlyTab.style.display = "block";
  }
  
  // Show/hide manager-only tab
  const managerOnlyTab = document.getElementById("tabTimeline");
  if (managerOnlyTab && isCurrentUserManagerOrDirector()) {
    managerOnlyTab.style.display = "block";
  }
}

function updateUserSelectionUI() {
  const congBtn = document.getElementById("userCong");
  const juliaBtn = document.getElementById("userJulia");
  const managerBtn = document.getElementById("userManager");
  const directorBtn = document.getElementById("userDirector");
  
  if (CURRENT_USER) {
    // Remove active class from all buttons
    congBtn?.classList.remove("active");
    juliaBtn?.classList.remove("active");
    managerBtn?.classList.remove("active");
    directorBtn?.classList.remove("active");
    
    // Add active class to current user button
    if (CURRENT_USER.user_id === 1) {
      congBtn?.classList.add("active");
    } else if (CURRENT_USER.user_id === 2) {
      juliaBtn?.classList.add("active");
    } else if (CURRENT_USER.user_id === 3) {
      managerBtn?.classList.add("active");
    } else if (CURRENT_USER.user_id === 4) {
      directorBtn?.classList.add("active");
    }
    
    // Show/hide staff-only tab
    const staffOnlyTab = document.getElementById("tabTeamSchedule");
    if (staffOnlyTab) {
      staffOnlyTab.style.display = isCurrentUserStaff() ? "block" : "none";
    }
    
    // Show/hide manager-only tab
    const managerOnlyTab = document.getElementById("tabTimeline");
    if (managerOnlyTab) {
      managerOnlyTab.style.display = isCurrentUserManagerOrDirector() ? "block" : "none";
    }
    
    // Auto-switch to List view if current tab is not accessible
    const activeTab = document.querySelector(".tab-btn.active");
    if (activeTab) {
      const tabName = activeTab.getAttribute("data-tab");
      if (tabName === "teamSchedule" && !isCurrentUserStaff()) {
        switchTab("list");
      } else if (tabName === "timeline" && !isCurrentUserManagerOrDirector()) {
        switchTab("list");
      }
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

// Wire tabs
function switchTab(tabName) {
  const tabList = document.getElementById("tabList");
  const tabCalendar = document.getElementById("tabCalendar");
  const tabTeamSchedule = document.getElementById("tabTeamSchedule");
  const tabTimeline = document.getElementById("tabTimeline");
  const contentList = document.getElementById("tabContentList");
  const contentCalendar = document.getElementById("tabContentCalendar");
  const contentTeamSchedule = document.getElementById("tabContentTeamSchedule");
  const contentTimeline = document.getElementById("tabContentTimeline");
  
  // Remove active class from all tabs and content
  [tabList, tabCalendar, tabTeamSchedule, tabTimeline].forEach(tab => tab?.classList.remove("active"));
  [contentList, contentCalendar, contentTeamSchedule, contentTimeline].forEach(content => content?.classList.remove("active"));
  
  if (tabName === "list") {
    tabList?.classList.add("active");
    contentList?.classList.add("active");
  } else if (tabName === "calendar") {
    tabCalendar?.classList.add("active");
    contentCalendar?.classList.add("active");
  } else if (tabName === "teamSchedule") {
    tabTeamSchedule?.classList.add("active");
    contentTeamSchedule?.classList.add("active");
  } else if (tabName === "timeline") {
    tabTimeline?.classList.add("active");
    contentTimeline?.classList.add("active");
    // Render timeline view when switching to timeline tab
    renderTimelineView();
  }
}

// Wire timeline sub-tabs
function switchTimelineSubTab(subTabName) {
  const timelineTabList = document.getElementById("timelineTabList");
  const timelineTabGantt = document.getElementById("timelineTabGantt");
  const subContentList = document.getElementById("timelineSubContentList");
  const subContentGantt = document.getElementById("timelineSubContentGantt");
  
  // Remove active class from all timeline sub-tabs
  [timelineTabList, timelineTabGantt].forEach(tab => tab?.classList.remove("active"));
  [subContentList, subContentGantt].forEach(content => content?.classList.remove("active"));
  
  if (subTabName === "list") {
    timelineTabList?.classList.add("active");
    subContentList?.classList.add("active");
    renderTimelineView();
  } else if (subTabName === "gantt") {
    timelineTabGantt?.classList.add("active");
    subContentGantt?.classList.add("active");
    renderGanttView();
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
  document.getElementById("tabTeamSchedule")?.addEventListener("click", () => switchTab("teamSchedule"));
  document.getElementById("tabTimeline")?.addEventListener("click", () => switchTab("timeline"));

  // Wire timeline sub-tabs
  document.getElementById("timelineTabList")?.addEventListener("click", () => switchTimelineSubTab("list"));
  document.getElementById("timelineTabGantt")?.addEventListener("click", () => switchTimelineSubTab("gantt"));

  // Wire calendar controls
  document.getElementById("calDateMode")?.addEventListener("change", () => document.dispatchEvent(new Event("redraw-calendar")));
  document.addEventListener("redraw-calendar", () => applyCalendarFilters());

  // Wire filter dropdowns for list view - sync to calendar
  document.getElementById("filterStatus")?.addEventListener("change", (e) => {
    syncListFilter("filterStatus", e.target.value);
    syncCalendarFilter("calFilterStatus", e.target.value);
  });
  document.getElementById("filterPriority")?.addEventListener("change", (e) => {
    syncListFilter("filterPriority", e.target.value);
    syncCalendarFilter("calFilterPriority", e.target.value);
  });
  document.getElementById("filterProject")?.addEventListener("change", (e) => {
    syncListFilter("filterProject", e.target.value);
    syncCalendarFilter("calFilterProject", e.target.value);
  });
  document.getElementById("filterTag")?.addEventListener("change", (e) => {
    syncListFilter("filterTag", e.target.value);
    syncCalendarFilter("calFilterTag", e.target.value);
  });

  // Wire filter dropdowns for calendar view - sync to list
  document.getElementById("calFilterStatus")?.addEventListener("change", (e) => {
    syncListFilter("filterStatus", e.target.value);
    syncCalendarFilter("calFilterStatus", e.target.value);
  });
  document.getElementById("calFilterPriority")?.addEventListener("change", (e) => {
    syncListFilter("filterPriority", e.target.value);
    syncCalendarFilter("calFilterPriority", e.target.value);
  });
  document.getElementById("calFilterProject")?.addEventListener("change", (e) => {
    syncListFilter("filterProject", e.target.value);
    syncCalendarFilter("calFilterProject", e.target.value);
  });
  document.getElementById("calFilterTag")?.addEventListener("change", (e) => {
    syncListFilter("filterTag", e.target.value);
    syncCalendarFilter("calFilterTag", e.target.value);
  });

  // Wire user selection buttons
  const congBtn = document.getElementById("userCong");
  const juliaBtn = document.getElementById("userJulia");
  const managerBtn = document.getElementById("userManager");
  const directorBtn = document.getElementById("userDirector");
  congBtn?.addEventListener("click", () => switchUser(1));
  juliaBtn?.addEventListener("click", () => switchUser(2));
  managerBtn?.addEventListener("click", () => switchUser(3));
  directorBtn?.addEventListener("click", () => switchUser(4));

  // Wire team calendar navigation
  document.getElementById("teamCalPrev")?.addEventListener("click", () => {
    setCalMonth(addMonths(CAL_MONTH, -1));
    renderTeamCalendar();
  });
  document.getElementById("teamCalNext")?.addEventListener("click", () => {
    setCalMonth(addMonths(CAL_MONTH, +1));
    renderTeamCalendar();
  });
  document.getElementById("teamCalDateMode")?.addEventListener("change", () => renderTeamCalendar());
  document.getElementById("teamCalFilterStatus")?.addEventListener("change", () => renderTeamCalendar());
  document.getElementById("teamCalFilterPriority")?.addEventListener("change", () => renderTeamCalendar());
  document.getElementById("teamCalFilterProject")?.addEventListener("change", () => renderTeamCalendar());
  document.getElementById("teamCalFilterTag")?.addEventListener("change", () => renderTeamCalendar());

  // Wire timeline filters and sort
  document.getElementById("timelineFilterProject")?.addEventListener("change", () => renderTimelineView());
  document.getElementById("timelineSortBy")?.addEventListener("change", () => renderTimelineView());

  // Wire gantt filters
  document.getElementById("ganttFilterProject")?.addEventListener("change", () => renderGanttView());
  document.getElementById("ganttFilterStatus")?.addEventListener("change", () => renderGanttView());
  document.getElementById("ganttFilterPriority")?.addEventListener("change", () => renderGanttView());

  // Wire create dialog buttons
  const btnToggleCreate = document.getElementById("btnToggleCreate");
  const btnToggleCreateFab = document.getElementById("btnToggleCreateFab");
  btnToggleCreate?.addEventListener("click", () => document.getElementById("dlgCreate")?.showModal());
  btnToggleCreateFab?.addEventListener("click", () => document.getElementById("dlgCreate")?.showModal());

  // Initialize dialogs
bindCalendarNav();
bindCreateForm(log, () => autoReload());
bindEditDialog(log, () => autoReload());

// First load
loadParents();
});
