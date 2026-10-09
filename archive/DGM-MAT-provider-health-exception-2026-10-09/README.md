# Provider health exception handling archive — 2026-10-09

Exact pre-change files copied from canonical DGM-MAT before modification. Source and archive SHA-256 values matched.

- `reality_snapshot.py` — `CA8E7311F5A405A4811271E79D5D906364CC23839440BAAB701244EB315B92B3`
- `test_reality_snapshot.py` — `89042E034DA54B450F4C5BDFECAF2A3ACFEF099E4CB68F4EEDD8F5641E6E66EA`

## Finding

A registered provider whose `check_health()` raised an exception could cause `RealitySnapshotService.snapshot()` to return an empty snapshot. The `/runtime/providers` endpoint called the provider-status collector directly, so this failure could also propagate as an endpoint error.

## Canonical correction

- A raised provider health check is represented as an observed `error` state.
- The failing provider is marked unavailable and unhealthy.
- The snapshot continues collecting other providers rather than failing wholesale.
- Regression test: `test_provider_health_exception_is_reported_as_observed_error`.

## Safety

This is an archival record only. No provider was installed or activated; no credentials were accessed; the immutable full mirror was not accessed.
