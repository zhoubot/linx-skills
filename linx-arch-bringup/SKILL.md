---
name: linx-arch-bringup
description: Computer-architecture guidance for Linx ISA bring-up. Use when defining or reviewing ISA/ABI/microarchitecture decisions (pipeline, hazards, privilege, CSRs, interrupts, memory ordering, caches), deriving bring-up checklists, or turning architecture intent into compiler/emulator/RTL requirements and tests.
---

# Linx Architecture Bring-up

## Overview

Turn “architecture intent” into precise requirements, implementation plans, and bring-up tests across spec, compiler, emulator, and RTL.

When you need the concrete “why”, open `references/evidence.md` and cite the matching evidence ID in your change notes.

## Linx-specific architectural constraints (Block ISA)

- Define the **block-structured control-flow contract** up front (block start markers, block boundaries, and CARG lifetime). (Evidence: ARCH-01)
- Enforce the **safety rule** as an architectural property (targets must land on block start markers; otherwise exception). (Evidence: ARCH-01)
- Treat `FENTRY`/`FEXIT`/`FRET.*` as standalone blocks when defining ABI/function-boundary behavior. (Evidence: ARCH-02)
- Preserve the **call header adjacency** rule (`BSTART CALL` + `SETRET` adjacent). (Evidence: ARCH-03)

## Workflow (architecture -> implementation)

1. Write/confirm the architectural contract (spec-level):
   - Programmer-visible state, privilege, exceptions, memory model
2. Choose microarchitecture:
   - Pipeline stages, forwarding, stall rules, branch strategy
   - Optional features: caches, MMU, atomics, debug
3. Define interfaces between blocks:
   - Fetch/decode/execute/mem/wb, CSR, interrupt controller
4. Define bring-up checkpoints:
   - Minimal boot sequence and “first light”
   - Conformance tests per feature
5. Define cross-check strategy:
   - Emulator as reference model
   - Commit trace schema shared by RTL and emulator

## Performance/benchmark deliverables (bring-up reality)

For each benchmark target, plan to produce:

- static instruction count (from objdump/disassembly)
- dynamic instruction count + instruction histogram (from emulator tracing/instrumentation)

(Evidence: ARCH-04)

## High-value early decisions (avoid rework)

- Instruction retirement model (precise traps? one insn commit per cycle?)
- Alignment and access splitting rules
- CSR semantics: RO/W1C/WARL-like behavior, reset values
- Memory ordering: what is guaranteed without fences
- ABI: stack alignment, callee-saved, syscall convention

## Alignment checklist (spec → compiler → emulator → RTL)

Use this list when adding or changing any of these “stack-wide” contracts:

- **Decoupled blocks**
  - Define header-only legality + required `B.TEXT` (spec)
  - Compiler emits `B.TEXT` + out-of-line linear bodies (plus empty-body stubs where appropriate)
  - Emulator implements header→body→return execution and traps on illegal body instructions
  - RTL/pyCircuit/Janus implement the same state machine and expose `EBARG` + `ECSTATE.BI` fields needed for restart
- **Template blocks (restartable)**
  - Define template progress and restart contracts via `EBARG` + `ECSTATE.BI` (+ ext-context metadata/pointer when used)
  - Emulator executes “one step” per helper/iteration so interrupts can land between steps
  - RTL implements a micro-op sequencer with precise restart from saved `EBARG` state
- **TTBR0/TTBR1 MMU + IOMMU**
  - Lock down v0.2 profile: 4K, 48-bit canonical VA, permission bits, fault reporting (`TRAPNO` + `TRAPARG0`)
  - QEMU page-walk + TLB behavior matches the spec subset
  - Linux programs TTBR/TCR/MAIR and handles page faults without skipping work
  - RTL integrates MMU/IOMMU with LSU/TMA ordering rules

## Outputs to produce

- Architecture spec deltas + rationale
- A bring-up checklist with “done means…”
- A trace schema for difftest
- A minimal test suite map (feature -> tests)

## References

- `references/bringup_checklist.md`
- `references/architecture_template.md`
- `references/evidence.md`
