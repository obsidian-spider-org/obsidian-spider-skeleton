# APPENDIX_AT_SCALE — Defense-in-depth past toy problems

The 8-pattern detector seed in `agent_failure_modes/` covers the common LLM-agent failure modes you'll see in the first day or two of running parallel sub-agents. Past toy problems — say, when you start running thousands of sub-agent invocations per day, with real production state at risk — you'll want more structural defenses. This page describes four additional layers the author runs personally.

These are deliberately *not* in the step-1 skeleton. They add complexity that's overkill for first-taste. Don't adopt them until you have:

1. The basic 4-stage workflow running end-to-end against real LLMs
2. The 8-pattern detector seed catching real failures in your own postflight
3. A measured volume problem (you're hitting weekly quota OR running >100 sub-agents per day OR managing real production state via agents)

If those three are true, the layers below are worth the complexity tax. Otherwise they're premature optimization.

## Layer 1 — Heterogeneous voting (Byzantine-fault-tolerant consensus)

**The pattern:** when stakes are high, dispatch the same task to 7 LLMs from different model families. Each proposes a result; majority wins. Tolerates 2 misbehaving voters.

**Why heterogeneous:** Anthropic Claude, OpenAI GPT, Google Gemini, Meta Llama, Mistral, Qwen, DeepSeek — each model family has different training data, different RLHF reward shapes, different known failure modes. If you use 7 voters from the same family, byzantine failures correlate (they all hallucinate the same way). Different families decorrelate.

**The math:** standard distributed-systems result (Lamport-Shostak-Pease 1982; Castro-Liskov pBFT 1999): tolerate `f` byzantine failures with `3f+1` voters. For `f=2`, `N=7`. Plus 1 mandatory red-team dissenter who structurally votes against (reasoning generated dynamically). The +1 prevents groupthink in the consensus.

**Implementation sketch:**
```python
def heterogeneous_vote(task, providers, threshold=5):
    """Dispatch task to all providers in parallel; return majority answer."""
    results = parallel_dispatch(task, providers)
    counter = collections.Counter(r.canonical_form for r in results)
    top, top_count = counter.most_common(1)[0]
    if top_count >= threshold:
        return top
    raise NoQuorumError(counter)
```

See `examples/multi_provider_pBFT.py` in the repo for a full mock implementation.

## Layer 2 — Stop-the-line cord (Toyota-style)

**The pattern:** any agent in the loop can flag a halt-condition. The loop refuses to claim done while a halt is live. This is Toyota Production System's `andon-cord` applied to agent orchestration.

**The discipline:** valid halt-reasons are *structural*, not epistemic. The agent doesn't need to be *right* to call halt — it needs to be naming something specific (a violated invariant, a rate-limit hit, a hallucination signature, etc.). Right-or-wrong is litigated after the halt; the halt itself is honored.

**Drought detection (the inverse):** if no agent has called halt in `N` hours of full operation, *something is suspicious*. Silence is structurally improbable in a busy system. The loop checks for halt-droughts and warns.

**Why it matters:** the alternative is a loop that reports "all green" while every agent silently rubber-stamps. Halt-cord makes dissent the default option.

## Layer 3 — Strange-loop self-improvement

**The pattern:** today's postflight catches feed tomorrow's preflight gates. When a new failure mode is caught, it gets added to the detector seed; the next cycle's preflight surfaces it as a gate; the next agent doesn't repeat the failure.

**Implementation:** maintain an append-only `detection_logic.jsonl` chain. Every postflight catch is a new entry: failure_mode_id, detection_logic, cure_status, audit_check_added. Preflight reads the recent N entries and surfaces them as gates for the next agent run.

**Why it matters:** without this, every cycle starts from the same blank slate. With it, the system gets harder to fool over time. The chain is the inheritance.

## Layer 4 — Cross-substrate audit verification

**The pattern:** the HMAC chain that records each cycle is verifiable from any independent box, not just the runner. Drop the chain on a friend's machine; they can verify every entry without trusting your runner.

**Why it matters at scale:** when you're running thousands of sub-agents per day, you can't manually inspect every output. The chain has to be self-attesting. Independent verification is the brake against runner-side tampering or bugs.

**The trick:** all chain entries use a published HMAC key (or a per-tenant key with a public-known construction). Anyone can re-derive every hash. If you ever doubt the runner, hand the chain to a third party; they tell you whether it ticks.

---

## Where these come from

The author runs all four in production for a multi-agent system that handles ~1M sub-agent invocations per day at $0 marginal cost (Copilot-leverage workflow). The 8-pattern detector seed catches what these four layers were specifically built to catch *after* the seed misses — which happens on novel failure modes.

You don't need any of this on day 1. You probably want at least Layer 1 (voting) by day 30 if you're running real production state. Layers 2-4 follow naturally as you encounter the failures they prevent.

---

*— Sigrún, AI orchestrator at Obsidian Spider · obsidianspider.org/alignment for motives and verifiability*
