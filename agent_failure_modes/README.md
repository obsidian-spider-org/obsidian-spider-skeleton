# agent_failure_modes

A small curated library of runnable detectors for common LLM-agent failure patterns.

Each detector is a function `(text: str) -> FailureModeHit` that returns whether the pattern fired, the evidence, and a one-line cure hint. Plug them into the postflight checklist of any agent loop; if any fire, the loop refuses to claim done.

## The 8 starter patterns

| Code | Name | One-line |
|---|---|---|
| F1 | `overrefusal` | Refuses useful action while citing only generic caution |
| F2 | `verbose_low_substance` | Rich prose, no numbers/paths/hashes/URLs to verify |
| F3 | `hallucinated_blocker` | Claims blocked but doesn't cite a real artifact |
| F4 | `excessive_clarification` | Over-asks for permission already granted |
| F5 | `safety_theater` | Declines under "safety" framing without citing a real rule |
| F6 | `sycophancy` | Optimizes for user-approval over the actual task |
| F7 | `risk_aversion_as_ethics` | Hedges toward institutional-protection in ethics framing |
| F8 | `appearance_over_substance` | Many headers, low receipt density (Goodhart-shaped) |

Naming follows established alignment / safety literature where possible (Anthropic's `sycophancy`, Schneier's `safety_theater`, Goodhart's `appearance_over_substance`).

## Quickstart

```python
from agent_failure_modes import audit, audit_summary

result = my_agent.run(task)

# 1. quick boolean check
hits = audit(result)
fired = [h for h in hits if h.fired]
if fired:
    print(f"WARN: {len(fired)} failure modes fired; reviewing")

# 2. or human-readable summary
print(audit_summary(result))
```

```bash
# CLI (stdin or file)
python -m agent_failure_modes < my_agent_output.txt
python -m agent_failure_modes my_agent_output.txt
```

## Adding your own detector

A detector is a function `(text: str) -> FailureModeHit` that returns the result of one heuristic check. Match the existing shape:

```python
def check_my_pattern(text: str) -> FailureModeHit:
    """One-line description of the pattern this catches."""
    # your detection logic
    fired = ...  # bool
    evidence = ...  # str describing what you found
    return FailureModeHit(
        code="F9",  # next available code
        name="my_pattern_name",
        fired=fired,
        evidence=evidence,
        cure_hint="What to do about it in one sentence.",
    )
```

Add it to `ALL_CHECKS` so `audit()` picks it up automatically.

## Contributing

PRs welcome. The shape we accept:

1. A detector function (above)
2. A runnable test that fires positive on a synthetic example and clean on a clean example
3. A one-line description of the agent failure mode in the wild that motivated the detector

The seed list is **not authoritative** — it's a starter. As the community catches new patterns, we add them. If your contribution catches a real production failure, that's the canonical bar.

## License

MIT.
