#!/usr/bin/env python3
"""Fikra Benchmark Phase 2: generation runner.

Re-runs the frozen Phase 1 500-task suite (same build code, same dataset
revisions, same SHA-256 gate) on the Phase 2 models. It executes the original
notebook's cells unchanged except for the run configuration below, so the
protocol stays auditable against Phase 1:

  * models:            PHASE2_MODELS
  * output cap:        32,768 tokens (Phase 1: 4,096). Phase 1's KNOWN_ISSUES
                       names the 4k cap as a likely cause of scores below
                       published values; reasoning models need the room.
  * everything else:   temperature 0, top-p 1, streaming, one success per
                       (task, model) pair, resumable.

Usage:
  FIKRA_API_KEY=... HF_TOKEN=... python phase2/run_phase2.py [model ...]
Results: phase2/work/<RUN_ID>_results.jsonl
"""
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
WORK = Path(__file__).resolve().parent / "work"
WORK.mkdir(parents=True, exist_ok=True)

PHASE2_MODELS = sys.argv[1:] or [
    "qwen3.8-max",          # first: free window ends 25 Nov 2026
    "qwen3.8-27b",
    "deepseek-v4.1-flash",
    "mimo-v2.6-pro",
    "qwen4-max",
]
RUN_ID = "fikra-benchmark-phase2-2026-11-25"
EXPERIMENT_ID = "fikra-phase2-2026-11-25-v1"
MAX_OUTPUT_TOKENS = int(os.getenv("PHASE2_MAX_OUTPUT_TOKENS", "32768"))
WORKERS = int(os.getenv("PHASE2_WORKERS", "8"))
RPM = int(os.getenv("PHASE2_RPM", "60"))

nb = json.loads((REPO / "notebooks" / "phase1_run_original.ipynb").read_text())
cells = {i: "".join(c["source"]) for i, c in enumerate(nb["cells"]) if c["cell_type"] == "code"}


def patch_config(src: str) -> str:
    n = len(PHASE2_MODELS)
    src = re.sub(r'SEED = .*', 'SEED = 20260926  # unchanged: same frozen suite', src, count=1)
    src = re.sub(r'EXPERIMENT_ID = ".*"', f'EXPERIMENT_ID = "{EXPERIMENT_ID}"', src, count=1)
    src = re.sub(r'RUN_ID = ".*"', f'RUN_ID = "{RUN_ID}"', src, count=1)
    src = re.sub(r'FINAL_MODELS = \[.*?\]', f"FINAL_MODELS = {PHASE2_MODELS!r}", src, count=1, flags=re.S)
    src = re.sub(r'MODEL_UPSTREAM = \{.*?\}', "MODEL_UPSTREAM = {m: m for m in FINAL_MODELS}", src, count=1, flags=re.S)
    src = re.sub(r'EXPECTED_EVALUATIONS = \d+', f"EXPECTED_EVALUATIONS = {500 * n}", src, count=1)
    src = re.sub(r'MAX_OUTPUT_TOKENS = \d+', f"MAX_OUTPUT_TOKENS = {MAX_OUTPUT_TOKENS}", src, count=1)
    src = src.replace("assert len(FINAL_MODELS) == 4", f"assert len(FINAL_MODELS) == {n}")
    src = src.replace("assert len(FINAL_MODELS) * 500 == 2000", "")
    return src


def patch_root(src: str) -> str:
    return src.replace('ROOT = Path("/content/fikra_benchmark_phase1")', f'ROOT = Path({str(WORK)!r})')


def patch_build(src: str) -> str:
    """The notebook's build cell has trailing top-level code that assumes the
    fresh-build path. When the frozen suite already exists, run only the
    recovery branch (hash check + load) so nothing is rebuilt or overwritten."""
    if (WORK / "benchmark_500.jsonl").exists() and (WORK / "frozen_manifest.json").exists():
        head, sep, _ = src.partition("\nelse:\n")
        assert sep, "cell 5 layout changed"
        return head
    return src


def patch_runner(src: str) -> str:
    """Notebook bug: timing fields are only set when the stream returns a usage
    chunk, so a response without usage raised UnboundLocalError and was
    recorded as a failure. Initialise them with the token counters."""
    old = "            total_tokens = None\n\n            if usage:"
    assert old in src, "cell 9 layout changed"
    return src.replace(old, "            total_tokens = None\n            queue_time_s = None\n            prompt_time_s = None\n            completion_time_s = None\n            api_total_time_s = None\n\n            if usage:", 1)


def patch_run(src: str) -> str:
    src = re.sub(r'MAX_WORKERS = \d+', f"MAX_WORKERS = {WORKERS}", src, count=1)
    src = re.sub(r'TARGET_RPM = \d+', f"TARGET_RPM = {RPM}", src, count=1)
    return src.replace("2,000-evaluation", "Phase 2")


ns: dict = {"__name__": "__phase2__"}
plan = [(2, patch_root), (3, patch_config), (4, None), (5, patch_build), (6, None), (7, None),
        (8, None), (9, patch_runner), (10, None), (11, None), (12, patch_run), (13, None), (14, None)]
if os.getenv("PHASE2_BUILD_ONLY"):
    plan = [p for p in plan if p[0] <= 6]
for idx, patch in plan:
    src = cells[idx]
    if patch:
        src = patch(src)
    src = "\n".join(l for l in src.splitlines() if not l.lstrip().startswith("!"))
    print(f"\n===== notebook cell {idx} =====", flush=True)
    exec(compile(src, f"phase1_notebook_cell_{idx}", "exec"), ns)
