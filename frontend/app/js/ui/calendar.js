import { CAL_MONTH, setCalMonth, addMonths, fmtYMD, parseYMD } from "../state.js";
import { escapeHtml, getSubtasks } from "../state.js";

function normalizeTaskDate(task, mode){
  const by = mode === "start" ? (task.start_date || task.startDate) : (task.deadline || task.due || task.due_date);
  const fallback = mode === "start" ? (task.deadline || task.due || task.due_date) : (task.start_date || task.startDate);
  return parseYMD(by) || parseYMD(fallback) || null;
}

function flattenTasksWithSubs(tasks){
  const out = [];
  (tasks||[]).forEach(t => {
    out.push({...t, __isSub:false});
    const subs = getSubtasks(t);
    if (Array.isArray(subs)) {
      // Only include subtasks that are not completed
      subs.filter(st => st.status !== "Completed").forEach(st => out.push({...st, __isSub:true, __parentId: t.id}));
    }
  });
  return out;
}

export function renderCalendar(tasks){
  const calendarPanel = document.getElementById("calendarPanel");
  const calendarEl = document.getElementById("calendar");
  const calTitle = document.getElementById("calTitle");
  const mode = document.getElementById("calDateMode").value;

  const year = CAL_MONTH.getFullYear();
  const month = CAL_MONTH.getMonth();
  const firstDow = new Date(year, month, 1).getDay();
  const start = new Date(year, month, 1 - firstDow);
  const labels = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];

  const map = new Map();
  // Filter out completed tasks for calendar view
  const activeTasks = (tasks || []).filter(t => t.status !== "Completed");
  const flat = flattenTasksWithSubs(activeTasks);
  flat.forEach(t => {
    const d = normalizeTaskDate(t, mode);
    if (!d) return;
    const key = fmtYMD(d);
    if (!map.has(key)) map.set(key, []);
    map.get(key).push(t);
  });

  calTitle.textContent = CAL_MONTH.toLocaleString(undefined, { month: "long", year: "numeric" });

  const frag = document.createDocumentFragment();
  const hdrRow = document.createElement("div");
  hdrRow.className = "cal-grid";
  labels.forEach(lbl => {
    const c = document.createElement("div");
    c.className = "cal-colhdr";
    c.textContent = lbl;
    hdrRow.appendChild(c);
  });
  frag.appendChild(hdrRow);

  let cur = new Date(start);
  for (let i=0; i<6; i++){
    const row = document.createElement("div");
    row.className = "cal-grid cal-row";
    for (let j=0; j<7; j++){
      const cell = document.createElement("div");
      cell.className = "cal-cell";
      if (cur.getMonth() !== month) cell.classList.add("cal-other-month");

      const day = document.createElement("div");
      day.className = "cal-day";
      const today = new Date(); today.setHours(0,0,0,0);
      const isToday = cur.getTime() === today.getTime();
      day.innerHTML = `<span>${cur.getDate()}</span>` + (isToday ? `<span class="pill ok">Today</span>` : `<span></span>`);
      cell.appendChild(day);

      const key = fmtYMD(cur);
      const items = map.get(key) || [];
      items.slice(0,5).forEach(t => {
        const el = document.createElement("div");
        el.className = "cal-task";
        const title = escapeHtml(t.title || `(untitled #${t.id})`);
        const project = (t.project_id != null) ? `· P${t.project_id}` : "";
        el.innerHTML = `${t.__isSub ? "↳ " : ""}${title} <span class="small">${project}</span>`;
        el.title = `${title}${project ? " " + project : ""}`;
        el.addEventListener("click", () => document.dispatchEvent(new CustomEvent("open-edit", { detail: t })));
        cell.appendChild(el);
      });
      if (items.length > 5){
        const more = document.createElement("div");
        more.className = "small muted";
        more.textContent = `+${items.length - 5} more`;
        cell.appendChild(more);
      }

      row.appendChild(cell);
      cur.setDate(cur.getDate()+1);
    }
    frag.appendChild(row);
  }

  calendarEl.innerHTML = "";
  calendarEl.appendChild(frag);
}

export function bindCalendarNav(){
  document.getElementById("calPrev").addEventListener("click", () => {
    setCalMonth(addMonths(CAL_MONTH, -1));
    document.dispatchEvent(new Event("redraw-calendar"));
  });
  document.getElementById("calNext").addEventListener("click", () => {
    setCalMonth(addMonths(CAL_MONTH, +1));
    document.dispatchEvent(new Event("redraw-calendar"));
  });
  document.getElementById("calToday").addEventListener("click", () => {
    setCalMonth(new Date());
    document.dispatchEvent(new Event("redraw-calendar"));
  });
}
