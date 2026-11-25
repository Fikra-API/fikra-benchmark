#!/usr/bin/env python3
"""Re-run BFCL tasks whose provider rejected dotted function names.

OpenAI-format endpoints require tool names matching ^[a-zA-Z0-9_-]+$; BFCL
uses names like "math.gcd". The official BFCL harness converts "." to "_"
for OpenAI-format models and maps names back before checking. Phase 2 sent
names unchanged; some providers accepted them, DeepSeek's rejected them and
the error arrived inside the stream (recorded as an empty generation).

This re-runs, for the given model, every BFCL task whose stored generation
has neither text nor tool calls, with "." -> "_" in function names, and
appends the new rows to the results file (the scorer keeps the latest
successful row per task/model and maps names back).
Usage: FIKRA_API_KEY=... python phase2/rerun_bfcl_sanitized.py deepseek-v4.1-flash
"""
import json
import os
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

WORK = Path(__file__).resolve().parent / "work"
RESULTS = WORK / "fikra-benchmark-phase2-2026-11-25_results.jsonl"
TASKS = WORK / "benchmark_500.jsonl"
URL = "https://api.fikraapi.co.ke/v1/chat/completions"
TYPE_REMAP = {"dict": "object", "float": "number", "tuple": "array", "any": "string"}


def schema(node):
    if isinstance(node, dict):
        return {k: (TYPE_REMAP.get(v, v) if k == "type" and isinstance(v, str) else schema(v)) for k, v in node.items()}
    if isinstance(node, list):
        return [schema(x) for x in node]
    return node


def messages(question):
    if isinstance(question, list) and question and all(isinstance(x, list) for x in question):
        question = [m for conv in question for m in conv]
    return [{"role": m.get("role", "user"), "content": m.get("content", "")} for m in question]


def main():
    model = sys.argv[1]
    key = os.environ["FIKRA_API_KEY"]
    tasks = {t["task_id"]: t for t in map(json.loads, open(TASKS))}
    latest = {}
    for line in open(RESULTS):
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        if r["model"] == model and r["task_id"].startswith("BFCL") and r.get("success"):
            latest[r["task_id"]] = r
    todo = [tid for tid, r in latest.items()
            if not (r.get("output_text") or "").strip() and r.get("tool_calls_json") in (None, "", "[]")]
    print(f"{len(todo)} empty BFCL generations to re-run for {model}")
    out = open(RESULTS, "a")
    for i, tid in enumerate(sorted(todo), 1):
        md = json.loads(tasks[tid]["metadata_json"])
        tools = []
        for fn in md["function"]:
            f = schema(fn)
            f["name"] = f["name"].replace(".", "_")
            tools.append({"type": "function", "function": f})
        payload = {"model": model, "messages": messages(md["question"]), "tools": tools, "tool_choice": "auto",
                   "temperature": 0, "top_p": 1, "max_tokens": 32768}
        t0 = time.time()
        try:
            resp = requests.post(URL, json=payload, headers={"Authorization": f"Bearer {key}"}, timeout=600)
            data = resp.json()
            ok = resp.status_code == 200 and "choices" in data
        except Exception as exc:
            ok, data = False, {"error": type(exc).__name__}
        msg = ((data.get("choices") or [{}])[0].get("message") or {}) if ok else {}
        usage = data.get("usage") or {}
        row = {"success": ok, "task_id": tid, "model": model, "attempt": 1, "http_status": resp.status_code if ok or "resp" in locals() else None,
               "started_at": datetime.fromtimestamp(t0, timezone.utc).isoformat(),
               "total_latency_ms": round((time.time() - t0) * 1000, 1), "ttft_ms": None,
               "output_text": msg.get("content") or "", "tool_calls_json": json.dumps(msg.get("tool_calls") or []),
               "input_tokens": usage.get("prompt_tokens"), "output_tokens": usage.get("completion_tokens"),
               "finish_reason": ((data.get("choices") or [{}])[0].get("finish_reason")) if ok else None,
               "dataset": "BFCL", "note": "rerun: function names '.'->'_' (official BFCL OpenAI-format handling)",
               "error_message": None if ok else json.dumps(data)[:500]}
        out.write(json.dumps(row) + "\n")
        out.flush()
        print(f"[{i}/{len(todo)}] {tid}: {'ok' if ok else 'FAIL'} tools={len(msg.get('tool_calls') or [])}", flush=True)
    out.close()


if __name__ == "__main__":
    main()
