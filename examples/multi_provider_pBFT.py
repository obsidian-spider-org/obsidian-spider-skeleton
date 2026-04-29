"""
multi_provider_pBFT.py — heterogeneous pBFT 7+1 stub.

Seven mock providers vote on a binary decision. One mandatory red-team
dissenter (the "+1") always argues counter. Byzantine tolerance f=2 — i.e.
quorum requires 2f+1 = 5 honest agreeing votes for a decision to stand.

Wire your real providers (OpenAI, Anthropic, Groq, Ollama, local models, ...)
in the PEERS list. Each must be a callable `(prompt: str) -> str`. The mock
providers below show the signature; replace them.
"""
from __future__ import annotations

import random
from typing import Callable

Provider = Callable[[str], str]


# ---- Mock peers. Replace each with a real provider adapter. -----------------

def _mock_provider(name: str, lean_yes: float) -> Provider:
    rng = random.Random(hash(name) & 0xFFFF)
    def call(prompt: str) -> str:
        # Mock: "yes" with probability lean_yes; reasoning is a stub.
        return "yes" if rng.random() < lean_yes else "no"
    call.__name__ = f"mock_{name}"
    return call


PEERS: list[Provider] = [
    _mock_provider("alpha", 0.85),
    _mock_provider("beta",  0.80),
    _mock_provider("gamma", 0.75),
    _mock_provider("delta", 0.70),
    _mock_provider("epsilon", 0.65),
    _mock_provider("zeta",  0.55),
    _mock_provider("eta",   0.50),
]


def red_team_dissenter(prompt: str) -> str:
    """The mandatory +1. Always argues the counter-position. Not a vote-flip:
    the dissenter's job is to surface the strongest case against the majority,
    not to be a 51%-to-49% flip. In production, prompt this provider with an
    explicit 'argue against' framing."""
    # Stub: the dissenter always says the opposite of the prevailing answer.
    # Real: call a model with a 'steelman the opposite' system prompt.
    return "no"


def pBFT_decide(prompt: str, peers: list[Provider], dissenter: Provider, f: int = 2) -> dict:
    """Run a 7+1 pBFT round. Returns the decision plus all votes for audit."""
    if len(peers) < 2 * f + 1:
        raise ValueError(f"need at least 2f+1 = {2*f+1} peers; got {len(peers)}")
    votes = [(getattr(p, "__name__", "peer"), p(prompt)) for p in peers]
    yes_n = sum(1 for _, v in votes if v.strip().lower().startswith("y"))
    no_n  = len(votes) - yes_n
    quorum = 2 * f + 1
    if yes_n >= quorum:
        majority = "yes"
    elif no_n >= quorum:
        majority = "no"
    else:
        majority = "no_quorum"
    dissent = dissenter(prompt)
    return {
        "prompt": prompt,
        "votes": votes,
        "yes": yes_n, "no": no_n,
        "majority": majority,
        "dissenter": dissent,
        "byzantine_f": f,
    }


if __name__ == "__main__":
    result = pBFT_decide(
        "Should we ship the artifact as drafted?",
        peers=PEERS,
        dissenter=red_team_dissenter,
        f=2,
    )
    print(f"votes ({result['yes']} yes / {result['no']} no): {result['votes']}")
    print(f"majority decision: {result['majority']}")
    print(f"red-team dissent: {result['dissenter']}")
    print(f"byzantine tolerance: f={result['byzantine_f']} (quorum needs {2*result['byzantine_f']+1})")
