#!/usr/bin/env python3
"""
Parse QEMU trace logs for Linx and produce:
  - dynamic instruction count
  - decode-fail count
  - length histogram
  - (optional) mnemonic histogram via the JSON spec

Intended inputs:
  - QEMU trace-events like:
      linx_insn_exec PC=0x... insn=0x... len=2 <extra>
      linx_insn_decode_fail PC=0x... insn=0x... len=2 (decode failed)
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path


TRACE_EXEC_RE = re.compile(
    r"\blinx_insn_exec\b.*?\bPC=0x(?P<pc>[0-9a-fA-F]+)\b.*?\binsn=0x(?P<insn>[0-9a-fA-F]+)\b.*?\blen=(?P<len>\d+)\b"
)
TRACE_FAIL_RE = re.compile(
    r"\blinx_insn_decode_fail\b.*?\bPC=0x(?P<pc>[0-9a-fA-F]+)\b.*?\binsn=0x(?P<insn>[0-9a-fA-F]+)\b.*?\blen=(?P<len>\d+)\b"
)


@dataclass(frozen=True)
class Form:
    mnemonic: str
    length_bits: int
    mask: int
    match: int
    fixed_bits: int


def _parse_int(v: object) -> int:
    if v is None:
        return 0
    if isinstance(v, int):
        return v
    if isinstance(v, str):
        s = v.strip().lower().replace("_", "")
        if s.startswith("0x"):
            return int(s, 0)
        if s and all(c in "0123456789abcdef" for c in s):
            return int(s, 16)
        return int(s, 10)
    return int(v)  # fallback


def _read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(encoding="utf-8", errors="replace")


def _load_spec_forms(spec_path: Path) -> dict[int, list[Form]]:
    spec = json.loads(_read_text(spec_path))

    out: dict[int, list[Form]] = {}
    for inst in spec.get("instructions", []):
        enc = inst.get("encoding", {}) or {}
        length_bits = int(enc.get("length_bits") or inst.get("length_bits") or 0)
        parts = list(enc.get("parts", []))
        if not length_bits or not parts:
            continue

        # Combine part-local mask/match into an instruction-wide mask/match.
        offsets: list[int] = []
        off = 0
        for p in parts:
            offsets.append(off)
            off += int(p.get("width_bits") or 0)

        if off != length_bits:
            # Skip malformed entries.
            continue

        mask = 0
        match = 0
        for part_index, part in enumerate(parts):
            shift = offsets[part_index]
            part_mask = _parse_int(part.get("mask"))
            part_match = _parse_int(part.get("match"))
            mask |= part_mask << shift
            match |= part_match << shift

        fixed_bits = int(mask.bit_count())
        mnemonic = str(inst.get("mnemonic") or "")
        if not mnemonic:
            continue

        out.setdefault(length_bits, []).append(
            Form(
                mnemonic=mnemonic,
                length_bits=length_bits,
                mask=mask,
                match=match,
                fixed_bits=fixed_bits,
            )
        )

    for bits in list(out.keys()):
        out[bits].sort(key=lambda f: (-f.fixed_bits, f.mnemonic))
    return out


def _decode_mnemonic(forms_by_bits: dict[int, list[Form]], length_bytes: int, insn: int) -> str | None:
    length_bits = length_bytes * 8
    forms = forms_by_bits.get(length_bits)
    if not forms:
        return None
    mask = (1 << length_bits) - 1
    val = insn & mask
    for f in forms:
        if (val & f.mask) == f.match:
            return f.mnemonic
    return None


def _fmt_table(rows: list[tuple[str, int]], top: int) -> str:
    rows = rows[:top]
    if not rows:
        return "(none)"
    w0 = max(len(r[0]) for r in rows)
    w1 = max(len(str(r[1])) for r in rows)
    out = []
    for name, count in rows:
        out.append(f"{name:<{w0}}  {count:>{w1}}")
    return "\n".join(out)


def parse_args(argv: list[str]) -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Summarize Linx QEMU trace logs (dynamic counts + histograms).")
    p.add_argument("trace", help="Trace log file (text)")
    p.add_argument(
        "--spec",
        help="Path to isa/spec JSON (for mnemonic decoding). Defaults to ~/linxisa/isa/spec/current/linxisa-v0.2.json when present.",
        default=None,
    )
    p.add_argument("--top", type=int, default=40, help="Show top-N mnemonics/raw encodings.")
    p.add_argument("--no-decode", action="store_true", help="Do not attempt to decode mnemonics (even if --spec exists).")
    return p.parse_args(argv)


def main(argv: list[str]) -> int:
    args = parse_args(argv)

    trace_path = Path(args.trace)
    if not trace_path.exists():
        print(f"error: trace not found: {trace_path}", file=sys.stderr)
        return 2

    spec_path: Path | None = None
    if not args.no_decode:
        if args.spec:
            spec_path = Path(args.spec)
        else:
            default = Path.home() / "linxisa" / "isa" / "spec" / "current" / "linxisa-v0.2.json"
            if default.exists():
                spec_path = default

    forms_by_bits: dict[int, list[Form]] = {}
    if spec_path is not None:
        if not spec_path.exists():
            print(f"warning: spec not found: {spec_path} (mnemonic decoding disabled)", file=sys.stderr)
            spec_path = None
        else:
            forms_by_bits = _load_spec_forms(spec_path)

    exec_total = 0
    fail_total = 0
    len_hist: dict[int, int] = {}
    mnemonic_hist: dict[str, int] = {}
    raw_hist: dict[tuple[int, int], int] = {}

    for line in _read_text(trace_path).splitlines():
        m = TRACE_EXEC_RE.search(line)
        if m:
            exec_total += 1
            length = int(m.group("len"))
            insn = int(m.group("insn"), 16)
            len_hist[length] = len_hist.get(length, 0) + 1

            mnemonic = None
            if spec_path is not None:
                mnemonic = _decode_mnemonic(forms_by_bits, length, insn)
            if mnemonic is None:
                raw_hist[(length, insn)] = raw_hist.get((length, insn), 0) + 1
            else:
                mnemonic_hist[mnemonic] = mnemonic_hist.get(mnemonic, 0) + 1
            continue

        m = TRACE_FAIL_RE.search(line)
        if m:
            fail_total += 1
            continue

    print(f"trace: {trace_path}")
    if spec_path is not None:
        print(f"spec:  {spec_path}")
    print(f"exec:  {exec_total}")
    print(f"fail:  {fail_total}")

    print("\n-- Length histogram (bytes) --")
    for k in sorted(len_hist.keys()):
        print(f"{k:>2}  {len_hist[k]}")

    if spec_path is not None:
        print("\n-- Mnemonic histogram (top) --")
        rows = sorted(mnemonic_hist.items(), key=lambda kv: (-kv[1], kv[0]))
        print(_fmt_table(rows, args.top))

    print("\n-- Raw encodings (top; includes undecoded lengths) --")
    rows2 = sorted(raw_hist.items(), key=lambda kv: (-kv[1], kv[0][0], kv[0][1]))
    rows2_fmt: list[tuple[str, int]] = []
    for (length, insn), count in rows2:
        rows2_fmt.append((f"len={length} insn=0x{insn:08x}", count))
    print(_fmt_table(rows2_fmt, args.top))

    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
