# Evidence index (linx-llvm-backend)

Use these IDs to justify backend decisions (e.g., in PR descriptions, review replies, or design notes).

## LLVM-01 — Block ISA is the architectural control-flow model

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (Block Split overview + execution model; defines block boundaries and block-granular sequencing).

## LLVM-02 — Safety rule: all control-flow targets must be block start markers

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (safety rule; branching into non-markers raises an exception).

## LLVM-03 — Frame macro blocks are standalone blocks (do not wrap in extra `BSTART`/`BSTOP`)

Source: Codex session `019c1e50-4ffb-7380-893a-f8ed8426ee2a` user message in `/Users/zhoubot/.codex/sessions/2026/02/02/rollout-2026-02-02T20-25-05-019c1e50-4ffb-7380-893a-f8ed8426ee2a.jsonl` (explicitly requests emitting `FRET.STK ...` by itself).

## LLVM-04 — Call header adjacency (`BSTART CALL` + `SETRET`)

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (rule: `SETRET`/`C.SETRET` must appear immediately after a call-type block start marker; no instruction may be between them).

## LLVM-05 — Prefer generating TableGen/MC tables from the JSON spec

Source: `/Users/zhoubot/linxisa/compiler/llvm/LLVM_BACKEND_GUIDE.md` (documents generating TableGen from `isa/spec/current/linxisa-v0.2.json` via `tools/isa/gen_llvm_tablegen.py`).

Supporting source: `/Users/zhoubot/linxisa/tools/isa/README.md` (single-source JSON spec + codec generation used by multiple consumers).

## LLVM-06 — C++17 build: `std::string::starts_with` causes AsmParser compile failures

Source: Codex session `019c1e50-4ffb-7380-893a-f8ed8426ee2a` build log in `/Users/zhoubot/.codex/sessions/2026/02/02/rollout-2026-02-02T20-25-05-019c1e50-4ffb-7380-893a-f8ed8426ee2a.jsonl` (clang++ `-std=c++17`; error: “no member named 'starts_with' in 'std::string'” in `LinxISAAsmParser.cpp`).

## LLVM-07 — Missing `MCAsmInfo` include causes “incomplete type” errors

Source: Same build log as LLVM-06 (error: “member access into incomplete type 'const MCAsmInfo'” in `LinxISAAsmPrinter.cpp`; forward declaration in `llvm/MC/MCExpr.h`).

## LLVM-08 — ELF directive printing bug: `type foo,@function` rejected

Source: Codex session `019c3144-703b-79d3-a250-288fed10a978` output in `/Users/zhoubot/.codex/sessions/2026/02/06/rollout-2026-02-06T12-44-54-019c3144-703b-79d3-a250-288fed10a978.jsonl` (assembler error: “invalid variant 'function'” at `type test,@function` / `type target,@function`).

## LLVM-09 — PLT/shared-lib expectations and relocation types

Source: `/Users/zhoubot/linxisa/compiler/llvm/tests/run.sh` (checks for `R_LINX_B17_PLT`, presence of `.plt` in shared objects, `R_LINX_JUMP_SLOT`, and `.plt` disassembly containing `BSTART IND`).

## LLVM-10 — AsmParser/disassembler “sugar” around call headers and PC-relative symbolization

Source: Codex session `019c1edd-5936-7600-b973-9e2597a033f2` output in `/Users/zhoubot/.codex/sessions/2026/02/02/rollout-2026-02-02T22-59-08-019c1edd-5936-7600-b973-9e2597a033f2.jsonl` (AsmParser logic for fused `BSTART CALL, <target>, ra=<return>` syntax and error string “expected 'CALL' for fused BSTART 'ra=' syntax”; disassembler logic that fuses `BSTART ... CALL` + `SETRET` for printing; `.PCR` symbolization rules).

## LLVM-11 — Toolchain/QEMU bring-up uses ET_REL and PC-relative relocations

Source: Codex session `019c1edd-5936-7600-b973-9e2597a033f2` reasoning in `/Users/zhoubot/.codex/sessions/2026/02/02/rollout-2026-02-02T22-59-08-019c1edd-5936-7600-b973-9e2597a033f2.jsonl` (notes that QEMU loads relocatable ET_REL and expects relocation types like `R_LINX_B17_PCREL` to be applied by the loader).

## LLVM-12 — Current bring-up triples and baseline block emission

Source: `/Users/zhoubot/linxisa/docs/llvm_bringup_status.md` (2026-01-31 status: clang supports `-target linx64-linx-none-elf` and `-target linx32-linx-none-elf`; each MBB emits `C.BSTART.STD` at start and `BSTOP` at end).

