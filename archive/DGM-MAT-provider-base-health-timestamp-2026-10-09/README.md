# ProviderBase health timestamp archive — 2026-10-09

Preserved the exact pre-change `core/providers/base/provider_base.py` before changing health timestamp semantics. Source and archived copy SHA-256 matched.

The original base `check_health()` updated `last_check` when called despite explicitly stating it could not prove remote health. The canonical fix adds `last_check_attempt`, reserves `last_check` for an actual observation, and prevents the base implementation from returning a manually assigned healthy status without a concrete adapter override.

Historical copy only. Do not reintroduce the old timestamp/health semantics.
