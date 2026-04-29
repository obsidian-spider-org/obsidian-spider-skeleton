# Configuration

The fan-out shape (parallel-subagent dial) lives in `public_release/leverage_config.py` (one directory up from this skeleton). Read that file directly; it is the authoritative single editable knob.

## Shape table (calibrated to operator-empirical 2026-04 testing)

| Shape | fanout × waves | delay | observed multiplier | note |
|---|---|---|---|---|
| Light | 2 × 2 | 60s | ~2× | doubles workflow at no extra cost |
| **Default** | **4 × 4** | **60s** | **~16×** | author has seen no rate-limit issues at this shape |
| More | 6 × 8 | 30s | ~50× | comfortable; runs regularly without incident |
| Lots | 8 × 16 | 15s | ~1000× | 100+ waves at this shape with no upstream issues |
| Reckless | 12 × 8 | 0s | ~2000× (Opus, heavy reasoning) | documented ceiling on a single session |

Default ships at 4×4. The only crash the author personally hit at the higher shapes was a home-ISP wobble after 6 hours at Reckless — not a provider rate-limit. Calibrate to your own infrastructure.

## How to change

Edit one line in `leverage_config.py`:

```python
SHAPE = "Default"   # change to "Light" / "More" / "Lots" / "Reckless"
```

Or override individual fields below the `LEVERAGE_CONFIG = ...` line. Run the file directly to see all shapes:

```bash
python3 public_release/leverage_config.py
```

## Provider keys (env vars)

The skeleton itself uses mock providers and needs no keys. When you wire real providers, set keys via environment variables — never hard-code:

```bash
export OPENAI_API_KEY=sk-...
export ANTHROPIC_API_KEY=sk-ant-...
export GROQ_API_KEY=gsk_...
```

The chain ledger key for `chain.jsonl` HMAC defaults to a published constant; override it for any non-throwaway run:

```bash
export PDCA_CHAIN_KEY="your-secret-here"
export PDCA_CHAIN_PATH="/path/to/chain.jsonl"
```
