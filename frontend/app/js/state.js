// App state & shared helpers
export let USERS = [];
export let LAST_TASKS = [];
export let CAL_MONTH = startOfMonth(new Date());
export let CURRENT_USER = null;

export function setUsers(list){ USERS = list || []; }
export function setLastTasks(list){ LAST_TASKS = list || []; }
export function setCalMonth(d){ CAL_MONTH = startOfMonth(d); }
export function setCurrentUser(user){ CURRENT_USER = user; }

// Date helpers
export function startOfMonth(d){ const x = new Date(d); x.setDate(1); x.setHours(0,0,0,0); return x; }
export function addMonths(d, n){ const x = new Date(d); x.setMonth(x.getMonth()+n); return startOfMonth(x); }
export function pad(n){ return n<10 ? "0"+n : String(n); }
export function fmtYMD(d){ return `${d.getFullYear()}-${pad(d.getMonth()+1)}-${pad(d.getDate())}`; }
export function parseYMD(s){
  if(!s) return null;
  const m = /^(\d{4})-(\d{2})-(\d{2})$/.exec(String(s));
  if(!m) return null;
  return new Date(Number(m[1]), Number(m[2])-1, Number(m[3]));
}
export const escapeHtml = (s) => String(s).replace(/[&<>"']/g, m => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;','\'':'&#39;'}[m]));
export const getSubtasks = (t) => t.subTasks || t.subtasks || [];
export const getAssignees = (t) => t.assignees || t.users || [];
export const getPriorityDisplay = (t) => (typeof t.priority === "number" ? String(t.priority) : (t.priority || "—"));
export const getUsers = () => USERS;

// Toast notification helper
export function showToast(message, type = 'info') {
  const container = document.getElementById('toast-container');
  if (!container) return;
  
  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;
  
  const content = document.createElement('div');
  content.className = 'toast-content';
  content.textContent = message;
  toast.appendChild(content);
  
  const dismiss = document.createElement('button');
  dismiss.className = 'toast-dismiss';
  dismiss.innerHTML = '×';
  dismiss.setAttribute('aria-label', 'Dismiss');
  dismiss.addEventListener('click', () => dismissToast(toast));
  toast.appendChild(dismiss);
  
  container.appendChild(toast);
  
  // Auto-dismiss after 3 seconds
  setTimeout(() => dismissToast(toast), 3000);
  
  function dismissToast(element) {
    element.classList.add('fade-out');
    setTimeout(() => element.remove(), 300);
  }
}

// User filtering helpers
export const getTasksForCurrentUser = () => {
  if (!CURRENT_USER) return LAST_TASKS;
  return LAST_TASKS.filter(task => {
    const assignees = getAssignees(task);
    return assignees.some(assignee => 
      (assignee.user_id || assignee.id) === CURRENT_USER.user_id
    );
  });
};

export const isTaskAssignedToCurrentUser = (task) => {
  if (!CURRENT_USER) return false;
  const assignees = getAssignees(task);
  return assignees.some(assignee => 
    (assignee.user_id || assignee.id) === CURRENT_USER.user_id
  );
};

export const isCurrentUserStaff = () => {
  return CURRENT_USER && CURRENT_USER.role === "Staff";
};

export const isCurrentUserManager = () => {
  return CURRENT_USER && CURRENT_USER.role === "Manager";
};

export const isCurrentUserDirector = () => {
  return CURRENT_USER && CURRENT_USER.role === "Director";
};

export const isCurrentUserManagerOrDirector = () => {
  return isCurrentUserManager() || isCurrentUserDirector();
};
