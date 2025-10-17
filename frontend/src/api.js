export const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

export async function api(path, opts = {}){
  const res = await fetch(API_BASE + path, {
    headers: { "Content-Type": "application/json", ...(opts.headers||{}) },
    ...opts,
  });
  if(!res.ok) throw new Error(`HTTP ${res.status}`);
  const ct = res.headers.get("content-type") || "";
  return ct.includes("application/json") ? res.json() : res.text();
}
