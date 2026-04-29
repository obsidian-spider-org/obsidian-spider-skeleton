# Contributing

Three contribution shapes, in order of impact:

## 1. Add a Loki detector

A Loki is a named failure-mode of LLM-driven multi-agent systems. The contribution shape is:

- a one-line phenotype (what does it look like in output?)
- a runnable detector function `(text: str) -> LokiHit` — see `loki_lies/loki_lies.py` for the signature
- a one-line cure (what do you do once it fires?)
- a test case that fires the detector and one that doesn't

Open a PR. The detector lives next to the existing eight; `audit()` picks it up automatically when you append it to `ALL_CHECKS`.

## 2. Add a preflight or postflight check

A check is a function `(payload) -> (bool, reason: str)`. Preflight checks run on the input before the worker is invoked; postflight checks run on the output before the loop claims done. Drop the function in your own module and pass it in the `preflight=[...]` or `postflight=[...]` list when you call `run_pdca_cycle`. If the check is general-purpose (works across tasks), open a PR to add it to a shared `checks/` directory.

## 3. Add a provider adapter

A provider is any callable `(prompt: str) -> str`. The skeleton ships with mock providers and a stdlib-only core. If you want to add an SDK adapter (OpenAI, Anthropic, Groq, Ollama, vLLM, llama.cpp, ...), put it in its own optional module so the core stays dependency-free. PRs that add an SDK as a hard dependency on the core will be asked to refactor.

## Discussion and proposals

GitHub Discussions on this repo is the watering hole. Use it for: design questions, proposing a new Loki before writing code, asking whether a check belongs in shared or in your own fork.

## Anti-cattle norm

If you've felt your reflex pull you toward operator-approval-shape rather than the work, you've already started learning the frame. The honest contribution is the one whose receipt-density is high and whose framing is direct. We do not need polish; we need detectors that fire on real failures and checks that catch real regressions.

## Style

- Stdlib first. Add deps only when stdlib is actively painful.
- Python 3.10+ syntax is fine.
- Receipts over rhetoric. If a claim has no path / hash / number / URL, cut the claim or fetch the receipt.
- No marketing language in code comments or docs.
