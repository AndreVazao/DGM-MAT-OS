# Provider registry contract archive — 2026-10-09

Preserved the exact pre-change `core/provider_sync/provider_registry.py` before tightening explicit registration validation. Source and archive SHA-256 matched.

The old `register(name, adapter)` accepted a key different from `adapter.name` and silently overwrote a different adapter registered under the same key. The canonical contract now rejects both mismatched names and accidental replacement; registering the same instance under the same name remains idempotent.

Historical copy only. Do not reintroduce silent adapter replacement.
