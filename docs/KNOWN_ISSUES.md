# Known issues and limitations

- **Coverage:** 106 of 2,000 evaluations have no successful result (Pro 20B: 105 missing; Flash: 1). Failed pairs are listed in `results/raw/missing_pairs.json`. Missing results are not counted as incorrect.
- **Excluded components:** LiveCodeBench and FRES are not scored, because reliable evaluation environments were not established. No scores are estimated or imputed for them.
- **IFEval:** 116 instruction entries needed keyword-argument sanitisation to run with the evaluator. Verification logic is otherwise retained.
- **BFCL:** the full evaluator stack could not run. Scoring used the AST-checking logic standalone. The frozen manifest records the source as `EnlightenedAI/BFCL` at commit `f7cf735`; confirm and state whether this matches Berkeley's official repository before describing it as "official".
- **Harness validity:** several absolute scores are below commonly reported values for the upstream models. Possible causes (output cap, answer extraction, reasoning settings, temperature 0) were not isolated in Phase 1.
- **GPQA redaction:** GPQA output text in `results/raw/` is redacted (hash and length only).
- **FRES hash:** the manifest's `fres_sha256` cannot be reproduced from `fres_v1.jsonl` alone; see `benchmark/SOURCES.md`.
