// App state & shared helpers
export let USERS = [];
export let LAST_TASKS = [];
export let CAL_MONTH = startOfMonth(new Date());

export function setUsers(list){ USERS = list || []; }
export function setLastTasks(list){ LAST_TASKS = list || []; }
export function setCalMonth(d){ CAL_MONTH = startOfMonth(d); }

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
