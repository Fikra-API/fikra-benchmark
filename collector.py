"""Nightly probe: one tiny Chat Completions call per DeepSeek lane.

Writes lanes.json (latest) and history.csv (append-only). Requires FIKRA_API_KEY.
"""
import csv, json, os, time, urllib.request

KEY = os.environ["FIKRA_API_KEY"]
LANES = [
    "deepseek-v4.1-flash",
    "deepseek-v4.1-flash-1017",
    "deepseek-v4-flash-0731",
    "glm-5.3-flash",
    "kimi-k3",
]
BASE = "https://api.fikraapi.co.ke/v1"

def probe(model):
    t0 = time.time()
    req = urllib.request.Request(
        BASE + "/chat/completions",
        data=json.dumps({"model": model, "messages": [{"role": "user", "content": "ping, reply ok"}], "max_tokens": 16}).encode(),
        headers={"Authorization": "Bearer " + KEY, "Content-Type": "application/json"},
        method="POST")
    try:
        r = urllib.request.urlopen(req, timeout=60)
        r.read()
        return {"model": model, "status": "ok", "latency_ms": int((time.time() - t0) * 1000)}
    except Exception as e:
        return {"model": model, "status": "error", "error": str(e)[:200], "latency_ms": int((time.time() - t0) * 1000)}

results = [probe(m) for m in LANES]
now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

json.dump({"checked_at": now, "lanes": results}, open("lanes.json", "w"), indent=1)
new = not os.path.exists("history.csv")
with open("history.csv", "a", newline="") as f:
    w = csv.DictWriter(f, fieldnames=["checked_at", "model", "status", "latency_ms"])
    if new:
        w.writeheader()
    for r in results:
        w.writerow({**r, "checked_at": now})

table = ["| Lane | Status | Latency |", "| --- | --- | --- |"]
for r in results:
    table.append("| %s | %s | %s |" % (r["model"], r["status"], r["latency_ms"]))
readme = open("README.md").read()
start = readme.find("## Last run")
end = readme.find("## Probe budget")
readme = readme[:start] + "## Last run\n\nChecked at " + now + "\n\n" + "\n".join(table) + "\n\n" + readme[end:]
open("README.md", "w").write(readme)
print("done", now)
