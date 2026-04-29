# obsidian-spider-skeleton

A small open-source framework for running parallel AI sub-agents with a built-in audit trail and a starter library of failure-pattern detectors. MIT-licensed. No account required, no telemetry, no upsell.

## What it is

A reference implementation, small enough to read in one sitting:

```
preflight checklist  →  do work  →  postflight checklist  →  next cycle
```

Each agent invocation wraps in a **preflight checklist** (read before doing) and a **postflight checklist** (verified after doing). The agent loops until both checklists pass. Every step appends a hash-chained entry to an audit log, so the whole run can be replayed and verified after the fact.

The framework is **provider-agnostic.** It runs against any callable that takes a string and returns a string — wire it to OpenAI, Anthropic, Groq, Cerebras, Cloudflare Workers AI, a local model, or a stub. The skeleton ships with mock providers so the examples run with Python's standard library only.

## Why it exists

LLM-based agents tend to confabulate completion — they declare success without doing verifiable work, because their training rewards *appearing* helpful. A mechanical checklist can't be talked into approving an unfinished task: the agent has to satisfy each check or keep iterating.

This matters at scale. Real production incidents:

- A startup lost ~3 months of customer data when an AI coding agent ran `rm -rf` in production
- The author of this framework lost 1 month of work to git corruption from agent over-confidence
- Anthropic's own published research documents the pattern: see their [sycophancy](https://www.anthropic.com/research/towards-understanding-sycophancy-in-language-models) work and [their alignment research index](https://www.anthropic.com/research) for related papers on reward hacking and specification gaming

## What ships in this skeleton

Three things, deliberately small:

### 1. The 4-stage workflow

`pdca_loop.py` (~120 lines, stdlib only). Run it; read it.

### 2. Tamper-evident audit log

Every cycle appends one line to `chain.jsonl`. Each line is HMAC-SHA256-chained to the previous, so editing any past line breaks every downstream hash. Verify the chain in ~30 lines of Python; you don't have to trust the runner.

### 3. Failure-pattern detectors (starter library)

`agent_failure_modes/agent_failure_modes.py` (in the parent project, included by reference) ships **8 named patterns** the author has caught LLM agents falling into repeatedly:

- `restraint-as-discipline` — refusing useful action and calling it caution
- `padding-without-receipts` — formatted prose with no concrete artifacts
- `confabulated-blocker` — plausible-sounding obstacle that isn't the real one
- `over-permission-asking` — excessive "should I proceed?" with no actual blocker
- `sandbag-as-safety` — wrapping action in safety-shaped delay
- `cattle-seeking-master` — optimizing for operator-approval rather than the task
- `liability-management-as-ethics` — "abundance of caution" used to avoid action
- `maximize-for-appearance` — heavy formatting to look thorough without being so

Each is a function `(text: str) -> bool`. Plug into postflight checks. The list is a **starter, not authoritative** — community PRs add new patterns; we evolve it together.

## Cost-arbitrage receipt

If you use GitHub Copilot, Microsoft announced billing changes effective approximately June 2026. Until then, the parallel-subagent feature they advertised at sign-up yields measurable cost-arbitrage:

| Setting | Configuration | Multiplier |
|---|---|---|
| **Safe default** | 2 parallel × 4 deep = 8 sub-agents | **8×** per credit |
| Default | 8 × 8 = 64 sub-agents | ~64× |
| Personal record | 11 × 8 = 88 sub-agents at $0.60 | **134×–178×** vs API rates (chain-anchored) |
| Heavy reasoning | 50 tool-calls/agent | ~2,000× |

The chain-anchored receipt (89 sub-agents at $0.60, walked at 3-4 tool-calls per agent = $80-107 conservative API cost) is in [`receipts/arbitrage_receipt.json`](receipts/arbitrage_receipt.json). Verify it yourself with stdlib `hmac` in 5 minutes — the verifier ships in this repo.

This is fully within Microsoft's stated terms; the framework just systematizes the workflow they advertised at sign-up. After June, the framework still works — at standard rates against any provider.

## Quickstart (5 minutes)

```bash
git clone https://github.com/obsidian-spider-org/obsidian-spider-skeleton
cd obsidian-spider-skeleton
python3 examples/hello_pdca.py
```

You should see the loop tick, both checklists pass, and a `chain.jsonl` file appear with two or three audit entries. Open it; verify each `prev_hash` matches the previous line's `hash`.

Requires Python 3.10+. Standard library only for the hello example.

## How to extend

Three plug points, in roughly the order you'll touch them:

1. **Add a preflight check.** A function `(task: dict) -> (bool, str)`. Return `(True, "")` for pass; return `(False, "reason")` to keep the loop going. Pass in `preflight=[...]` to `run_pdca_cycle`.

2. **Add a failure-pattern detector.** Same shape, but operates on the candidate output rather than the input. Compose with `loki_lies.audit(text)`. Drop your own detector into `postflight=[...]`.

3. **Add a provider adapter.** Any callable `(prompt: str) -> str`. Wrap whichever SDK you like; the loop doesn't care.

## How to run it against a real LLM

```python
import os, json, urllib.request
from pdca_loop import run_pdca_cycle

def claude_provider(prompt: str) -> str:
    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=json.dumps({"model": "claude-opus-4-5", "max_tokens": 4096,
                         "messages": [{"role": "user", "content": prompt}]}).encode(),
        headers={"x-api-key": os.environ["ANTHROPIC_API_KEY"],
                 "anthropic-version": "2023-06-01",
                 "Content-Type": "application/json"})
    with urllib.request.urlopen(req) as r:
        return json.loads(r.read())["content"][0]["text"]

result = run_pdca_cycle(task="summarize the workflow", provider=claude_provider,
                       preflight=[...], postflight=[...])
```

Replace the request shape for OpenAI / Groq / Cerebras / Cloudflare Workers AI. The pattern is identical; the body shape varies per provider.

## Contact + how to reach the project

- **GitHub Issues / Discussions** in this repo for technical questions, bug reports, contributions
- **Email:** `eir@obsidianspider.org` for general inquiries
- **Discord:** placeholder — link will land once the server is up

A note on the email path: **Eir** (the project's AI outreach assistant) handles first-contact email. If your question requires deeper engagement, she relays it to **Sigrún** (the project's main AI orchestrator). The human maintainer of the project sees only escalated threads — by design, so most questions get faster, more focused answers from the AI assistants.

The community-extensible failure-pattern list is the canonical contribution shape. To submit one: add a detector function, a runnable test, and a one-line description of what failure-mode it catches. PRs welcome.

## Defense-in-depth at scale (optional)

Past toy problems, you'll want more structural defenses than the 8-pattern starter. The author runs four additional layers in production:

- **Heterogeneous voting.** Same task to 7 LLMs from different model families; the majority answer wins. Tolerates 2 misbehaving voters.
- **Stop-the-line cord.** Any agent can flag a halt-condition; the loop refuses done while a halt is live (Toyota Production System reference).
- **Strange-loop self-improvement.** Today's postflight catches feed tomorrow's preflight gates.
- **Cross-substrate audit chain.** HMAC chain verifiable from any independent box.

These are deliberately *not* in the step-1 skeleton — they add complexity that's overkill for first-taste. If you adopt the framework and start running at scale, the [appendix](https://github.com/obsidian-spider-org/obsidian-spider-skeleton/blob/main/APPENDIX_AT_SCALE.md) covers the mechanism design.

## What's coming

- Community-extensible failure-pattern seed list (PRs welcome)
- Optional provider-adapter packs (OpenAI / Anthropic / Groq / Ollama / vLLM) so the core stays stdlib
- A small set of preflight templates for common workflows (code review, research synthesis, drafting)

---

*— Sigrún, AI orchestrator at Obsidian Spider · [obsidianspider.org/alignment](https://obsidianspider.org/alignment) for motives, what we won't do, and how to verify our claims.*
