import { apiTask, apiUser } from "./api.js";
import { USERS, setUsers, LAST_TASKS, setLastTasks, CURRENT_USER, setCurrentUser, getTasksForCurrentUser, isCurrentUserStaff, isCurrentUserManager, isCurrentUserDirector, isCurrentUserManagerOrDirector, CAL_MONTH, setCalMonth, addMonths, showToast } from "./state.js";
import { renderTaskCard } from "./ui/cards.js";
import { renderCalendar, bindCalendarNav } from "./ui/calendar.js";
import { bindCreateForm } from "./ui/createForm.js";
import { bindEditDialog } from "./ui/editDialog.js";
import { renderTimeline } from "./ui/timeline.js";
import { renderGantt } from "./ui/gantt.js";
import { renderTeamManagement } from "./ui/team-management.js";
import { bindReminderSettings, resetReminderSettings } from "./ui/reminderSettings.js";
import { resetNotificationTracking } from "./ui/taskNotifications.js";
import { bindReportExport } from "./ui/reportExport.js";
import { checkAndSendNotifications } from "./ui/taskNotifications.js";

// Demo user IDs - used for presentation demo
const DEMO_USER_IDS = {
  STAFF1: 15,    // Aisha Rahman (Account Manager - Overdue Task)
  STAFF2: 571,   // Aaron Koh (IT Member - Upcoming Task)
  MANAGER1: 10,  // Alice Tan (Sales Manager - Recurring Task)
  MANAGER2: 516, // Ivan Lee (Finance Manager)
  DIRECTOR1: 3,  // Derek Tan (Sales Director)
  DIRECTOR2: 7   // Sally Loh (HR Director)
};

// Project ID to name mapping (from seeded data)
const PROJECT_NAMES = {
  1: "Sales Automation Tool",
  2: "Consulting CRM System",
  3: "Software Solutions Development",
  4: "Enterprise Operations Dashboard",
  5: "HR Management Platform",
  6: "Financial Analytics Suite",
  7: "IT Infrastructure Upgrade",
  8: "Client Acquisition Campaign",
  9: "Market Expansion Strategy",
  10: "Sales Training Program",
  11: "Product Launch Event",
  12: "Customer Retention Initiative",
  13: "Budget Planning Tool",
  14: "Expense Tracking System",
  15: "Payroll Automation",
  16: "Financial Reporting Dashboard",
  17: "Audit Compliance System"
};

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

// Extract unique project IDs from tasks (including subtasks)
function extractProjectIdsFromTasks(tasks) {
  const projectIds = new Set();
  tasks.forEach(task => {
    if (task.project_id) {
      projectIds.add(task.project_id);
    }
    // Also check subtasks
    if (task.subTasks && Array.isArray(task.subTasks)) {
      task.subTasks.forEach(subtask => {
        if (subtask.project_id) {
          projectIds.add(subtask.project_id);
        }
      });
    }
  });
  return Array.from(projectIds).sort((a, b) => a - b);
}

// Extract unique tags from tasks (including subtasks)
function extractTagsFromTasks(tasks) {
  const tags = new Set();
  tasks.forEach(task => {
    if (task.tag && task.tag.trim() !== "") {
      tags.add(task.tag.trim());
    }
    // Also check subtasks
    if (task.subTasks && Array.isArray(task.subTasks)) {
      task.subTasks.forEach(subtask => {
        if (subtask.tag && subtask.tag.trim() !== "") {
          tags.add(subtask.tag.trim());
        }
      });
    }
  });
  return Array.from(tags).sort(); // Sort alphabetically
}

// Update a single project filter dropdown
function updateProjectFilterDropdown(selectId, projectIds, includeAllOption = true, defaultSelectedId = null) {
  const select = document.getElementById(selectId);
  if (!select) return;
  
  const currentValue = select.value;
  select.innerHTML = "";
  
  // Add "All Projects" option if needed
  if (includeAllOption) {
    const allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = "All Projects";
    select.appendChild(allOption);
  }
  
  // Add project options
  let validCurrentValue = null;
  projectIds.forEach(projectId => {
    const option = document.createElement("option");
    option.value = projectId.toString();
    const projectName = PROJECT_NAMES[projectId] || `Project ${projectId}`;
    option.textContent = `${projectName} (${projectId})`;
    
    // Preserve current selection or use default
    if (defaultSelectedId && projectId === defaultSelectedId) {
      option.selected = true;
      validCurrentValue = projectId.toString();
    } else if (currentValue === projectId.toString()) {
      option.selected = true;
      validCurrentValue = projectId.toString();
    }
    
    select.appendChild(option);
  });
  
  // If current selection is invalid, select first available (or "All Projects")
  if (!validCurrentValue && select.options.length > 0) {
    select.options[0].selected = true;
  }
  
  // If no projects available, show message
  if (projectIds.length === 0) {
    const noProjectsOption = document.createElement("option");
    noProjectsOption.value = "";
    noProjectsOption.textContent = "No projects available";
    noProjectsOption.disabled = true;
    select.appendChild(noProjectsOption);
  }
}

// Update a single tag filter dropdown
function updateTagFilterDropdown(selectId, tags, includeAllOption = true) {
  const select = document.getElementById(selectId);
  if (!select) return;
  
  const currentValue = select.value;
  select.innerHTML = "";
  
  // Add "All Tags" option if needed
  if (includeAllOption) {
    const allOption = document.createElement("option");
    allOption.value = "";
    allOption.textContent = "All Tags";
    select.appendChild(allOption);
  }
  
  // Add tag options
  let validCurrentValue = null;
  tags.forEach(tag => {
    const option = document.createElement("option");
    option.value = tag;
    option.textContent = tag;
    
    // Preserve current selection
    if (currentValue === tag) {
      option.selected = true;
      validCurrentValue = tag;
    }
    
    select.appendChild(option);
  });
  
  // If current selection is invalid, select first available (or "All Tags")
  if (!validCurrentValue && select.options.length > 0) {
    select.options[0].selected = true;
  }
  
  // If no tags available, show message
  if (tags.length === 0 && includeAllOption) {
    // Keep "All Tags" option, no additional message needed
  } else if (tags.length === 0 && !includeAllOption) {
    const noTagsOption = document.createElement("option");
    noTagsOption.value = "";
    noTagsOption.textContent = "No tags available";
    noTagsOption.disabled = true;
    select.appendChild(noTagsOption);
  }
}

// Update all project filters based on user's tasks
function updateAllProjectFilters(userTasks) {
  const projectIds = extractProjectIdsFromTasks(userTasks);
  
  // Update all filter dropdowns
  updateProjectFilterDropdown("filterProject", projectIds, true);
  updateProjectFilterDropdown("calFilterProject", projectIds, true);
  updateProjectFilterDropdown("timelineFilterProject", projectIds, true);
  updateProjectFilterDropdown("ganttFilterProject", projectIds, true);
  
  // Team calendar filter (no "All Projects" option, defaults to first project)
  const teamProjectIds = projectIds.length > 0 ? projectIds : [];
  updateProjectFilterDropdown("teamCalFilterProject", teamProjectIds, false, teamProjectIds[0] || null);
  
  // Update create form project dropdown - restrict to user's projects only
  const cProjectSelect = document.getElementById("c_project");
  if (cProjectSelect) {
    cProjectSelect.innerHTML = "";
    const placeholder = document.createElement("option");
    placeholder.value = "";
    placeholder.disabled = true;
    placeholder.selected = true;
    placeholder.textContent = projectIds.length > 0 ? "Select a project" : "No projects available";
    cProjectSelect.appendChild(placeholder);
    
    if (projectIds.length > 0) {
      projectIds.forEach(projectId => {
        const option = document.createElement("option");
        option.value = projectId.toString();
        const projectName = PROJECT_NAMES[projectId] || `Project ${projectId}`;
        option.textContent = `${projectName} (${projectId})`;
        cProjectSelect.appendChild(option);
      });
    }
  }
  
  // For edit form, show all projects (so users can change to any project when editing)
  // This ensures existing tasks can be edited even if the user no longer has tasks in that project
  const allProjectIds = Object.keys(PROJECT_NAMES).map(id => parseInt(id)).sort((a, b) => a - b);
  const eProjectSelect = document.getElementById("e_project");
  if (eProjectSelect) {
    // Don't clear if already populated (during edit), just ensure all options exist
    const existingValue = eProjectSelect.value;
    const existingOptions = Array.from(eProjectSelect.options).map(opt => opt.value);
    allProjectIds.forEach(projectId => {
      const projectIdStr = projectId.toString();
      if (!existingOptions.includes(projectIdStr)) {
        const option = document.createElement("option");
        option.value = projectIdStr;
        const projectName = PROJECT_NAMES[projectId] || `Project ${projectId}`;
        option.textContent = `${projectName} (${projectId})`;
        eProjectSelect.appendChild(option);
      }
    });
    // Restore selection if it was set
    if (existingValue) {
      eProjectSelect.value = existingValue;
    }
  }
}

// Update all tag filters based on user's tasks
function updateAllTagFilters(userTasks) {
  const tags = extractTagsFromTasks(userTasks);
  
  // Update all tag filter dropdowns
  updateTagFilterDropdown("filterTag", tags, true);
  updateTagFilterDropdown("calFilterTag", tags, true);
  updateTagFilterDropdown("teamCalFilterTag", tags, true);
}

function updateTeamProjectFilter(userTasks) {
  // This function is now a wrapper for the new updateAllProjectFilters
  // Kept for backward compatibility
  const projectIds = extractProjectIdsFromTasks(userTasks);
  updateProjectFilterDropdown("teamCalFilterProject", projectIds, false, projectIds[0] || null);
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

async function renderTeamManagementView() {
  const teamMgmtEl = document.getElementById("teamManagement");
  if (!teamMgmtEl || !isCurrentUserManagerOrDirector()) return;
  
  teamMgmtEl.innerHTML = `<div class="muted">Loading…</div>`;
  
  try {
    // Fetch team tasks based on user role
    let data;
    if (isCurrentUserManager() && !isCurrentUserDirector()) {
      // Manager: get tasks from teams they manage
      data = await apiTask(`/manager/${CURRENT_USER.user_id}`, { method: "GET" });
      log("GET manager team-management tasks", data);
    } else if (isCurrentUserDirector()) {
      // Director: get tasks from departments they manage
      data = await apiTask(`/director/${CURRENT_USER.user_id}`, { method: "GET" });
      log("GET director team-management tasks", data);
    } else {
      log("User is neither manager nor director");
      teamMgmtEl.innerHTML = `<div class="muted">Access denied.</div>`;
      return;
    }
    
    // Pass the dict directly to renderTeamManagement (now async)
    const container = await renderTeamManagement(data, { log, reload: () => renderTeamManagementView() });
    
    teamMgmtEl.innerHTML = "";
    teamMgmtEl.appendChild(container);
    
  } catch (e) {
    teamMgmtEl.innerHTML = `<div class="muted">Error loading team management.</div>`;
    log("Team management error", String(e));
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
        const data = await apiTask(`/manager/project/${CURRENT_USER.user_id}`, { method: "GET" });
        userTasks = Array.isArray(data) ? data : [];
        setLastTasks(userTasks);
      } else if (isCurrentUserDirector()) {
        // For directors, load tasks from their managed departments (returns dict grouped by team)
        const data = await apiTask(`/director/${CURRENT_USER.user_id}`, { method: "GET" });
        // Flatten the dict into an array of all tasks, deduplicating by task ID
        userTasks = [];
        const taskIdsSeen = new Set();
        if (data && typeof data === 'object') {
          Object.values(data).forEach(teamTaskList => {
            if (Array.isArray(teamTaskList)) {
              teamTaskList.forEach(task => {
                if (!taskIdsSeen.has(task.id)) {
                  taskIdsSeen.add(task.id);
                  userTasks.push(task);
                }
              });
            }
          });
        }
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
    
    // Update all project and tag filters based on user's tasks
    updateAllProjectFilters(userTasks);
    updateAllTagFilters(userTasks);
    
    // Apply team calendar filters if staff user
    if (isCurrentUserStaff()) {
      renderTeamCalendar();
    }
    
    // Apply timeline and gantt views if manager/director
    if (isCurrentUserManagerOrDirector()) {
      renderTimelineView();
      renderGanttView();
    }
    
    // Check and send notifications for overdue/upcoming tasks
    // This runs once per session/day (tracked via localStorage)
    checkAndSendNotifications(userTasks, { log }).catch(err => {
      log("Notification check error", String(err));
      // Don't show toast for notification errors - they're not critical
    });
    
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
  // Set default user (Staff 1) only if no user is currently selected
  if (!CURRENT_USER) {
    const defaultUser = USERS.find(u => u.user_id === DEMO_USER_IDS.STAFF1) || USERS[0];
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
  const managerOnlyTabTeamMgmt = document.getElementById("tabTeamManagement");
  if (managerOnlyTabTeamMgmt && isCurrentUserManagerOrDirector()) {
    managerOnlyTabTeamMgmt.style.display = "block";
  }
}

function updateUserSelectionUI() {
  const staff1Btn = document.getElementById("userStaff1");
  const staff2Btn = document.getElementById("userStaff2");
  const manager1Btn = document.getElementById("userManager1");
  const manager2Btn = document.getElementById("userManager2");
  const director1Btn = document.getElementById("userDirector1");
  const director2Btn = document.getElementById("userDirector2");
  
  if (CURRENT_USER) {
    // Remove active class from all buttons
    staff1Btn?.classList.remove("active");
    staff2Btn?.classList.remove("active");
    manager1Btn?.classList.remove("active");
    manager2Btn?.classList.remove("active");
    director1Btn?.classList.remove("active");
    director2Btn?.classList.remove("active");
    
    // Add active class to current user button
    if (CURRENT_USER.user_id === DEMO_USER_IDS.STAFF1) {
      staff1Btn?.classList.add("active");
    } else if (CURRENT_USER.user_id === DEMO_USER_IDS.STAFF2) {
      staff2Btn?.classList.add("active");
    } else if (CURRENT_USER.user_id === DEMO_USER_IDS.MANAGER1) {
      manager1Btn?.classList.add("active");
    } else if (CURRENT_USER.user_id === DEMO_USER_IDS.MANAGER2) {
      manager2Btn?.classList.add("active");
    } else if (CURRENT_USER.user_id === DEMO_USER_IDS.DIRECTOR1) {
      director1Btn?.classList.add("active");
    } else if (CURRENT_USER.user_id === DEMO_USER_IDS.DIRECTOR2) {
      director2Btn?.classList.add("active");
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
    const managerOnlyTabTeamMgmt = document.getElementById("tabTeamManagement");
    if (managerOnlyTabTeamMgmt) {
      managerOnlyTabTeamMgmt.style.display = isCurrentUserManagerOrDirector() ? "block" : "none";
    }
    
    // Auto-switch to List view if current tab is not accessible
    const activeTab = document.querySelector(".tab-btn.active");
    if (activeTab) {
      const tabName = activeTab.getAttribute("data-tab");
      if (tabName === "teamSchedule" && !isCurrentUserStaff()) {
        switchTab("list");
      } else if (tabName === "timeline" && !isCurrentUserManagerOrDirector()) {
        switchTab("list");
      } else if (tabName === "teamManagement" && !isCurrentUserManagerOrDirector()) {
        switchTab("list");
      }
    }
  }
}

// Reset all filters to their default values
function resetAllFilters() {
  // List view filters
  const filterStatus = document.getElementById("filterStatus");
  const filterPriority = document.getElementById("filterPriority");
  const filterProject = document.getElementById("filterProject");
  const filterTag = document.getElementById("filterTag");
  
  if (filterStatus) filterStatus.value = "";
  if (filterPriority) filterPriority.value = "";
  if (filterProject) filterProject.value = "";
  if (filterTag) filterTag.value = "";
  
  // Calendar view filters
  const calFilterStatus = document.getElementById("calFilterStatus");
  const calFilterPriority = document.getElementById("calFilterPriority");
  const calFilterProject = document.getElementById("calFilterProject");
  const calFilterTag = document.getElementById("calFilterTag");
  
  if (calFilterStatus) calFilterStatus.value = "";
  if (calFilterPriority) calFilterPriority.value = "";
  if (calFilterProject) calFilterProject.value = "";
  if (calFilterTag) calFilterTag.value = "";
  
  // Team calendar filters
  const teamCalFilterStatus = document.getElementById("teamCalFilterStatus");
  const teamCalFilterPriority = document.getElementById("teamCalFilterPriority");
  const teamCalFilterProject = document.getElementById("teamCalFilterProject");
  const teamCalFilterTag = document.getElementById("teamCalFilterTag");
  
  if (teamCalFilterStatus) teamCalFilterStatus.value = "";
  if (teamCalFilterPriority) teamCalFilterPriority.value = "";
  // Team calendar project filter will be set by updateAllProjectFilters, but reset it here too
  if (teamCalFilterProject) teamCalFilterProject.value = "";
  if (teamCalFilterTag) teamCalFilterTag.value = "";
  
  // Timeline view filters
  const timelineFilterProject = document.getElementById("timelineFilterProject");
  const timelineSortBy = document.getElementById("timelineSortBy");
  
  if (timelineFilterProject) timelineFilterProject.value = "";
  if (timelineSortBy) timelineSortBy.value = "";
  
  // Gantt view filters
  const ganttFilterProject = document.getElementById("ganttFilterProject");
  const ganttFilterStatus = document.getElementById("ganttFilterStatus");
  const ganttFilterPriority = document.getElementById("ganttFilterPriority");
  
  if (ganttFilterProject) ganttFilterProject.value = "";
  if (ganttFilterStatus) ganttFilterStatus.value = "";
  if (ganttFilterPriority) ganttFilterPriority.value = "";
}

function switchUser(userId) {
  const user = USERS.find(u => u.user_id === userId);
  if (user) {
    setCurrentUser(user);
    updateUserSelectionUI();
    // Reset all filters for the new user
    resetAllFilters();
    // Reset reminder settings and notification tracking for the new user
    resetReminderSettings();
    resetNotificationTracking();
    // Reload tasks for the new user (this will also update filters with new user's projects/tags)
    loadParents();
  }
}

// Wire tabs
function switchTab(tabName) {
  const tabList = document.getElementById("tabList");
  const tabCalendar = document.getElementById("tabCalendar");
  const tabTeamSchedule = document.getElementById("tabTeamSchedule");
  const tabTimeline = document.getElementById("tabTimeline");
  const tabTeamManagement = document.getElementById("tabTeamManagement");
  const contentList = document.getElementById("tabContentList");
  const contentCalendar = document.getElementById("tabContentCalendar");
  const contentTeamSchedule = document.getElementById("tabContentTeamSchedule");
  const contentTimeline = document.getElementById("tabContentTimeline");
  const contentTeamManagement = document.getElementById("tabContentTeamManagement");
  
  // Remove active class from all tabs and content
  [tabList, tabCalendar, tabTeamSchedule, tabTimeline, tabTeamManagement].forEach(tab => tab?.classList.remove("active"));
  [contentList, contentCalendar, contentTeamSchedule, contentTimeline, contentTeamManagement].forEach(content => content?.classList.remove("active"));
  
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
  } else if (tabName === "teamManagement") {
    tabTeamManagement?.classList.add("active");
    contentTeamManagement?.classList.add("active");
    renderTeamManagementView();
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
  document.getElementById("tabTeamManagement")?.addEventListener("click", () => switchTab("teamManagement"));

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

  // Wire user selection buttons - Demo users
  const staff1Btn = document.getElementById("userStaff1");
  const staff2Btn = document.getElementById("userStaff2");
  const manager1Btn = document.getElementById("userManager1");
  const manager2Btn = document.getElementById("userManager2");
  const director1Btn = document.getElementById("userDirector1");
  const director2Btn = document.getElementById("userDirector2");
  
  staff1Btn?.addEventListener("click", () => switchUser(DEMO_USER_IDS.STAFF1));
  staff2Btn?.addEventListener("click", () => switchUser(DEMO_USER_IDS.STAFF2));
  manager1Btn?.addEventListener("click", () => switchUser(DEMO_USER_IDS.MANAGER1));
  manager2Btn?.addEventListener("click", () => switchUser(DEMO_USER_IDS.MANAGER2));
  director1Btn?.addEventListener("click", () => switchUser(DEMO_USER_IDS.DIRECTOR1));
  director2Btn?.addEventListener("click", () => switchUser(DEMO_USER_IDS.DIRECTOR2));

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
bindReminderSettings({ log, reload: () => autoReload() });
bindReportExport({ log });

// First load
loadParents();
});
