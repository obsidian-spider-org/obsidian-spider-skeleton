#!/usr/bin/env python3
"""verify_chain.py — verify a chain.jsonl file end-to-end. ~30 lines, stdlib only.

Walks every entry, recomputes each HMAC, confirms each prev_hash matches the
prior line's hash. Returns 0 on success, 2 on tamper.

Usage:
    python verify_chain.py [path-to-chain.jsonl]   # defaults to ./chain.jsonl
"""
import hashlib, hmac, json, sys
from pathlib import Path

DEFAULT_KEY = b"obsidian-spider-default-key"  # override via env PDCA_CHAIN_KEY


def canonical(payload: dict) -> bytes:
    body = {k: v for k, v in payload.items() if k not in ("hash", "prev_hash")}
    return json.dumps(body, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def verify(path: Path, key: bytes = DEFAULT_KEY) -> int:
    lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
    if not lines:
        print(f"empty chain: {path}"); return 2
    prev = "0" * 64
    for i, line in enumerate(lines):
        entry = json.loads(line)
        if entry.get("prev_hash", prev) != prev:
            print(f"FAIL line {i+1}: prev_hash mismatch (expected {prev[:16]}..., got {entry.get('prev_hash','')[:16]}...)")
            return 2
        expected = hmac.new(key, prev.encode() + canonical(entry), hashlib.sha256).hexdigest()
        if entry.get("hash") != expected:
            print(f"FAIL line {i+1}: hash mismatch (expected {expected[:16]}..., got {entry.get('hash','')[:16]}...)")
            return 2
        prev = entry["hash"]
    print(f"OK: {len(lines)} entries verified; head={prev[:16]}...")
    return 0


if __name__ == "__main__":
    p = Path(sys.argv[1] if len(sys.argv) > 1 else "chain.jsonl")
    if not p.exists():
        print(f"chain not found: {p}"); sys.exit(2)
    sys.exit(verify(p))
