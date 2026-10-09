# Unverified provider routing, benchmark, and sync archive — 2026-10-09

The following canonical files were copied to this archive before any quarantine/removal. SHA-256 was computed for every source and destination; all 16 pairs matched.

## Archived source paths

- `core/providers/performance/health_monitor.py`
- `core/providers/performance/provider_affinity_engine.py`
- `core/providers/performance/provider_benchmark.py`
- `core/providers/performance/provider_capability_matrix.py`
- `core/providers/performance/provider_cost_optimizer.py`
- `core/providers/performance/provider_memory_profiles.py`
- `core/providers/performance/provider_routing_engine.py`
- `core/providers/performance/provider_scoring.py`
- `core/research/provider_benchmarking.py`
- `scripts/stress_test_providers.py`
- `core/provider_sync/provider_memory_sync.py`
- `core/provider_sync/provider_health.py`
- `core/provider_sync/sync_engine.py`
- `core/operator/provider_sync.py`
- `tests/provider_sync/test_sync.py`
- `tests/integration/test_provider_sync.py`

## Why these were preserved

- Performance/routing implementations contain fixed, heuristic, or unmeasured outputs and no productive canonical consumers were found for the individual classes. The only source reference to the routing engine outside itself is the incompatible stress script.
- The stress script imports provider adapters absent from the canonical source and calls an obsolete failover signature/field.
- The provider sync engine expects `provider_id`, `list_conversations()`, and `sync_conversation()`, which are not part of the current `ProviderBase` contract.
- The memory sync adapter calls `ProviderSync._sync_provider()`, which does not exist. Its health cache therefore records success/failure for attempted calls but does not prove real synchronization.
- The old integration file is a manual `validate()` script, not a pytest contract, and calls methods/attributes that the current facade does not provide.
- The operator facade's `sync_providers()` had no productive callers found; its only purpose was to import and invoke the unverified memory sync adapter.

## Quarantine rule

These files are historical evidence only. They must not be represented as operational provider capabilities. Canonical quarantine/removal is allowed only after checking the current source references and tests, and the replacement facade must fail closed rather than report a successful sync without implementation.

The empty `core/providers/performance/__init__.py` is intentionally not included and should remain unless a later package-structure audit proves it unnecessary.
