# DGM-MAT Provider State Freshness — Pre-change Archive

Date: 2026-10-09
Purpose: preserve exact canonical source before implementing atomic provider-state reconciliation and API freshness metadata.

Canonical source repository: AndreVazao/DGM-MAT
Archive repository: AndreVazao/DGM-MAT-OS

## Preserved files and SHA-256

- `runtime_state_store.py` — `24434ED6306438F5A4A827D422D611D6BC6A46411E41F478B6EC7729CD76BEF7`
- `runtime.py` — `03E23E22063569BD6A3B5E6E1EF1ED9F68E695117EBE66EE92E16CECE8DB775C`
- `reality_snapshot.py` — `976E3EAB86718A0414A5DC03209985453FFA9BF7692AD5E1DCDFDFBB973F54A7`
- `runtime_api.py` — `F2440BDEB9A47FB5A8D0013DE144418B1B9036DE7DED78171D640D81A837FC02`

These hashes were computed on the archived files immediately after copying from the canonical working tree. No source changes have been applied to the canonical repository at the time of this archive note.

Safety: no provider activation, no credential reads, no destructive cleanup. The immutable DGM-MAT-FULL-MIRROR path was not accessed.
