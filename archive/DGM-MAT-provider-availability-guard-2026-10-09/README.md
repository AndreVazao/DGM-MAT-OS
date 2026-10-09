# Provider availability guard archive — 2026-10-09

## Preserved original

- Canonical path before change: `core/providers/base/provider_base.py`
- Archived file: `provider_base.py`
- SHA-256 (source and archive, identical): `7F49E0A181831C3082160440ADB92F5A3280804AE2EF390242791F6F12E46DC5`

## Finding

A read-only runtime probe set `ProviderBase.health_metrics["status"] = "ok"` while leaving `last_check = 0`. The pre-change `is_available()` returned `True`, despite no health observation. This violated the recent distinction between status labels and observed health.

## Canonical correction

`ProviderBase.is_available()` now requires a non-zero `last_check` observation timestamp before it can return available for `ok` or `degraded` status. Cooldown remains unavailable and is not promoted automatically. Regression tests cover both rejection of an unobserved `ok` status and acceptance of a status with an observation marker.

## Safety

Only this exact source file was copied and hash-verified before modification. No provider adapter was installed or activated. The immutable `DGM-MAT-FULL-MIRROR` was not accessed.
