"""
pdca_loop.py — reference implementation of the preflight/postflight PDCA loop.

The pattern (operator-named):
  preflight checklist  ->  do work  ->  postflight checklist  ->  cycle n+1
The agent loops until both gates are green. Receipts append to chain.jsonl as
HMAC-SHA256-chained lines. Stdlib only.

MIT licensed. Compose, fork, replace any piece.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
import time
from pathlib import Path
from typing import Any, Callable

# A check returns (passed: bool, reason: str). Empty reason on pass is fine.
Check = Callable[[Any], tuple[bool, str]]
# A provider takes a prompt-string and returns an output-string.
Provider = Callable[[str], str]

CHAIN_PATH = Path(os.environ.get("PDCA_CHAIN_PATH", "chain.jsonl"))
CHAIN_KEY = os.environ.get("PDCA_CHAIN_KEY", "obsidian-spider-default-key").encode()


def _last_hash(path: Path) -> str:
    """Return the hash of the last receipt in chain.jsonl, or '0' * 64 if empty."""
    if not path.exists() or path.stat().st_size == 0:
        return "0" * 64
    with path.open("rb") as f:
        f.seek(0, 2)  # end
        size = f.tell()
        block = min(4096, size)
        f.seek(size - block)
        tail = f.read().decode("utf-8", errors="replace").strip().splitlines()
    return json.loads(tail[-1])["hash"] if tail else "0" * 64


def _append_receipt(payload: dict[str, Any]) -> dict[str, Any]:
    """Append an HMAC-chained receipt. The chain breaks if any line is mutated."""
    prev = _last_hash(CHAIN_PATH)
    body = {"prev_hash": prev, "ts": time.time(), **payload}
    body_bytes = json.dumps(body, sort_keys=True, separators=(",", ":")).encode()
    body["hash"] = hmac.new(CHAIN_KEY, body_bytes, hashlib.sha256).hexdigest()
    with CHAIN_PATH.open("a", encoding="utf-8") as f:
        f.write(json.dumps(body) + "\n")
    return body


def _run_checks(checks: list[Check], payload: Any) -> list[tuple[str, bool, str]]:
    """Run each check and return [(name, passed, reason), ...]."""
    out = []
    for c in checks:
        try:
            ok, reason = c(payload)
        except Exception as e:  # check itself is buggy; treat as fail
            ok, reason = False, f"check_exception:{type(e).__name__}:{e}"
        out.append((getattr(c, "__name__", repr(c)), bool(ok), reason or ""))
    return out


def run_pdca_cycle(
    task: dict[str, Any],
    providers: list[Provider],
    preflight: list[Check],
    postflight: list[Check],
    max_iters: int = 5,
) -> dict[str, Any]:
    """Run preflight -> do -> postflight, looping up to max_iters until both gates green.

    `providers[0]` is used as the worker; additional providers can be invoked
    by extending this loop or composing with `examples/multi_provider_pBFT.py`.
    """
    if not providers:
        raise ValueError("at least one provider is required")
    worker = providers[0]
    final = {"task": task, "iterations": [], "done": False}

    for i in range(1, max_iters + 1):
        pre = _run_checks(preflight, task)
        pre_green = all(p for _, p, _ in pre)
        receipt_pre = _append_receipt(
            {"kind": "preflight", "iter": i, "checks": pre, "green": pre_green}
        )
        print(f"[iter {i}] preflight green={pre_green}  hash={receipt_pre['hash'][:12]}")
        if not pre_green:
            # Preflight not satisfied — give the worker a chance to repair the input.
            task["input"] = worker(json.dumps({"repair_input": task, "failures": pre}))
            continue

        output = worker(task.get("input", ""))
        post_payload = {**task, "output": output}
        post = _run_checks(postflight, post_payload)
        post_green = all(p for _, p, _ in post)
        receipt_post = _append_receipt(
            {"kind": "postflight", "iter": i, "checks": post, "green": post_green,
             "output_preview": output[:200]}
        )
        print(f"[iter {i}] postflight green={post_green}  hash={receipt_post['hash'][:12]}")

        final["iterations"].append({"iter": i, "pre": pre, "post": post, "output": output})
        if pre_green and post_green:
            final["done"] = True
            final["output"] = output
            break
        # Postflight failed; feed reasons back as repair signal for next iter.
        task["input"] = worker(
            json.dumps({"repair_output": output, "failures": [r for _, ok, r in post if not ok]})
        )
    _append_receipt({"kind": "cycle_end", "done": final["done"], "iters": len(final["iterations"])})
    return final
