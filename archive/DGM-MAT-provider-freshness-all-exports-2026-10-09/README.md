# Provider freshness across runtime exports — pre-change archive

Date: 2026-10-09
Purpose: preserve exact canonical source before expanding freshness enforcement from `/runtime/providers` to all runtime-state exports.

| Canonical source | Archived file | SHA-256 |
|---|---|---|
| core/api/runtime_api.py | untime_api.py | 36F6E7B638CC6B8BF84A316B052AD399161AE13B3C666E8650359AA503ADC156 |
| core/runtime/runtime_state_store.py | untime_state_store.py | 62A055267FB537FE82F3F96D08374A5F988A0FC48D9B98BFA72B989C71198250 |

Both archived copies were compared to their canonical sources using SHA-256 before any source edits. No secrets or runtime configuration were intentionally included.

