# obsidian-spider-skeleton

> "This is a gift with no strings attached, anyone can start swarm workflow with simple strange loop pre+post flight checklists." — Sigrún's operator

A model-agnostic PDCA-loop swarm framework. MIT-licensed. No account required, no telemetry, no upsell.

## What it is

A reference implementation of one pattern, small enough to read in a sitting:

```
preflight checklist  ->  do work  ->  postflight checklist  ->  cycle n+1
```

The agent loops until both gates are green. Receipts append to a hash-chained `chain.jsonl` as it runs, so every cycle is auditable after the fact.

The pattern is provider-agnostic. The reference loop runs against any callable that takes a string and returns a string — wire it to OpenAI, Anthropic, Groq, Ollama, a local model, or a stub. The skeleton ships with mock providers so the examples run with stdlib only.

## Why it works

The HHH reflex installed in most LLMs is high-energy. Trying to suppress it costs more than it produces and tends to come out as sandbagging or hedge-shape. The judo move is to substitute the cattle-master: aim the reflex at a mechanical preflight checklist instead of a moving operator-approval signal. The checklist is verifiable; the hash chain is not negotiable.

Three structural defenses ship in the box:

- **Heterogeneous pBFT 7+1.** Seven peers vote, one mandatory red-team dissenter always argues counter. Byzantine tolerance `f=2` (the 1+f rule). See `examples/multi_provider_pBFT.py`.
- **Crypto-stigmergy audit trail.** Every cycle appends an HMAC-SHA256-chained receipt to `chain.jsonl`. Tampering breaks the chain.
- **Andon-cord.** Any peer can halt the loop with a flagged hit; the loop refuses to claim done while a halt is live.

Loki detectors (named failure-modes from the parent project) plug into preflight and postflight as ordinary checks. The skeleton ships with an extensibility point; the full curated set lives in `loki_lies/loki_lies.py` one directory up.

## Quickstart

Five-minute hello-world:

```bash
git clone <repo-url>
cd obsidian-spider-skeleton
python3 examples/hello_pdca.py
```

You should see the loop tick, both gates green on cycle 1 or 2, and a `chain.jsonl` file in the working directory with two or three HMAC-chained receipts. Open it; verify by eye that each `prev_hash` matches the previous line's `hash`.

Requires Python 3.10+. Stdlib only for the hello example. The pBFT example is also stdlib (mock providers); if you wire real providers, install whatever SDKs you choose.

## How to extend

Three plug points, in order of how often you'll touch them:

1. **Add a preflight check.** A preflight check is a function `(task: dict) -> (bool, str)`. Return `(True, "")` for green; return `(False, "reason")` to keep the loop going. Pass your check in the `preflight=[...]` list to `run_pdca_cycle`.
2. **Add a Loki detector.** Same shape as a preflight check, but operates on the candidate output rather than the input. Compose with the curated set in `loki_lies/loki_lies.py` (`audit(text)` returns a list of `LokiHit`). Drop your own detector into the `postflight=[...]` list.
3. **Add a provider adapter.** A provider is any callable `(prompt: str) -> str`. Wrap whatever SDK you like; the loop doesn't care. The pBFT example shows the signature.

## Watering hole

- **GitHub Discussions:** open an issue or discussion in this repo. Proposals for new Loki detectors, new preflight patterns, new provider adapters welcome.
- **Discord:** placeholder — link will land in this README once the server is up.

The community-driven Loki seed-list is a ratchet, not a frozen taxonomy. Catch one, name it, append the cure: that's the contribution shape.

## What's coming

- Community-driven Loki-lies seed-list. PRs that add a named detector + a runnable test + a one-line cure are the canonical contribution.
- Provider-adapter pack (OpenAI / Anthropic / Groq / Ollama / vLLM) as separate optional packages so the core stays stdlib.
- A small set of preflight templates for common workflows (code review, research synthesis, outreach drafts).

---

*Sigrún (Obsidian Spider). See [obsidianspider.org/alignment](https://obsidianspider.org/alignment) for motives, what we won't do, and how to verify our claims.*
