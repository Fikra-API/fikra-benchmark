"""Rescore MMLU-Pro from the published raw generations.

Usage (from the repo root):
    python evaluation/rescore_mmlu_pro.py

Reads  results/raw/generations_1894.jsonl and benchmark/mmlu_pro_reference.csv
Writes results/scored/mmlu_pro_items.csv and prints accuracy per model.

Answer extraction (all ten options, A-J):
  1. If the output consists of a single letter A-J, use it.
  2. Otherwise use the last standalone A-J token in the final 200 characters.
"""
import csv, json, re
from collections import defaultdict

def extract(text):
    text = text if isinstance(text, str) else ""
    letters = re.sub(r"[^A-Za-z]", "", text)
    if len(letters) == 1 and letters.upper() in "ABCDEFGHIJ":
        return letters.upper()
    found = re.findall(r"\b([A-J])\b", text[-200:])
    return found[-1] if found else ""

ref = {r["task_id"]: r["reference_letter"] for r in csv.DictReader(open("benchmark/mmlu_pro_reference.csv"))}
rows, tally = [], defaultdict(lambda: [0, 0])
for line in open("results/raw/generations_1894.jsonl"):
    g = json.loads(line)
    if not g.get("success") or g["task_id"] not in ref:
        continue
    pred = extract(g.get("output_text"))
    ok = int(pred == ref[g["task_id"]])
    rows.append((g["task_id"], g["model"], pred, ref[g["task_id"]], ok))
    tally[g["model"]][0] += ok
    tally[g["model"]][1] += 1

rows.sort(key=lambda r: (r[1], r[0]))
with open("results/scored/mmlu_pro_items.csv", "w", newline="") as f:
    w = csv.writer(f); w.writerow(["task_id", "model", "extracted", "reference", "correct"]); w.writerows(rows)
for m, (k, n) in sorted(tally.items()):
    print(f"{m}: {k}/{n} = {100*k/n:.2f}%")
