import { TASK_BASE, USER_BASE, REPORT_BASE } from "./config.js";

async function doFetch(base, path, init) {
  const url = base + path;
  const res = await fetch(url, { headers: { "Content-Type": "application/json" }, ...init });
  if (!res.ok) {
    let detail = ""; try { detail = await res.text(); } catch {}
    throw new Error(`${res.status} ${res.statusText} - ${detail}`);
  }
  return res.status === 204 ? null : res.json();
}

// Special fetch for binary responses (PDF, Excel, etc.)
async function doFetchBinary(base, path, init) {
  const url = base + path;
  const res = await fetch(url, init);
  if (!res.ok) {
    let detail = ""; try { detail = await res.text(); } catch {}
    throw new Error(`${res.status} ${res.statusText} - ${detail}`);
  }
  return res.blob();
}

export const apiTask = (path, init) => doFetch(TASK_BASE, path, init);
export const apiUser = (path, init) => doFetch(USER_BASE, path, init);
export const apiReport = (path, init) => doFetchBinary(REPORT_BASE, path, init);
