---
name: linx-llvm-backend
description: LLVM backend bring-up and maintenance for the Linx ISA. Use when implementing or changing Linx codegen/MC support (TableGen, registers, instruction selection, asm/disasm, object emission, ABI/calling convention), debugging miscompiles, or adding LLVM lit/FileCheck tests for Linx.
---

# Linx LLVM Backend

## Overview

Implement and debug a production-quality LLVM backend for Linx, with a bias toward testability and minimal divergence between spec, compiler, emulator, and RTL.

When you need the concrete “why”, open `references/evidence.md` and cite the matching evidence ID in your change notes.

## Bring-up invariants (Linx-specific, do not violate)

- Treat **Block ISA** as the architectural control-flow model: every MachineBasicBlock must map to a block that begins with a block start marker and commits at a block boundary. (Evidence: LLVM-01, LLVM-02)
- Treat `FENTRY`/`FEXIT`/`FRET.*` as **standalone blocks**; do not surround them with extra `BSTART`/`BSTOP` or prologue/epilogue stack micro-ops. (Evidence: LLVM-03)
- Preserve the **call header adjacency** rule: `BSTART CALL, <target>` and the return-address materialization (`SETRET`/`C.SETRET`) must be adjacent. (Evidence: LLVM-04)
- Decoupled block lowering is **not optional** for bring-up:
  - Tile blocks (`BSTART.TMA`/`BSTART.CUBE`) MUST be emitted as decoupled headers with a `B.TEXT` body pointer, and the referenced body MUST be linear and terminate at `C.BSTOP`.
  - For the initial compiler, tile blocks may use a per-function **empty body stub** (`.__linx_empty_body`) that contains only `C.BSTOP`. (Keep header-only semantics.) (Evidence: LLVM-02)

## Core workflow (add or modify an instruction)

1. Start from the ISA spec: encoding, semantics, operand constraints, trap behavior.
2. Update/generate TableGen from the JSON spec when possible; avoid hand-maintaining mask/match in multiple places. (Evidence: LLVM-05)
3. Ensure isel correctness:
   - Prefer TableGen patterns when semantics match exactly.
   - Use custom lowering only when necessary (special flags, multi-insn sequences, etc.).
4. Update the MC layer: asm parser, printer, disassembler, and encodings.
5. Update ABI as needed: calling convention, stack alignment, callee-saved, varargs, red zone, TLS, etc.
6. Add tests (do not skip):
   - `CodeGen` tests: `llc` output with `FileCheck`.
   - `MC` tests: `llvm-mc` asm/disasm round-trips and encoding bytes.
7. Run the smallest relevant test set first; then run full backend tests.

## Debugging miscompiles / codegen regressions

- Reduce to a minimal IR reproducer; check `-O0` vs `-O2`.
- Use verifier flags: `-verify-machineinstrs` and `-verify-dom-info`.
- Use pass debugging: `-print-after-all`, `-stop-after=...`, `-debug-only=...` (as applicable).
- Compare outputs: assembly, MIR, object bytes (endianness + relocations).

## Build failures you will hit again (fix them correctly)

- `error: no member named 'starts_with' in 'std::string'` (C++17 build): replace with `StringRef` helpers or equivalent; do not bump the whole backend to C++20. (Evidence: LLVM-06)
- `error: member access into incomplete type 'const MCAsmInfo'`: include the correct MC header (`llvm/MC/MCAsmInfo.h`) in any file that calls `printExpr`. (Evidence: LLVM-07)
- `error: invalid variant 'function'` on `type foo,@function`: ensure the emitted directive is the ELF form (`.type foo,@function`) and matches LLVM’s asm printer expectations. (Evidence: LLVM-08)

## Bring-up milestones (suggested order)

- Assembler/disassembler + encoding sanity
- `llc` can emit correct asm for simple arithmetic and branches
- Correct function calls + stack frame (ABI)
- Correct loads/stores + alignment and endianness
- Relocations/object emission (link a “hello world”; then prove PLT/shared-lib relocations) (Evidence: LLVM-09)
- Debug info + unwind (if needed)

## References

Read these when you need more detail:

- `references/backend_checklist.md` (milestones + “done means…”)
- `references/test_patterns.md` (lit/FileCheck patterns for new instructions)
- `references/common_flags.md` (useful `llc/opt/llvm-mc` flags)
- `references/evidence.md` (PRs/sessions/commits that motivated the rules)
