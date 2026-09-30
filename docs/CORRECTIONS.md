# Corrections

## Release after v1.0.1: MMLU-Pro scores and latency table corrected

- **MMLU-Pro (error).** Earlier versions of the paper reported MMLU-Pro scores of 29.03 to 37%. These came from an answer-extraction step that accepted only options A-D, although MMLU-Pro has ten options (A-J). Restricting extraction to A-D reproduces the old numbers, and about 58% of correct answers fall outside A-D. Rescoring over all ten options gives Flash 77.00%, Pro 20B 67.74% (21/31), Pro 120B 82.00%, and Qwen Max 90.00%. Per-item scores are in `results/scored/mmlu_pro_items.csv`, and `evaluation/rescore_mmlu_pro.py` reproduces them from the raw generations. Other datasets' scores are unchanged.
- **Latency table (error).** Earlier versions reported medians that could not be reproduced from the published raw results, apart from Qwen Max. The table now uses all successful calls and lists n and TTFT n explicitly.
- **Harness validity.** The paper now states that 126 of the 1,894 successful generations ended at the 4,096-token output cap.
- **BFCL wording.** "Official" was removed from the description of the BFCL AST-checking logic; the pinned source commit (f7cf735) is now stated.
- **Affiliation.** The operating company is Lacesse Ventures.

Versions archived before this correction (Zenodo v1.0.0 and v1.0.1) contain the erroneous MMLU-Pro numbers. Use the latest version.
