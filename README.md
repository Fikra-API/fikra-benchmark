# Fikra Benchmark, Phase 1

Comparative evaluation of four language-model configurations served through the Fikra API (fikra-flash, fikra-pro-20b, fikra-pro-120b, fikra-qwen-max) on a frozen 500-task suite drawn from MMLU-Pro, GPQA-Diamond, GSM8K, IFEval, LiveCodeBench, BFCL and FRES.

- Run: `fikra-benchmark-phase1-2026-09-26-4model` (experiment `fikra-phase1-2026-09-26-v1`)
- Benchmark SHA-256: `bf904af6e4a7f909c92642f2299f1001c7f1aff88894684fd61f2e799df72bfb`
- Coverage: 1,894 of 2,000 planned evaluations succeeded; 395 tasks have results for all four configurations (counted over all 500 tasks, including unscored components)
- Scored components: GPQA-Diamond, GSM8K, MMLU-Pro, IFEval, BFCL. LiveCodeBench and FRES are excluded from scoring.
- Paper: see `paper/` (arXiv link to be added)

**Disclosure:** the repository owner operates the Fikra API, and FRES is Fikra-owned.

## Layout
| Path | Contents |
|---|---|
| `paper/` | LaTeX source, figures, tables |
| `benchmark/` | Frozen manifest, prompt-hash manifest, FRES, model registry snapshot, `SOURCES.md` |
| `results/raw/` | Successful generations (1,894), full attempt log (2,321), run manifest, missing pairs |
| `results/scored/` | Per-item scores and summary tables |
| `notebooks/` | Original Colab notebook (benchmark build and generation run) |
| `evaluation/` | Scoring and analysis code |
| `docs/` | `REPRODUCING.md`, `KNOWN_ISSUES.md` |

## GPQA
GPQA-Diamond text is not redistributed. GPQA output text in `results/raw/` is replaced by a hash and character count. To reproduce, obtain GPQA access yourself and follow `docs/REPRODUCING.md`.

## Licences
Code: MIT (`LICENSE`). Results, paper and FRES: CC BY 4.0 (`LICENSE-DATA`). Upstream datasets keep their own licences (`benchmark/SOURCES.md`).

## Citation
See `CITATION.cff`. A DOI badge will be added after the first Zenodo release.
