# Fikra Benchmark

[![Paper DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23078946.svg)](https://doi.org/10.5281/zenodo.23078946)
[![Code DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.23068925.svg)](https://doi.org/10.5281/zenodo.23068925)

**Live results, charts and method: [fikraapi.co.ke/benchmark](https://fikraapi.co.ke/benchmark)**

## Phase 2 (published 25 November 2026)

Same frozen 500-task suite, re-run on the models Fikra API serves today: `deepseek-v4.1-flash`, `qwen3.8-max`, `qwen3.8-27b`, `qwen4-max`, `mimo-v2.6-pro`.

- The suite is rebuilt from the pinned dataset revisions and must match the Phase 1 SHA-256 below before any call is made.
- Output cap raised from 4,096 to 32,768 tokens, because Phase 1's `KNOWN_ISSUES.md` names the cap as a likely cause of scores below published values.
- Everything else is unchanged: temperature 0, top-p 1, streaming, resumable, one success per task-model pair.
- Scores will be shown next to each lab's published numbers, with a source for every reference value.
- Results: `results/phase2/scores.json` (per model and benchmark) and `results/phase2/items.csv` (per item); live page with lab-published reference scores: https://fikraapi.co.ke/benchmark
- Scoring: `phase2/score_phase2.py` reproduces Phase 1's BFCL and MMLU-Pro exactly and IFEval/GSM8K within 1-3 items; BFCL names use the official '.'->'_' conversion for OpenAI-format endpoints (`phase2/rerun_bfcl_sanitized.py`); IFEval is seeded per task so scores are reproducible.
- Runner: `phase2/run_phase2.py` executes the original notebook cells with only the run configuration changed, so the protocol stays auditable.

```sh
FIKRA_API_KEY=... HF_TOKEN=... python phase2/run_phase2.py            # all Phase 2 models
PHASE2_BUILD_ONLY=1 HF_TOKEN=... python phase2/run_phase2.py          # rebuild + verify the suite only
```

## Phase 1

Comparative evaluation of four language-model configurations served through the Fikra API (fikra-flash, fikra-pro-20b, fikra-pro-120b, fikra-qwen-max) on a frozen 500-task suite drawn from MMLU-Pro, GPQA-Diamond, GSM8K, IFEval, LiveCodeBench, BFCL and FRES.

- Run: `fikra-benchmark-phase1-2026-09-26-4model` (experiment `fikra-phase1-2026-09-26-v1`)
- Benchmark SHA-256: `bf904af6e4a7f909c92642f2299f1001c7f1aff88894684fd61f2e799df72bfb`
- Coverage: 1,894 of 2,000 planned evaluations succeeded; 395 tasks have results for all four configurations (counted over all 500 tasks, including unscored components)
- Scored components: GPQA-Diamond, GSM8K, MMLU-Pro, IFEval, BFCL. LiveCodeBench and FRES are excluded from scoring.
- Paper: see `paper/` and [doi.org/10.5281/zenodo.23078946](https://doi.org/10.5281/zenodo.23078946)

**Disclosure:** the repository owner operates the Fikra API, and FRES is Fikra-owned.

## Layout
| Path | Contents |
|---|---|
| `paper/` | LaTeX source, figures, tables |
| `benchmark/` | Frozen manifest, prompt-hash manifest, FRES, model registry snapshot, `SOURCES.md` |
| `results/raw/` | Successful generations (1,894), full attempt log (2,321), run manifest, missing pairs |
| `results/scored/` | Per-item scores and summary tables |
| `notebooks/` | Original Colab notebook (benchmark build and generation run) |
| `phase2/` | Phase 2 runner (reuses the notebook cells; results in `phase2/work/`, not committed until scored) |
| `evaluation/` | Scoring and analysis code |
| `docs/` | `REPRODUCING.md`, `KNOWN_ISSUES.md` |

## GPQA
GPQA-Diamond text is not redistributed. GPQA output text in `results/raw/` is replaced by a hash and character count. To reproduce, obtain GPQA access yourself and follow `docs/REPRODUCING.md`.

## Licences
Code: MIT (`LICENSE`). Results, paper and FRES: CC BY 4.0 (`LICENSE-DATA`). Upstream datasets keep their own licences (`benchmark/SOURCES.md`).

## Citation
See `CITATION.cff`. Paper: https://doi.org/10.5281/zenodo.23078946 · Code (v1.0.2): https://doi.org/10.5281/zenodo.23068925
