export const MockDB = (() => {
  let seq = 1000;
 const today = new Date();
    const iso = (d) => (d ? new Date(d).toISOString() : null);

    const store = [
    {
        id: 1,
        title: "Prepare Q4 report",
        status: "To-do",
        priority: "High",
        start_date: null,
        deadline: iso(new Date(today.getFullYear(), today.getMonth(), today.getDate() + 7)),
        collaborators: "julia@kira.ai, alex@kira.ai",
        notes: "Include churn",
        description: "Compile metrics & slides",
        parent_id: null,
        subtasks: [
        {
            id: 2,
            title: "Pull revenue data",
            status: "In progress",
            priority: "Medium",
            deadline: null,
            parent_id: 1,
            description: "BQ export",
            collaborators: "alex@kira.ai",
            notes: "partition by quarter",
        },
        {
            id: 3,
            title: "Build charts",
            status: "To-do",
            priority: "Low",
            deadline: null,
            parent_id: 1,
            description: "Looker + Slides",
            collaborators: "",
            notes: "",
        },
        ],
    },
    {
        id: 4,
        title: "Security review",
        status: "Blocked",
        priority: "Medium",
        start_date: null,
        deadline: null,
        collaborators: "",
        notes: "Waiting on approval",
        description: "Vendor risk",
        parent_id: null,
        subtasks: [],
    },
    {
        id: 5,
        title: "Marketing site refresh",
        status: "In progress",
        priority: "High",
        start_date: iso(new Date(today.getFullYear(), today.getMonth(), today.getDate() - 3)),
        deadline: iso(new Date(today.getFullYear(), today.getMonth(), today.getDate() + 14)),
        collaborators: "anita@kira.ai",
        notes: "Check branding guidelines",
        description: "Update homepage and blog layout",
        parent_id: null,
        subtasks: [
        {
            id: 6,
            title: "Hero section redesign",
            status: "To-do",
            priority: "High",
            deadline: null,
            parent_id: 5,
            description: "Add new case studies",
            collaborators: "",
            notes: "",
        },
        ],
    },
    {
        id: 7,
        title: "Incident postmortem",
        status: "Completed",
        priority: "Medium",
        start_date: iso(new Date(today.getFullYear(), today.getMonth(), today.getDate() - 10)),
        deadline: iso(new Date(today.getFullYear(), today.getMonth(), today.getDate() - 5)),
        collaborators: "sam@kira.ai",
        notes: "Write timeline & action items",
        description: "Outage RCA",
        parent_id: null,
        subtasks: [],
    },
    {
        id: 8,
        title: "A/B test: Pricing page",
        status: "In progress",
        priority: "Low",
        start_date: iso(new Date(today.getFullYear(), today.getMonth(), today.getDate() - 1)),
        deadline: iso(new Date(today.getFullYear(), today.getMonth(), today.getDate() + 10)),
        collaborators: "rosa@kira.ai",
        notes: "Monitor variant B",
        description: "Run experiment on new pricing tiers",
        parent_id: null,
        subtasks: [
        {
            id: 9,
            title: "Setup experiment in Optimizely",
            status: "Completed",
            priority: "Medium",
            deadline: null,
            parent_id: 8,
            description: "Configure traffic split",
            collaborators: "",
            notes: "",
        },
        {
            id: 10,
            title: "Collect initial results",
            status: "To-do",
            priority: "Low",
            deadline: null,
            parent_id: 8,
            description: "Export to Sheets",
            collaborators: "mei@kira.ai",
            notes: "",
        },
        ],
    },
    ];


  const parents = () => store;
  const flat = () => {
    const a = [];
    for (const p of store) { a.push(p); (p.subtasks || []).forEach(s => a.push(s)); }
    return a;
  };
  const findParent = (id) => store.find(x => x.id === id);
  const findAny = (id) => flat().find(x => x.id === id);

  async function list({ q = "", status = "" } = {}) {
    let out = parents().map(p => ({ ...p, subtasks: [ ...(p.subtasks || []) ] }));
    if (q) {
      const Q = q.toLowerCase();
      out = out.filter(t =>
        (t.title || "").toLowerCase().includes(Q) ||
        (t.collaborators || "").toLowerCase().includes(Q)
      );
    }
    if (status) out = out.filter(t => (t.status || "").toLowerCase() === status.toLowerCase());
    await sleep(40);
    return out;
  }

  async function create(payload) {
    const id = ++seq;
    const base = {
      id, title: payload.title,
      status: payload.status || "To-do",
      priority: payload.priority || "Medium",
      start_date: payload.start_date || null,
      deadline: payload.deadline || null,
      collaborators: payload.collaborators || "",
      notes: payload.notes || "",
      description: payload.description || "",
      parent_id: payload.parent_id || null,
      subtasks: []
    };
    if (payload.parent_id) {
      const par = findParent(payload.parent_id); if (!par) throw new Error("Parent not found");
      base.parent_id = par.id; par.subtasks.push(base);
    } else {
      store.push(base);
    }
    await sleep(40);
    return { id };
  }

  async function patch(id, updates) {
    const t = findAny(Number(id)); if (!t) throw new Error("Task not found");

    // re-parenting support
    if ("parent_id" in updates && updates.parent_id !== t.parent_id) {
      for (const p of store) {
        const idx = (p.subtasks || []).findIndex(s => s.id === t.id);
        if (idx >= 0) p.subtasks.splice(idx, 1);
      }
      if (updates.parent_id) {
        const target = findParent(updates.parent_id);
        if (target) target.subtasks.push(t);
        t.parent_id = updates.parent_id;
      } else {
        t.parent_id = null;
        if (!store.find(p => p.id === t.id)) store.push(t);
      }
    }

    Object.assign(t, updates);
    await sleep(30);
    return { id: t.id, updated: true };
  }

  async function setStatus(id, status) {
    const t = findAny(Number(id)); if (!t) throw new Error("Task not found");
    t.status = status; await sleep(20); return { id: t.id, status };
  }

  async function del(id) {
    id = Number(id);
    const pIndex = store.findIndex(p => p.id === id);
    if (pIndex >= 0) {
      const parent = store[pIndex];
      for (const s of (parent.subtasks || [])) {
        s.parent_id = null; s.subtasks = [];
        if (!store.find(p => p.id === s.id)) store.push(s);
      }
      store.splice(pIndex, 1);
      await sleep(20);
      return { id };
    }
    for (const p of store) {
      const sIndex = (p.subtasks || []).findIndex(s => s.id === id);
      if (sIndex >= 0) { p.subtasks.splice(sIndex, 1); await sleep(20); return { id }; }
    }
    throw new Error("Task not found");
  }

  function sleep(ms){ return new Promise(r => setTimeout(r, ms)); }

  // Expose ONLY what Backend needs
  return { list, create, patch, setStatus, delete: del };
})();
