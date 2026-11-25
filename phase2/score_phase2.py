#!/usr/bin/env python3
"""Score Fikra Benchmark Phase 2 generations.

Scored components (as Phase 1): MMLU-Pro, GPQA-Diamond, GSM8K, IFEval
(strict and loose), BFCL. LiveCodeBench and FRES stay unscored, as in Phase 1.

Methods
  MMLU-Pro      letter A-J: a lone letter, else the last standalone A-J token in
                the final 200 characters (evaluation/rescore_mmlu_pro.py).
  GPQA-Diamond  same rule over A-D, preferring an explicit "answer is X".
  GSM8K         the last number in the output (commas and $ removed) equals the
                reference.
  IFEval        Google's official instruction checker (instruction_following_eval),
                strict and loose; kwargs with None values are dropped, the same
                sanitisation Phase 1 needed.
  BFCL          the AST checker from the pinned BFCL commit (f7cf735) applied to
                the returned tool calls; function names compared as sent.

A generation that failed or hit the output cap with no answer counts as wrong.
Usage: python phase2/score_phase2.py   -> phase2/work/scores.json + items.csv
"""
import csv
import json
import re
import sys
import types
from collections import defaultdict
from enum import Enum
from pathlib import Path

HERE = Path(__file__).resolve().parent
WORK = HERE / "work"
import os
RESULTS = Path(os.getenv("SCORE_RESULTS") or WORK / "fikra-benchmark-phase2-2026-11-25_results.jsonl")
TASKS = WORK / "benchmark_500.jsonl"

# ---------- IFEval (official) ----------
sys.path.insert(0, str(HERE / "vendor" / "google-research"))
from instruction_following_eval import evaluation_lib  # noqa: E402

# ---------- BFCL AST checker (pinned), loaded without its heavy package ----------
_AST = WORK / "bfcl_repo/berkeley-function-call-leaderboard/bfcl_eval/eval_checker/ast_eval/ast_checker.py"


def _load_bfcl():
    src = _AST.read_text()
    src = re.sub(r"^from bfcl_eval[^\n]*\((?:[^)]*)\)\n", "", src, flags=re.M)
    src = re.sub(r"^from bfcl_eval[^\n]*\n", "", src, flags=re.M)

    class Language(Enum):
        PYTHON = "python"
        JAVA = "java"
        JAVASCRIPT = "javascript"

    mod = types.ModuleType("bfcl_ast")
    mod.__dict__.update({"Language": Language, "MODEL_CONFIG_MAPPING": {},
                         "JAVA_TYPE_CONVERSION": {}, "JS_TYPE_CONVERSION": {},
                         "java_type_converter": None, "js_type_converter": None})
    exec(compile(src, str(_AST), "exec"), mod.__dict__)
    mod.convert_func_name = lambda name, model_name: name  # names compared as sent
    return mod, Language


BFCL, Language = _load_bfcl()


def letter(text, allowed):
    text = text if isinstance(text, str) else ""
    m = re.findall(r"answer\s*(?:is|:)\s*\(?\**([%s])\**\)?" % allowed, text, flags=re.I)
    if m:
        return m[-1].upper()
    letters = re.sub(r"[^A-Za-z]", "", text)
    if len(letters) == 1 and letters.upper() in allowed:
        return letters.upper()
    found = re.findall(r"\b([%s])\b" % allowed, text[-200:])
    return found[-1] if found else ""


def last_number(text):
    nums = re.findall(r"-?\d[\d,]*\.?\d*", (text or "").replace("$", ""))
    if not nums:
        return None
    try:
        return float(nums[-1].replace(",", "").rstrip("."))
    except ValueError:
        return None


def score_ifeval(task, text):
    md = json.loads(task["metadata_json"])
    kwargs = [{k: v for k, v in (kw or {}).items() if v is not None} for kw in md["kwargs"]]
    inp = evaluation_lib.InputExample(key=md.get("key", 0), instruction_id_list=md["instruction_id_list"],
                                      prompt=task["prompt"], kwargs=kwargs)
    p2r = {task["prompt"]: text or ""}
    strict = evaluation_lib.test_instruction_following_strict(inp, p2r).follow_all_instructions
    loose = evaluation_lib.test_instruction_following_loose(inp, p2r).follow_all_instructions
    return int(strict), int(loose)


def score_bfcl(task, row):
    md = json.loads(task["metadata_json"])
    try:
        calls = json.loads(row.get("tool_calls_json") or "[]")
        output = []
        for c in calls:
            fn = c.get("function") or {}
            args = fn.get("arguments")
            args = json.loads(args) if isinstance(args, str) and args.strip() else (args or {})
            output.append({fn.get("name"): args})
        if not output:
            return 0
        res = BFCL.ast_checker(md["function"], output, md["ground_truth"]["ground_truth"],
                               Language.PYTHON, task.get("category") or md.get("category", ""), "fikra")
        return int(bool(res.get("valid")))
    except Exception:
        return 0


def main():
    tasks = {t["task_id"]: t for t in map(json.loads, open(TASKS))}
    best = {}
    for line in open(RESULTS):
        if not line.strip():
            continue
        try:
            r = json.loads(line)
        except json.JSONDecodeError:
            continue
        key = (r["task_id"], r["model"])
        if r.get("success") or key not in best:
            best[key] = r
    items, tally = [], defaultdict(lambda: defaultdict(lambda: [0, 0]))
    for (tid, model), r in sorted(best.items()):
        t = tasks.get(tid)
        if not t:
            continue
        ds, text, ok = t["dataset"], (r.get("output_text") or "") if r.get("success") else "", None
        if ds == "MMLU-Pro":
            ok = int(letter(text, "ABCDEFGHIJ") == t["reference_answer"])
        elif ds == "GPQA-Diamond":
            ok = int(letter(text, "ABCD") == t["reference_answer"])
        elif ds == "GSM8K":
            n = last_number(text)
            ok = int(n is not None and abs(n - float(t["reference_answer"])) < 1e-6)
        elif ds == "IFEval":
            s, l = score_ifeval(t, text) if r.get("success") else (0, 0)
            tally[model]["IFEval (loose)"][0] += l
            tally[model]["IFEval (loose)"][1] += 1
            ok, ds = s, "IFEval (strict)"
        elif ds == "BFCL":
            ok = score_bfcl(t, r) if r.get("success") else 0
        else:
            continue  # LiveCodeBench, FRES: not scored (as Phase 1)
        tally[model][ds][0] += ok
        tally[model][ds][1] += 1
        items.append((tid, model, ds, ok, int(bool(r.get("success")))))
    summary = {m: {d: {"correct": k, "n": n, "pct": round(100 * k / n, 2) if n else None}
                   for d, (k, n) in ds_.items()} for m, ds_ in tally.items()}
    json.dump({"run": "fikra-benchmark-phase2-2026-11-25", "summary": summary}, open(WORK / "scores.json", "w"), indent=1)
    with open(WORK / "items.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["task_id", "model", "dataset", "correct", "generation_succeeded"])
        w.writerows(items)
    for m, ds_ in sorted(summary.items()):
        print(m, {d: f"{v['pct']}% ({v['correct']}/{v['n']})" for d, v in sorted(ds_.items())})


if __name__ == "__main__":
    main()
