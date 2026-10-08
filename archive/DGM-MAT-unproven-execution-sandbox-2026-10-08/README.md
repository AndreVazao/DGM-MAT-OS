# DGM-MAT — Unproven Execution Fabric and Sandbox Archive

Date: 2026-10-08

## Why this was quarantined

A structural audit found that `core/execution_fabric` is not part of the proven current DGM-MAT runtime path. The canonical mission path is governed through `MissionEngine -> SafeActionQueue -> MISSION_EXECUTION handler` rather than this legacy fabric.

The fabric also contained code that is not trustworthy as a production execution boundary:

- `ExecutionFabric.start()` launches a blocking autonomous loop with no proven runtime owner.
- `ExecutionSupervisor.validate_plan()` always returns `True`.
- `ExecutionCycles._run_cycle()` is a no-op.
- `ExecutionMemory` is process-local memory only.
- `ExecutionRecovery` is mostly placeholder behavior.
- `AutonomousExecutor` calls `WorktreeRuntime.create_sandbox()` and `cleanup_sandbox()`, but the actual `WorktreeRuntime` does not implement those methods.
- `SafePatchEngine` contains a simple text-pattern risk scanner, not a complete governed patch boundary.
- `BranchOrchestrator` can merge directly without being proven as the canonical approval path.

`core/sandbox` was also found to have no production callers. Its only canonical dependency was the orphaned `WorktreeRuntime` import from `core/execution_fabric`. Its tests exercised the historical subsystem rather than a live runtime path.

## Preserved material

The exact tracked state from the DGM-MAT `HEAD` immediately before quarantine is preserved here, including:

- `core/execution_fabric/`
- `core/sandbox/`
- `tests/execution_fabric/`
- `tests/sandbox/`

The archive contains both the extracted tree and `payload.tar` generated directly from Git, so recovery does not depend on the current working tree.

## Important distinction

This is a quarantine, not a claim that every implementation idea here is useless. Worktree isolation, command execution limits, patch inspection, state tracking, recovery concepts, and snapshots may be valuable later. They must re-enter through a new, tested contract owned by the current runtime/governance architecture.

## Re-entry requirements

Any future resurrection must demonstrate:

1. A real production caller in the current architecture.
2. Explicit ownership and lifecycle.
3. Deterministic tests against real behavior.
4. Human approval for consequential/destructive operations.
5. No placeholder success paths.
6. No direct bypass of `SafeActionQueue` or current governance boundaries.
7. Clear workspace/repository scope and cleanup semantics.
8. Recovery/idempotency behavior proven under interruption.

Never auto-import or execute this archive.
