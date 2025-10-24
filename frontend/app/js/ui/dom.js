export function el(tag, cls, html){
    const n = document.createElement(tag);
    if (cls) n.className = cls;
    if (html != null) n.innerHTML = html;
    return n;
  }
  export function listen(node, ev, cb){ node.addEventListener(ev, cb); return () => node.removeEventListener(ev, cb); }
  export function field(labelText, valueText){
    const span = el("span", "task-field");
    span.innerHTML = `<span class="task-field-label">${labelText}:</span> <span class="task-field-value">${valueText}</span>`;
    return span;
  }
  