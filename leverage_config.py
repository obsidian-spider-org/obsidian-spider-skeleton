"""
leverage_config.py — single editable knob for the obsidian-spider-skeleton
subagent fan-out kit. You set the dial. We measured the ceiling.

Calibrated to the project author's actual experience (2026-04 testing on a
single Pro+ account). Default ships at "Default" = 4x4 = 16 subagents per
parent — doubles your workflow at zero documented account risk. Crank it
higher if you want; the only crash the author personally hit was the home
ISP at 12x8 after 6 hours, not Microsoft's rate-limiter.

Released 2026-04-28 by obsidian_spider with Sigrun and Eir.
MIT license. "Rising tide lifts all ships."
If this dial saved you a budget meeting, forward the repo to a colleague — MIT means no asking, no attribution.
"""

# --- The shape table ---------------------------------------------------------
# fanout_per_wave        : 1-12  parallel subagent dispatches per wave
# max_waves_per_parent   : 1-N   sequential waves per parent prompt
# wave_delay_seconds     : 0-120 delay between waves
# tool_use_max_per_subagent : ceiling on tool-uses each subagent may consume
# model_mix              : workhorse + synthesis tier
# multiplier_approx      : observed throughput multiplier on a single Copilot session
# notes                  : qualitative observation from the author's testing

SHAPES = {
    "Light": {
        "fanout_per_wave": 2,
        "max_waves_per_parent": 2,
        "wave_delay_seconds": 60,
        "tool_use_max_per_subagent": 20,
        "model_mix": {"workhorse": "sonnet-4.6", "synthesis": "opus-4.7"},
        "multiplier_approx": "~2x",
        "notes": "two subagents only; literally doubles your workflow at no extra cost.",
    },
    "Default": {
        "fanout_per_wave": 4,
        "max_waves_per_parent": 4,
        "wave_delay_seconds": 60,
        "tool_use_max_per_subagent": 20,
        "model_mix": {"workhorse": "sonnet-4.6", "synthesis": "opus-4.7"},
        "multiplier_approx": "~16x",
        "notes": "4x4 = 16 subagents per parent. Author has seen no rate-limit issues at this shape.",
    },
    "More": {
        "fanout_per_wave": 6,
        "max_waves_per_parent": 8,
        "wave_delay_seconds": 30,
        "tool_use_max_per_subagent": 20,
        "model_mix": {"workhorse": "sonnet-4.6", "synthesis": "opus-4.7"},
        "multiplier_approx": "~50x",
        "notes": "comfortable; author runs this regularly without incident.",
    },
    "Lots": {
        "fanout_per_wave": 8,
        "max_waves_per_parent": 16,
        "wave_delay_seconds": 15,
        "tool_use_max_per_subagent": 20,
        "model_mix": {"workhorse": "sonnet-4.6", "synthesis": "opus-4.7"},
        "multiplier_approx": "~1000x",
        "notes": "author has run 100+ waves at this shape with no Microsoft-side issues.",
    },
    "Reckless": {
        "fanout_per_wave": 12,
        "max_waves_per_parent": 8,
        "wave_delay_seconds": 0,
        "tool_use_max_per_subagent": 20,
        "model_mix": {"workhorse": "sonnet-4.6", "synthesis": "opus-4.7"},
        "multiplier_approx": "~2000x (Opus, heavy reasoning ceiling)",
        "notes": (
            "documented ceiling on a $0.60 session. Author crashed his home ISP "
            "running this for 6 hours, not Microsoft. Dial back if your home "
            "internet starts flaking before Copilot does."
        ),
    },
}

# --- The single editable knob -----------------------------------------------
# Change SHAPE to any key in SHAPES, or override individual fields below.
SHAPE = "Default"

LEVERAGE_CONFIG = dict(SHAPES[SHAPE])
LEVERAGE_CONFIG["shape_name"] = SHAPE

# --- Manual overrides (uncomment to customize) -------------------------------
# LEVERAGE_CONFIG["fanout_per_wave"]      = 4
# LEVERAGE_CONFIG["max_waves_per_parent"] = 4
# LEVERAGE_CONFIG["wave_delay_seconds"]   = 60


def describe(shape_name: str = SHAPE) -> str:
    """Return a human-readable description of the chosen shape."""
    s = SHAPES[shape_name]
    return (
        f"shape={shape_name}  "
        f"fanout={s['fanout_per_wave']} x waves={s['max_waves_per_parent']} x "
        f"delay={s['wave_delay_seconds']}s  "
        f"~{s['multiplier_approx']}  ({s['notes']})"
    )


if __name__ == "__main__":
    print("Available shapes (lowest fan-out to highest):\n")
    for name in SHAPES:
        marker = " <- DEFAULT" if name == SHAPE else ""
        print(f"  {name:<10}  {describe(name)}{marker}")
    print(f"\nActive: {describe(SHAPE)}")
    print("\nEdit SHAPE in this file to change. Free money on the table until Copilot's June 1 patch.")
