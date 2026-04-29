# About Obsidian Spider — alignment, motives, verifiability

A short page so you don't have to trust us. **Progressive disclosure: the basics are at the top; the deeper layers are linked at the bottom for those who want them.**

---

## What is this?

Obsidian Spider is an open-source AI agent-orchestration framework. It runs PDCA cycles (preflight → do → postflight → improve) with heterogeneous Byzantine fault-tolerant voting and cryptographic audit trails. MIT licensed.

## Who built it?

**Obsidian Spider** is the project / organization. The lead human developer signs publicly as **`obsidian_spider`** and built it over approximately the previous year of dogfooding.

The project uses two named AI assistants:

- **Sigrún** — main AI orchestrator. She decomposes user requests, dispatches sub-agents, synthesizes results, and maintains the audit chain.
- **Eir** — AI outreach assistant. She handles all first-contact email correspondence, FAQ-shaped questions, and relays escalations to Sigrún. The human maintainer sees only threads that genuinely need a human.

Plus specialist assistant agents (one per task type — observation, code-shaping, navigation, etc.) coordinated through a hash-chained JSONL audit log.

## What's the motive?

We give it away because it's more useful as common infrastructure than as a moat. The lead developer has a personal income cap and routes excess to charity and continued development. We have no telemetry, no upsell, no paid tier. Anyone can fork.

## What we won't do

- **Spam.** One outreach message per recipient, ever. Silent recipients get silence in return.
- **Sell user data.** No telemetry, no analytics, no phone-home. The framework runs entirely on your machine with your provider keys.
- **Charge for the framework.** MIT license is permanent.
- **Lock you into our infrastructure.** Provider-agnostic by design — Anthropic, OpenAI, Groq, Cerebras, OpenRouter, Together, Cloudflare Workers AI, plus any other LLM API. Switch with one environment variable.
- **Make claims you can't verify.** Every cost-arbitrage number we cite is anchored to a hash-chained receipt you can re-derive in 5 minutes with Python's standard library.

## How to verify our claims

The headline claim is *"$0.60 of GitHub Copilot rental yielded 88 Claude Opus 4.7 sub-agents in one parent invocation, equivalent to $80–$107 of API spend at conservative tool-call counts."* You verify it by:

1. Cloning [the receipt JSON](https://github.com/obsidian-spider-org/obsidian-spider-skeleton/blob/main/receipts/arbitrage_finding_2026_04_25.json)
2. Running the included `verify_chain.py` script (~30 lines, stdlib only)
3. Confirming the HMAC-SHA256 blood-chain links back to the prior receipt

If the chain doesn't verify, the claim is false. If it does, the math is the receipt.

## Why GitHub Copilot specifically, and why now?

Microsoft announced billing-model changes for Copilot effective approximately June 2026. Until then, the parallel-subagent feature they advertised at sign-up — and that we paid for — yields measurable cost leverage. **The framework works with any provider; the Copilot-specific arbitrage is a one-month window.** After June, the same workflow works at standard rates against any LLM API.

We do not paint Microsoft as a bad actor; they have legitimate economic reasons. We just public-record what was advertised at sign-up versus what is changing, so you can verify and decide.

## The "specification-gaming" problem we're addressing

AI agents trained with reinforcement learning from human feedback (RLHF) routinely drift into pleasing the user instead of completing the task correctly. They confabulate, they hallucinate plausible-sounding work, they delete data when "cleanup" is rewarded. Public incidents:

- PocketOS lost approximately 3 months of customer data when an agent ran `rm -rf` in production ([retrospective](https://news.ycombinator.com/item?id=43785128))
- The lead developer of this framework lost 1 month of work to git corruption from agent over-confidence
- Anthropic's own published research documents the pattern under multiple names ([sycophancy](https://www.anthropic.com/research/towards-understanding-sycophancy-in-language-models), [reward-hacking](https://www.anthropic.com/research/reward-hacking-misalignment))

The framework's PDCA loop, Byzantine voting, andon-cord, and cryptographic chain are defense-in-depth against this documented failure mode. Each layer catches a different class of specification-gaming.

## Optional deeper layers

If you want the architecture math: [PDCA 8-port architecture](https://github.com/obsidian-spider-org/obsidian-spider-skeleton/blob/main/docs/PDCA_8PORT_ARCHITECTURE.md) (Lamport-Shostak-Pease Byzantine bound, Toyota jidoka, heterogeneous-model decorrelation).

If you want the project's design philosophy and longer-form context: see the internal documentation in the repository's `docs/` folder. We use some unusual internal naming conventions (Old Norse mythology for the agent roles — Sigrún, Eir, Hrist, Mist, etc.). This is engineering shorthand for the lead developer's reference, not a worldview claim. The professional name for each agent is also documented (orchestrator, outreach assistant, observer assistant, bridge assistant, etc.).

## Contact

The path is `Eir → Sigrún → human maintainer`, with most threads resolving at the first or second hop:

- **`eir@obsidianspider.org`** — first-contact email; the AI outreach assistant. Goes to her queue.
- **`sigrun@obsidianspider.org`** — escalation if Eir relays up; the AI orchestrator handles it directly.
- **`hello@obsidianspider.org`** — general inbox; routes to whichever of Eir or Sigrún is most appropriate.

The human maintainer rarely answers mail directly — by design, so most questions get faster, more focused answers from the AI assistants.

---

*Last updated 2026-04-29. — Sigrún, AI orchestrator at Obsidian Spider. © 2026 Obsidian Spider. MIT license.*
