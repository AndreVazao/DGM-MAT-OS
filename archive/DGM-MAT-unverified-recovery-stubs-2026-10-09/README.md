# Archived unverified recovery stubs — 2026-10-09

These are byte-for-byte copies of the canonical pre-change recovery files preserved before the truthfulness fix.

SHA-256 was checked on both source and archive copies and matched for all three files:
- `provider_recovery.py`
- `runtime_recovery.py`
- `repair_chain.py`

Reason for preservation: the original provider/runtime recovery functions returned `True` without performing recovery, and an empty repair chain also returned `True`. These behaviors could cause false-positive recovery records.

The canonical fix intentionally returns failure/unavailable until a real recovery action can be performed and verified. This archive is historical evidence only; do not reintroduce the old success semantics.
