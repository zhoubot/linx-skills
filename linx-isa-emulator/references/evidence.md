# Evidence index (linx-isa-emulator)

Use these IDs to justify emulator behavior and debugging workflows.

## EMU-01 — Block ISA execution model and CARG semantics

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (defines block boundaries, block-granular sequencing, and CARG lifetime rules).

## EMU-02 — Safety rule: control-flow targets must be block start markers

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (states the safety rule; branching to a non-marker raises an exception).

## EMU-03 — Template macro blocks are treated as block start markers

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (notes that valid targets include template blocks like `FENTRY`/`FRET.*`).

Supporting source: QEMU commit `dc8b695a28` in `/Users/zhoubot/qemu` (comment: bring-up toolchain emits standalone frame macro blocks `FENTRY/FEXIT/FRET.*` that should also be treated as BSTART markers).

## EMU-04 — Block ISA → QEMU TB mapping + `goto_tb` fast-path

Source: `/Users/zhoubot/linxisa/docs/qemu.md` (performance notes: translate one Linx block into one TB; use `goto_tb` when target is fixed and no `SETC.TGT` override).

## EMU-05 — Indirect dispatch fallback (`lookup_and_goto_ptr`) and target checks

Source: QEMU commit `dc8b695a28` in `/Users/zhoubot/qemu` (diff mentions `goto_tb` vs `lookup_and_goto_ptr`, and “jump target does not point to BSTART” checks).

## EMU-06 — `C.BSTOP` all-zeros and decode-fail symptom

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (note about `C.BSTOP` being encoded as all-zeros).

Supporting source: Cursor transcript `/Users/zhoubot/.cursor/projects/Users-zhoubot-qemu/agent-transcripts/9422c463-b686-4556-b4d1-2540da470b1d.txt` (debugging around `linx_insn_decode_fail PC=0x1001e insn=0x00000000 len=2` and interpreting it as `C.BSTOP` plus loader offset issues).

## EMU-07 — “Illegal instruction” is a recurring bring-up failure mode (needs a deterministic triage path)

Source: `/Users/zhoubot/linxisa/example/generated/ctuning_run_after5_failed_illegal.log` (many failures with `qemu: fatal: Linx: Illegal instruction`, including `pc`, `brtype`, `carg`, `cond`, and `tgt` fields).

Supporting source: QEMU commit `e02890d53d` in `/Users/zhoubot/qemu` (introduces `LINX_EXCP_ILLEGAL_INST` and trace events `linx_insn_exec` / `linx_insn_decode_fail` in `target/linx/trace-events`).

## EMU-08 — Instruction histogram/dynamic counts are an explicit deliverable for benchmarks

Source: Codex session `019c30b7-01cb-7233-9201-7f18f7055aea` user message in `/Users/zhoubot/.codex/sessions/2026/02/06/rollout-2026-02-06T10-10-25-019c30b7-01cb-7233-9201-7f18f7055aea.jsonl` (requests report including “dynamic inst count from qemu” and “instruction histogram stats”).

