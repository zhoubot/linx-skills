---
name: linx-mlir-pycircuit
description: pyCircuit + MLIR development for Linx CPU bring-up. Use when modifying the PYC MLIR dialect, passes, or tools (pyc-opt/pyc-compile), adding ops/types/lowerings, or regenerating golden outputs and regressions for the Linx CPU examples in pyCircuit.
---

# Linx pyCircuit MLIR

## Overview

Develop the pyCircuit (PYC) MLIR dialect and toolchain to model and compile the Linx CPU design into Verilog or C++ for bring-up.

When you need the concrete “why”, open `references/evidence.md` and cite the matching evidence ID in your change notes.

## Project constraints that drive design

- Keep PYC as a **backend-agnostic IR** for hardware components; keep the C++ and Verilog backends interface-aligned. (Evidence: PYC-01, PYC-02)
- Model **ready/valid** and (eventually) **multi-clock** behavior explicitly in IR contracts and templates, not ad-hoc in emitters. (Evidence: PYC-01, PYC-03)
- Keep Linx bring-up **trace-first**: always have a path to generate commit traces and pipeline visualizations (Konata/Perfetto) to debug mismatches quickly. (Evidence: PYC-04)

## Quick start (this repo)

From the pyCircuit repo root:

```bash
scripts/pyc build
scripts/pyc regen
scripts/pyc test
```

Key docs:

- `docs/USAGE.md` (Python DSL + JIT rules; debug/tracing)
- `docs/IR_SPEC.md` (PYC dialect contract)
- `docs/PRIMITIVES.md` (backend template “ABI”)
- `docs/VERILOG_FLOW.md` (open-source Verilog sim/lint)

## Common tasks

### Add or modify a PYC op/type

1. Update TableGen:
   - Ops: `pyc/mlir/include/pyc/Dialect/PYC/PYCOps.td`
   - Types: `pyc/mlir/include/pyc/Dialect/PYC/PYCTypes.td`
2. Rebuild (`scripts/pyc build`).
3. Implement verification/semantics in:
   - `pyc/mlir/lib/Dialect/PYC/` (dialect, ops, types)
4. Update lowering/codegen:
   - Verilog emitter: `pyc/mlir/lib/Emit/VerilogEmitter.cpp`
   - C++ emitter: `pyc/mlir/lib/Emit/CppEmitter.cpp`
   - Passes: `pyc/mlir/lib/Transforms/`
5. Add/refresh examples + golden outputs (`scripts/pyc regen`).

### Debug a lowering or pass

- Use `pyc-opt` to run individual passes.
- Dump IR between passes and reduce to a minimal `.pyc` file.
- Keep the IR contract in `docs/IR_SPEC.md` as the source of truth.

## Linx CPU bring-up hooks (in this repo)

- Design: `examples/linx_cpu_pyc/`
- SV testbench + program images: `examples/linx_cpu/`
- Golden outputs: `examples/generated/linx_cpu_pyc/`
- Regression helper: `bash tools/run_linx_cpu_pyc_cpp.sh`

### Alignment tasks (when the ISA contract changes)

When the Linx ISA “contract” changes (Block forms, templates, MMU/IOMMU), treat these as required updates for the pyCircuit/Janus models:

- **Decode**: add opcode recognition for `B.TEXT`, `B.IOR`, `B.ATTR`, `TLB.*`, and `HL.SSRGET/HL.SSRSET` full IDs.
- **Control state**: implement decoupled header→body→return and body legality checks.
- **Template engine**: model template blocks as restartable step sequences (progress recorded in an `EBARG`/`ECSTATE.BI`-compatible struct).
- **Memory**: add MMU/IOMMU hooks (even if initially identity) so the call sites are stable.
- **Regressions**: add/refresh directed programs for:
  - Decoupled headers (`B.TEXT` present, empty-body stubs for tile ops)
  - Template restartability (fault mid-template, resume without double-commit)
  - TTBR0/TTBR1 basic translation + IOMMU tile translation

## Trace export (Konata / Perfetto)

If your tree includes PR #1 “Add pipeview, swimlane” (`zhoubot/pyCircuit`, head `ea63425c3f...`), the C++ TB supports:

- Konata pipeview (O3PipeView): `-p1` or `--pipeview 1` (output via `--pipfile`)
- Perfetto trace JSON: `--swimlane 1` (output via `--swimfile`)
- Boot PC override: `--boot-pc <addr>` (also supports `PYC_BOOT_PC`)

(Evidence: PYC-04)

## References

- `references/repo_map.md`
- `references/add_op_checklist.md`
- `references/debugging.md`
- `references/evidence.md`
