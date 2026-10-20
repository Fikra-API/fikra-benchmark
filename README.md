# fikra-benchmark

Nightly probes against the Fikra API DeepSeek lanes. One tiny Chat Completions call per lane, once a night: status plus latency, appended to a CSV history.

## Lanes

- deepseek-v4.1-flash
- deepseek-v4.1-flash-1017
- deepseek-v4-flash-0731
- glm-5.3-flash
- kimi-k3

## Probe budget

Sixteen output tokens per call, five lanes, once daily. Pennies per month on Fikra's per-token pricing ($0.045 per 1M input on `deepseek-v4.1-flash`, prices verified 2026-10-19 at the [pricing page](https://fikraapi.co.ke/pricing)).

## Files

- `lanes.json`: latest run
- `history.csv`: append-only, one row per lane per night
- README table rewritten by the workflow after each run

## Set up

1. Workflow runs nightly at 02:17 UTC (manually dispatchable).
2. Requires the `FIKRA_API_KEY` secret on this repo (create a key at https://fikraapi.co.ke, M-Pesa or card).
