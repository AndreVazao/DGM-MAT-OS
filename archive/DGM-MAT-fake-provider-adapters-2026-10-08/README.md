# DGM-MAT fake provider adapters archive

Archived 2026-10-08 during architecture surgery.

## Removed from canonical DGM-MAT

- `core/model_router/local_provider_adapter.py`
- `core/providers/ollama/ollama_provider.py`

## Reason

Reference tracing found no imports or runtime callers for either module. Both exposed health/capability behavior that was not grounded in real provider state:

- `LocalProviderAdapter.check_health()` always returned `True` and explicitly described itself as simulated.
- `OllamaProvider.check_health()` forced status to `ok` without checking whether Ollama was running.
- `OllamaProvider.chat()` returned a placeholder response instead of contacting a local Ollama instance.

Keeping these modules in the canonical tree could cause capability discovery or future integrations to mistake simulation for reality.

## Rule

Real Ollama support must be implemented only through a provider contract with an actual connectivity/model check and a real request path, followed by tests. This archive is evidence/history only and must not be auto-imported or executed.
