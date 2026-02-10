# Evidence index (linx-isa-manual)

Use these IDs to justify spec/wording changes (e.g., in PR descriptions or review replies).

## MAN-01 — Block ISA is the architectural control-flow model

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (overview; defines block boundaries, block-granular execution model, and CARG).

## MAN-02 — Safety rule: all control-flow targets must be block start markers

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (states “every architectural control-flow target … must point at a block start marker”; branching into non-markers raises an exception).

## MAN-03 — Branch targets may be template macro blocks (not just explicit `BSTART.*`)

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (example note: labels must refer to a block start marker such as `BSTART.*` or template blocks like `FENTRY`/`FRET.*`).

## MAN-04 — `FENTRY`/`FEXIT`/`FRET.*` are standalone blocks (do not wrap in `BSTART`/`BSTOP`)

Source: Codex session `019c1e50-4ffb-7380-893a-f8ed8426ee2a` user message in `/Users/zhoubot/.codex/sessions/2026/02/02/rollout-2026-02-02T20-25-05-019c1e50-4ffb-7380-893a-f8ed8426ee2a.jsonl` (explicitly requests removing surrounding `C.BSTART`/`C.BSTOP` around `FRET.STK`).

Supporting source: QEMU commit `dc8b695a28` in `/Users/zhoubot/qemu` (comment: bring-up toolchain emits standalone frame macro blocks `FENTRY/FEXIT/FRET.*` that should be treated as block start markers).

## MAN-05 — `C.BSTOP` is all-zeros in the 16-bit space; decode/loader bugs can surface as all-zero fetches

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (note about `C.BSTOP` being encoded as all-zeros in the 16-bit space).

Supporting source: Cursor transcript `/Users/zhoubot/.cursor/projects/Users-zhoubot-qemu/agent-transcripts/9422c463-b686-4556-b4d1-2540da470b1d.txt` (debugging narrative around `linx_insn_decode_fail ... insn=0x00000000 len=2`, interpreted as `C.BSTOP` and tied to loader/offset issues).

## MAN-06 — Canonical machine-readable spec pipeline (isa.txt → JSON spec → generated codec tables)

Source: `/Users/zhoubot/linxisa/tools/isa/README.md` (commands for `extract_isa_txt.py`, `validate_spec.py`, and codec generation; establishes JSON as a single source for mask/match + field extraction).

## MAN-07 — Call header adjacency rule (`BSTART CALL` + `SETRET`)

Source: `/Users/zhoubot/linxisa/docs/architecture/isa-manual/src/chapters/04_block_isa.adoc` (rule: `SETRET`/`C.SETRET` must appear immediately after a call-type block start marker; no instruction may be between them).

