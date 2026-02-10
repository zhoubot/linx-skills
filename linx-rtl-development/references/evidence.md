# Evidence index (linx-rtl-development)

Use these IDs to justify RTL invariants and trace schema requirements.

## RTL-01 — Block ISA safety rule and block boundaries are architectural requirements

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (safety rule: control-flow targets must be block start markers; block boundaries and block-granular execution model; CARG lifetime rules).

## RTL-02 — Frame macro blocks (`FENTRY`/`FEXIT`/`FRET.*`) are treated as standalone blocks in bring-up

Source: Codex session `019c1e50-4ffb-7380-893a-f8ed8426ee2a` user message in `/Users/zhoubot/.codex/sessions/2026/02/02/rollout-2026-02-02T20-25-05-019c1e50-4ffb-7380-893a-f8ed8426ee2a.jsonl` (explicit request to emit `FRET.STK ...` by itself).

Supporting source: QEMU commit `dc8b695a28` in `/Users/zhoubot/qemu` (comment: bring-up toolchain emits standalone frame macro blocks `FENTRY/FEXIT/FRET.*`).

## RTL-03 — Bring-up failures already report `brtype/carg/cond/tgt`; match that in RTL commit logs

Source: `/Users/zhoubot/linxisa/example/generated/ctuning_run_after5_failed_illegal.log` (QEMU fatal logs include `pc`, `brtype`, `carg`, `cond`, `tgt`, and register dumps).

