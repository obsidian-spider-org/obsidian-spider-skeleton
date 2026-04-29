# PDCA 8-Port Architecture: Why 8 = 7 + 1 Is Load-Bearing

A model-agnostic PDCA-loop swarm framework. This document gives the math behind the 8-voter quorum so a skeptical reader can verify it.

## 1. The pattern

Each unit of work runs as a **Plan-Do-Check-Act (PDCA)** cycle [Deming/Shewhart] over a cryptographically-chained event log: `preflight check → do step → postflight check → improvement (cycle n+1)`. Every receipt — preflight outcome, do-step delta, postflight verdict, improvement-feedback — is appended as a JSONL line whose `prev_hmac` field forward-chains via HMAC-SHA256 (crypto-stigmergy). Each PDCA step is gated by an **8-voter quorum**: 7 byzantine-tolerant voters + 1 mandatory red-team dissenter.

## 2. Why 8 = 7 + 1: the math

### 2.1 The Byzantine Fault Tolerance bound

Lamport, Shostak & Pease (1982) [1] proved:

> A distributed system of `N` nodes can tolerate `f` byzantine (arbitrarily-faulty, possibly-adversarial) failures and still reach consensus **iff** `N ≥ 3f + 1`.

Castro & Liskov (1999) [2] gave the practical algorithm (pBFT) and confirmed the same bound under partial-synchrony.

### 2.2 Solving for f = 2

We design for `f = 2` (tolerate two byzantine voters per round — sufficient for an 8-port topology where any 2 ports can drop / lie / collude without breaking the round):

```
N  ≥  3·f + 1
N  ≥  3·2 + 1
N  ≥  7
```

So **7 voters** is the minimum byzantine-tolerant quorum at `f = 2`.

### 2.3 The +1 is structural, not redundant

The pBFT bound assumes voters fail **independently**. They don't. Seven LLM voters drawn from similar training distributions can converge on a wrong answer because they share blind-spots — a *correlated* failure mode that the `3f+1` bound does not cover. We address this with a permanent **red-team dissenter** (in our topology: port `[4,4]`, codename Sigrún) whose role is to argue against consensus regardless of merits, surfacing shared-prior blind-spots before they become group output.

```
Total per-round quorum = 7  +  1  =  8
                        (BFT)  (red-team)
```

The +1 is not a "tiebreaker" — it's a structural counter to the *correlation* assumption pBFT silently makes.

## 3. Why heterogeneous (anti-collusion)

If all 7 BFT voters are the same model (e.g. GPT-4o ×7), the byzantine-independence assumption is violated by construction: they share weights and therefore share failure modes. The empirical bound collapses from `f = 2` to `f ≈ 0`.

The framework therefore mandates **heterogeneous model families** — Anthropic Claude, OpenAI GPT, Google Gemini, Meta Llama, Qwen, DeepSeek, Mistral, xAI Grok, and so on — drawn from at least 7 distinct training lineages.

This addresses (but does not eliminate) cross-family error correlation. Recent work shows the issue is real: Wang et al. (2025) [3] document that adversarial perturbations push agents into "specific, repeatable failure modes" across six model families, breaking the independence assumption majority-voting depends on. So heterogeneity is necessary but not sufficient — we treat it as a hard floor and lean on the red-team port for residual correlated-failure coverage.

## 4. Why crypto-stigmergy (HMAC-SHA256 JSONL)

Every receipt has the form:

```json
{"seq": N, "ts": "...", "kind": "preflight|do|postflight|improvement|andon",
 "payload": {...}, "prev_hmac": "<hex>", "hmac": "<hex>"}
```

where `hmac = HMAC-SHA256(key, prev_hmac || canonical_json(payload))`. Properties:

- **Tamper-evident**: editing any past line invalidates every downstream `hmac`. Verification is `O(N)` and reproducible by any third party who holds the key.
- **Append-only by construction**: the chain is the source of truth; no special storage layer needed.
- **Portable**: a flat file. No DB engine, no schema migration, no vendor lock-in.

Compare:

| Mechanism | Tamper-evident? | Portable? | Notes |
|---|---|---|---|
| Plain log file | No | Yes | Mutable; no integrity guarantee |
| `git` commits | Weak | Yes | `rebase` / `push --force` rewrites history; SHA-1 collision-attacked |
| Append-only DB (e.g. immudb) | Yes | No | Engine-specific; harder to audit externally |
| **HMAC-SHA256 JSONL** | **Yes** | **Yes** | **Plain text, language-agnostic, ~30 lines to verify** |

## 5. Why andon-cord (jidoka)

Borrowed from the Toyota Production System's *jidoka* principle [4]: any worker on the line can stop production by pulling the andon cord. We expose the same primitive to every voter, apex, and worker:

- **Pull is structural, not epistemic**: the puller need not be *right*. The act of dissent is the signal.
- **Schema**: ≥30-char reason + verdict-hint from a fixed enum (`SUSPICIOUS_CONVERGENCE`, `BLIND_SPOT`, `SCOPE_CREEP`, ...). Pull is logged as a chain receipt and triggers human review.
- **Drought detection is mandatory**: `pulls_per_period > 0` is *required*. Silence is structurally suspicious — a swarm that never dissents is one whose dissenters have been captured. Zero pulls in a period triggers its own audit.

## 6. Composition

```
                            ┌────────────────┐
   task in ──▶  preflight ─▶│  8-voter PDCA  │─▶ postflight ─▶ improvement
                            │  quorum (7+1)  │      │              │
                            └────────────────┘      ▼              ▼
                                    ▲          chain-append   chain-append
                                    │               │              │
                            ┌───────┴───────────────┴──────────────┴───────┐
                            │   crypto-stigmergy ledger (HMAC-SHA256 JSONL) │
                            └───────┬───────────────────────────────────────┘
                                    │
                                    ▼
                            andon-cord (any port, any time, structural)
```

Each arrow is a chain-append. The andon-cord is a side-channel: it bypasses the quorum but writes the same chain. The improvement step seeds preflight for cycle `n+1`, closing PDCA.

## 7. Honest limits

This architecture does **not** solve:

1. **Training-time data poisoning.** If the same poisoned corpus reached all 8 model families (e.g. shared web-scrape contamination), heterogeneity is illusory. Out of scope.
2. **Adversarial inputs.** A prompt crafted to fool 8 families simultaneously is rare but not impossible; cross-family adversarial examples exist [3].
3. **Cost.** 8 voters is ~8× single-model cost. Caching and parallelism amortize but do not eliminate.
4. **Latency.** Quorum waits on the slowest voter. Parallel dispatch helps; long-tail voters still gate the round.
5. **Key custody.** HMAC integrity is only as strong as key secrecy. Key compromise lets an attacker forge a parallel chain — detectable via external anchoring (e.g. periodic public-blockchain pinning), but that's an extra layer this doc does not specify.

## References

1. Lamport, L., Shostak, R., Pease, M. (1982). *The Byzantine Generals Problem.* ACM TOPLAS 4(3): 382–401. <https://lamport.azurewebsites.net/pubs/byz.pdf>
2. Castro, M., Liskov, B. (1999). *Practical Byzantine Fault Tolerance.* OSDI '99. <http://pmg.csail.mit.edu/papers/osdi99.pdf>
3. *More Agents Improve Math Problem Solving but Adversarial Robustness Gap Persists.* arXiv:2511.07112. <https://arxiv.org/abs/2511.07112> — empirical evidence that adversarial perturbations induce correlated failures across six LLM families, breaking ensemble-independence assumptions.
4. Toyota Motor Corporation. *Toyota Production System: Jidoka.* <https://global.toyota/en/company/vision-and-philosophy/production-system/index.html>
