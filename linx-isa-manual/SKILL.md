---
name: linx-isa-manual
description: Professional instruction-set manual drafting and maintenance for the Linx ISA. Use when creating or editing ISA spec content (instruction entries, encoding diagrams/tables, precise pseudocode semantics, exceptions/interrupts, CSRs/privileged behavior, memory model), or when linting/reviewing the spec for ambiguity and internal consistency.
---

# Linx ISA Manual

## Overview

Draft ISA documentation that is unambiguous, testable, and cross-consistent with the compiler, emulator, and RTL.

When you need the concrete “why”, open `references/evidence.md` and cite the matching evidence ID in your change notes.

## Quick-start (Linx bring-up conventions)

1. Treat **Block ISA** as a first-class chapter, not “just branches”: define block boundaries, CARG, and the safety rule up front. (Evidence: MAN-01, MAN-02, MAN-03)
2. Treat **frame macro blocks** (`FENTRY`/`FEXIT`/`FRET.*`) as **standalone blocks**, not instructions that must be wrapped in `BSTART`/`BSTOP`. (Evidence: MAN-04, MAN-05)
3. Keep the spec **machine-checkable**: align prose with the generated JSON spec and codec tables (`isa/golden/v0.2/... → isa/spec/current/linxisa-v0.2.json → validate_spec → gen_*_codec`). (Evidence: MAN-06)
4. When introducing new block types or tooling, explicitly define the **three block forms** and their legality:
   - Coupled blocks: `BSTART … inst* … BSTOP`
   - Decoupled blocks: header-only descriptors + `B.TEXT <tpc>` to an out-of-line **linear** body that terminates at `BSTOP`
   - Template blocks: standalone “code template gen” blocks (`FENTRY/FEXIT/FRET*/MCOPY/MSET`) that MUST NOT appear inside `BSTART..BSTOP`. (Evidence: MAN-01, MAN-04)

## Workflow

### 1) Clarify the architectural context (do this first)

Collect (or confirm) the “global knobs” before writing details:

- XLEN / register width(s); endianness; instruction length(s)
- Privilege levels + CSR map (if any)
- Addressing: virtual/physical, page size, alignment rules
- Memory model: ordering, atomics, fences
- Exception + interrupt model (priority, nesting, precise state)

If these are unknown, write a short “Assumptions” block and mark it as a **normative TODO**.

### 2) Write or update an instruction entry

Use `assets/instruction_entry_template.md` as the canonical layout, but do not skip the Linx-specific sections below.

Add (or update) these Linx-specific items when applicable:

- **Block boundary behavior**: whether the instruction is a block marker, and whether it is valid only inside a block (e.g., `SETC.*`/`SETRET`). (Evidence: MAN-01, MAN-03)
- **Control-flow safety rule impact**: if the instruction creates a control-flow target, specify that it MUST target a block start marker (including template blocks). (Evidence: MAN-02, MAN-03)
- **Call header adjacency rule**: if documenting calls/returns, specify the `BSTART CALL` + `SETRET` “no instruction in between” rule. (Evidence: MAN-07)
- **Decoupled legality** (for any `B.*` header descriptor or `BSTART.<type>`):
  - State whether the instruction is valid in a decoupled **header**, a decoupled **body**, or both.
  - For headers, list the allowed descriptor set and require exactly one `B.TEXT` when decoupled.
  - For bodies, state the forbidden set (no block markers, no branches/calls/returns, no `B.*` descriptors, no templates) and the termination rule (`BSTOP` only).

For a new instruction:

1. Assign mnemonic + operand syntax (assembly grammar)
2. Specify encoding (bit fields, fixed bits, reserved bits)
3. Specify semantics in pseudocode (single-threaded, then memory/atomic notes)
4. Specify exceptions, traps, and privilege checks
5. Specify side effects (flags/CSRs, memory, timers, etc.)
6. Specify any undefined/implementation-defined behavior (avoid if possible)

For an edit:

- Update semantics and every dependent section: encoding constraints, exceptions, and notes.
- Add a “Compatibility” note if behavior changed vs earlier revisions.

### 3) Ensure the spec is executable (testability)

For each instruction, ensure you can write at least:

- 1 directed assembly test (edge cases)
- 1 negative test (illegal encoding, privilege fault, misalignment)
- 1 differential check (emulator vs RTL, if available)

### 4) Lint for ambiguity and consistency

Run the linter:

```bash
python3 "$CODEX_HOME/skills/linx-isa-manual/scripts/spec_lint.py" path/to/spec.md
```

Then manually check the “sharp edges” list below and the Block ISA checklist in `references/instruction_checklist.md`. (Evidence: MAN-01, MAN-02)

## Writing rules (keep it professional and precise)

- Prefer RFC-2119 style terms for requirements: **MUST**, **MUST NOT**, **SHOULD**, **MAY**.
- Avoid weasel words: “usually”, “typically”, “fast”, “small”, “simple”, “some”.
- Define every term that could be misread (e.g., “word”, “aligned”, “sign-extend”).
- State behavior for every bit pattern: either defined, reserved (and how it traps), or illegal.
- Avoid hidden state. If something depends on microarchitecture, call it implementation-defined.
- Specify all width/extension rules explicitly (zero-extend vs sign-extend, truncation).
- Specify PC update precisely (fall-through vs branch target, alignment requirements).

## Sharp edges checklist (common bring-up bugs)

- Immediate sign-extension and shift-mask behavior
- Zero register / partial register writes (if any)
- Misaligned accesses: trap vs split vs undefined
- Reserved bits: ignore vs trap vs must-be-zero
- Flag updates: per-instruction vs global rules
- Memory ordering: what fences/atomics actually guarantee
- Exceptions: priority, precise state, side effects when trapping

## Decoupled block entry template (copy/paste)

Use this when documenting a new decoupled block type (e.g. `BSTART.TMA`, `BSTART.CUBE`, `BSTART.VPAR/VSEQ`):

- **Header form**: `BSTART.<type>` then only `B.*` header descriptors; header ends at `BSTOP` or implicitly at the next block start marker.
- **Body pointer**: `B.TEXT <tpc>` is required exactly once in the header; `<tpc>` points to the out-of-line body.
- **Body form**: linear snippet beginning at `<tpc>`; MUST terminate at `BSTOP`/`C.BSTOP`.
- **Forbidden in body**: any `BSTART.*`, any template block, any branch/jump/call/ret, any `B.*` header descriptor.
- **Return rule**: on body `BSTOP`, resume at the header continuation PC.
- **Trap semantics**: specify what `TRAPNO/TRAPARG0/EBARG/ECSTATE.BI` report when trapping in header vs body.

## Resources

- Templates: `assets/isa_manual_outline.md`, `assets/instruction_entry_template.md`
- Reference: `references/style_guide.md`, `references/instruction_checklist.md`, `references/evidence.md`
- Tooling: `scripts/spec_lint.py`
