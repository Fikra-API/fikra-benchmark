# Reproducing Phase 1

1. **Rebuild the frozen benchmark.** Run the benchmark-build cell of `notebooks/phase1_run_original.ipynb` (cell 5) with the pinned dataset revisions in `benchmark/frozen_manifest.json` and a Hugging Face token that has GPQA access.
2. **Verify it.** Compare the rebuilt file's SHA-256 with `benchmark_sha256`, and each task's `prompt_hash` with `benchmark/benchmark_500_public_manifest.csv`. This checks fidelity without publishing any prompt text.
3. **Generation (optional).** The same notebook runs all 2,000 model-task evaluations. It needs a Fikra API key, supplied via Colab secrets and never stored in the notebook. Settings: temperature 0, top-p 1, one attempt per pair, 4,096 max output tokens, 12 workers under a shared cap of about 80 requests per minute.
4. **Score.** Use the code in `evaluation/` on `results/raw/generations_1894.jsonl` to produce `results/scored/` and the paper's tables.

Note: GPQA generations in `results/raw/` are redacted, so GPQA scores can only be recomputed by re-running generation, or from the published per-item scores in `results/scored/`.
