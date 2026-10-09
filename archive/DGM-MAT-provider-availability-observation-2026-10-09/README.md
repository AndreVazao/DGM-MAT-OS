# Provider availability observation archive — 2026-10-09

Exact pre-change copies of the canonical files below were preserved before the availability-observation contract correction. Source and archive SHA-256 hashes matched at copy time.

- `reality_snapshot.py` — `FBBD82A556BC91D540BAB7584E15B85CBD6A52D442C07445FD99634549A77072`
- `runtime_api.py` — `E27A235B34E17463928153857BB1C262F93A6CFC6F6C771542A25ECBDF034A28`
- `test_provider_api_truth.py` — `0DF1AFED0A5B7DC2E83349D0F402434FB61BAB33B6D393169CB97609D07C51C7`

The pre-change API summary treated `available: false` as if no availability result had been reported, although the field itself was present. The snapshot also emitted `available: false` by default for unregistered source files and deferred checks, without distinguishing that default from an observed result. The correction will add an explicit observation marker and make the API summarize only observed availability state.

Historical copies only; do not copy the old inference behavior back into canonical code.
