# Evidence index (linx-arch-bringup)

Use these IDs to justify architecture constraints and bring-up deliverables.

## ARCH-01 — Block ISA contract: safety rule, block boundaries, and CARG lifetime

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (defines Block Split model, safety rule, and CARG lifetime rules).

## ARCH-02 — Frame macro blocks (`FENTRY`/`FEXIT`/`FRET.*`) are standalone blocks in bring-up tooling

Source: Codex session `019c1e50-4ffb-7380-893a-f8ed8426ee2a` user message in `/Users/zhoubot/.codex/sessions/2026/02/02/rollout-2026-02-02T20-25-05-019c1e50-4ffb-7380-893a-f8ed8426ee2a.jsonl` (explicitly requests `FRET.STK` to be emitted by itself, without surrounding `C.BSTART`/`C.BSTOP`).

Supporting source: QEMU commit `dc8b695a28` in `/Users/zhoubot/qemu` (comment: bring-up toolchain emits standalone frame macro blocks).

## ARCH-03 — Call header adjacency (`BSTART CALL` + `SETRET`)

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (rule: `SETRET`/`C.SETRET` must appear immediately after a call-type block start marker).

## ARCH-04 — Benchmarks require dynamic counts and instruction histograms

Source: Codex session `019c30b7-01cb-7233-9201-7f18f7055aea` user message in `/Users/zhoubot/.codex/sessions/2026/02/06/rollout-2026-02-06T10-10-25-019c30b7-01cb-7233-9201-7f18f7055aea.jsonl` (requests report including “dynamic inst count from qemu” and “instruction histogram stats”).

## ARCH-05 — QEMU failure logs already expose block-control fields; include them in trace schemas

Source: `/Users/zhoubot/linxisa/example/generated/ctuning_run_after5_failed_illegal.log` (fatal logs include `pc`, `brtype`, `carg`, `cond`, and `tgt`).

