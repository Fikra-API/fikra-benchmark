# Original Colab notebook

`phase1_run_original.ipynb` is the notebook used for the production run, published unedited (outputs included). It contains, in order: dependency install, secrets and workspace setup, experiment configuration, reproducibility utilities, benchmark build/recovery (cell 5), integrity gate, model registry, request adapter, stream parser and single-evaluation runner, pre-flight, run manifest, the parallel resumable production run (cell 12), integrity check with CSV export, and a summary.

It does **not** contain scoring or evaluator code; that lives in `evaluation/`. The Fikra API key was supplied through Colab secrets and is not in the notebook.
