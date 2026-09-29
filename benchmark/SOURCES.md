# Benchmark sources

Frozen on 2026-09-26 (experiment `fikra-phase1-2026-09-26-v1`, selection seed 20260926).
Benchmark SHA-256: `bf904af6e4a7f909c92642f2299f1001c7f1aff88894684fd61f2e799df72bfb`

| Component | Tasks | Source | Revision | Notes |
|---|---|---|---|---|
| BFCL | 50 | `https://github.com/EnlightenedAI/BFCL.git` | `f7cf735` | categories: multiple=10, parallel=10, parallel_multiple=10, simple_python=20 |
| FRES | 50 | `Fikra-owned` | `v1` |  |
| GPQA-Diamond | 50 | `Idavidrein/gpqa` | `83022cefff930aea54f654c0b282e74b9eeda5c6` | subset `diamond`; redistribution: **restricted** |
| GSM8K | 75 | `openai/gsm8k` | `740312add88f781978c0658806c59bc2815b9866` | split `test` |
| IFEval | 75 | `google/IFEval` | `966cd89545d6b6acfd7638bc708b98261ca58e84` | split `train` |
| LiveCodeBench | 100 | `livecodebench/code_generation_lite` | `d44be6b144381afa49392b1f0eb424a64a4d8a10` |  |
| MMLU-Pro | 100 | `TIGER-Lab/MMLU-Pro` | `b189ec765aa7ed75c8acfea42df31fdae71f97be` | split `test` |

## Upstream licences and access
- GSM8K (MIT), MMLU-Pro (MIT), IFEval (Apache-2.0), BFCL (Apache-2.0): task text is not redistributed here except through hashes; rebuild from the pinned revisions.
- LiveCodeBench: see the upstream licence.
- **GPQA-Diamond:** gated dataset. Its authors ask that examples not be posted in plain text online, so no GPQA question text, reference answers, or model outputs quoting them are in this repository. GPQA output text in `results/raw/` is replaced by a SHA-256 hash and length.
- **FRES:** Fikra-owned and published in full as `fres_v1.jsonl` (see below).

## What is and is not in `benchmark/`
- `benchmark_500_public_manifest.csv`: every task's ID, dataset, revision, category, scoring type and **prompt hash**, with no prompt text. Use it to verify a rebuilt benchmark.
- `fres_v1.jsonl`: the 50 FRES tasks in full (SHA-256 of this file: `e44bca3440fdd4d011a17c72449c8ec55c1724b4ef391bb2c4157d125c0f3244`). The manifest's `fres_sha256` was computed over the original internal serialisation, which cannot be reproduced from this file alone.
- The full 500-task file with prompts and references is **not** published because it contains GPQA.

## BFCL source
The frozen manifest records the BFCL source as `https://github.com/EnlightenedAI/BFCL.git` at commit `f7cf735`. This is recorded as-is; see `docs/KNOWN_ISSUES.md`.
