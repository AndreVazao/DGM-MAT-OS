# Archived legacy execution engine lineage

Date: 2026-10-08

These files were quarantined from canonical DGM-MAT after historical and structural audit.

Origin: Phase 15-17 lineage, introduced in commit 8135a73 on 2026-05-23.

Findings:
- ExecutionEngine has no production callers and only an import-only historical test.
- ExecutionEngine.start_execution calls WorktreeManager with three arguments although the current WorktreeManager accepts two, so the old path is not a trustworthy execution route.
- WorktreeManager and BranchManager have no production callers outside the old ExecutionEngine.
- RepairLoop, RollbackEngine, MergeGuard, ExecutionContext and ExecutionModels have no production callers.
- BranchManager and MergeGuard were only exercised by a small logic test, not by the canonical runtime.
- GitUtils is NOT archived here because it remains actively used by repository/import infrastructure.

This archive is historical evidence only. It is not a runtime dependency and must not be auto-imported or executed.

Canonical execution must continue to be derived from the currently proven runtime/queue path and future verified execution components.
