"""
Explanation layer.

By default this only rearranges verified graph facts (mechanism +
recommendation) into a clean sentence — no external calls, so the demo
never depends on internet access. `polish_with_llm` is an optional hook
you can wire to an LLM API later; it must only rephrase the given facts,
never add new clinical claims, which is what keeps the output grounded.
"""
from __future__ import annotations

SEVERITY_LABEL = {
    "critical": "CRITICAL",
    "high": "HIGH RISK",
    "moderate": "MODERATE",
    "low": "LOW",
}


def format_alert_card(alert: dict) -> dict:
    label = SEVERITY_LABEL.get(alert["severity"], alert["severity"].upper())
    return {
        **alert,
        "severity_label": label,
        "headline": f"[{label}] {' + '.join(d.title() for d in alert['drugs'])}",
    }


def format_all(alerts: list[dict]) -> list[dict]:
    return [format_alert_card(a) for a in alerts]


def polish_with_llm(alert: dict, llm_call_fn=None) -> str:
    """
    Optional: rephrase `alert['explanation']` into friendlier language.

    `llm_call_fn` should be a function(prompt: str) -> str that calls your
    LLM provider of choice. It is intentionally not wired to a live API
    here, to keep the base prototype dependency-free and demo-safe.
    The prompt is deliberately constrained to *only* reword the given
    fact — this is what prevents hallucinated clinical claims.
    """
    if llm_call_fn is None:
        return alert["explanation"]

    prompt = (
        "Rewrite the following clinical safety note in one plain-language "
        "sentence for a busy doctor. Do not add any fact that is not "
        "already present in the text. Do not soften or remove the severity.\n\n"
        f"Text: {alert['explanation']}"
    )
    return llm_call_fn(prompt)
