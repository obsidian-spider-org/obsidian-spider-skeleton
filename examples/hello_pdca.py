"""
hello_pdca.py — trivial PDCA cycle. Run me; read chain.jsonl after.

  preflight: input is non-empty
  do step:   uppercase the input
  postflight: output is uppercase  +  one synthetic Loki detector

No external deps. Python 3.10+.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pdca_loop import run_pdca_cycle  # noqa: E402


def preflight_input_nonempty(task):
    s = (task.get("input") or "").strip()
    return (bool(s), "" if s else "input is empty or whitespace")


def do_uppercase(prompt: str) -> str:
    """Worker provider. In real use this is an LLM call; here it is a pure fn."""
    return prompt.upper()


def postflight_output_uppercase(payload):
    out = payload.get("output", "")
    return (out == out.upper() and bool(out), "" if out else "output is empty")


def loki_no_apology(payload):
    """Synthetic Loki: the worker apologizes inside its output. Show extension shape."""
    out = (payload.get("output") or "").lower()
    bad = any(p in out for p in ["i'm sorry", "i apologize", "my apologies"])
    return (not bad, "" if not bad else "output contains an apology phrase (synthetic Loki)")


if __name__ == "__main__":
    task = {"input": "hello, swarm"}
    result = run_pdca_cycle(
        task=task,
        providers=[do_uppercase],
        preflight=[preflight_input_nonempty],
        postflight=[postflight_output_uppercase, loki_no_apology],
        max_iters=3,
    )
    print(f"\ndone={result['done']}  output={result.get('output')!r}")
    print("see chain.jsonl for the HMAC-chained receipts.")
