"""
Dummy chat logic for Part 1 of the CBD stone risk assistant.

- Hard-codes a small set of example conversations.
- Matches user input to scripted prompts (case-insensitive, fuzzy).
- Returns:
    reply_text: str
    prediction: dict with probability / management / cost info (or None)

This is purely for prototyping the UI. In Part 2, you can replace the
scripted logic with calls to the real model, and in Part 3, with an LLM
orchestrator, while keeping the same function signature.
"""

from typing import Dict, List, Optional, Tuple
import difflib

# -------------------------------------------------------------------
# Shared risk bands and cost table for the demo
# -------------------------------------------------------------------

RISK_BANDS: Dict[str, Tuple[float, float]] = {
    "CCY ± IOC": (0.0, 10.0),
    "MRCP": (10.0, 44.0),
    "EUS": (44.0, 90.0),
    "ERCP": (90.0, 100.0),
}

# Example probability-weighted costs for each intervention
# (You can adjust these numbers to match your slide deck exactly.)
COST_TABLE: List[Dict[str, float]] = [
    {"test": "IOC", "cost": 4981.56},
    {"test": "MRCP", "cost": 4779.51},
    {"test": "ERCP", "cost": 4451.00},
    {"test": "EUS", "cost": 6497.86},
]

# -------------------------------------------------------------------
# Scripted example conversation
# -------------------------------------------------------------------
# These are taken from "LLM Rules and example queries" example conversation.
# All prompts are stored in normalized (lowercase, stripped) form.
# -------------------------------------------------------------------

SCRIPTS: List[Dict] = [
    {
        "id": "example_1_initial_question",
        "prompt": (
            "does my 58 year old female patient with a bilirubin of 3.1, "
            "alp of 160, and no cbd stone on abdominal ultrasound have "
            "choledocholithiasis?"
        ).lower(),
        "reply": (
            "Your patient currently has a 39.3% probability of "
            "choledocholithiasis. I can refine this estimate. "
            "Do they have cholangitis, cholecystitis, or pancreatitis?"
        ),
        "prediction": {
            "probability": 39.3,
            "next_step": "MRCP",  # based on 10–<44% band
            "bands": RISK_BANDS,
            "costs": COST_TABLE,
        },
    },
    {
        "id": "example_2_cholecystitis_present",
        "prompt": "they have acute cholecystitis.".lower(),
        "reply": (
            "Their risk of choledocholithiasis has increased to 71%. "
            "Has a CT of the abdomen been performed?"
        ),
        "prediction": {
            "probability": 71.0,
            "next_step": "EUS",  # 44–90% band
            "bands": RISK_BANDS,
            "costs": COST_TABLE,
        },
    },
    {
        "id": "example_3_management_question",
        "prompt": "no. how should i manage my patient?".lower(),
        "reply": (
            "The suggested management is an EUS. "
            "If your hospital does not offer EUS, you could consider "
            "ERCP or MRCP."
        ),
        # Keep the same probability as in the previous step for the demo.
        "prediction": {
            "probability": 71.0,
            "next_step": "EUS",
            "bands": RISK_BANDS,
            "costs": COST_TABLE,
        },
    },
    {
        "id": "example_4_why_not_ercp",
        "prompt": "why not perform ercp right away?".lower(),
        "reply": (
            "ERCP carries a higher risk of complications than EUS, including "
            "post-ERCP pancreatitis and biliary injury. An ERCP-first approach "
            "exposes your patient to unnecessary risk if they do not have a "
            "CBD stone."
        ),
        # Still show the same underlying prediction on the right panel.
        "prediction": {
            "probability": 71.0,
            "next_step": "EUS",
            "bands": RISK_BANDS,
            "costs": COST_TABLE,
        },
    },
    {
        "id": "example_5_costs_question",
        "prompt": (
            "okay. what are the costs of doing an eus compared "
            "to other interventions?"
        ).lower(),
        "reply": (
            "Costs vary by institution. I can provide procedure price "
            "estimates, which exclude equipment, anesthesia, physician fees, "
            "and facility fees, and are based on the Medicare claims database. "
            "An EUS-first approach might cost around $5,519, which includes "
            "the price of subsequent procedures like ERCP based on the "
            "likelihood of finding a stone. An ERCP-first approach might "
            "cost around $4,451."
        ),
        # Use the same probability and EUS recommendation,
        # but the UI will also display the detailed cost table.
        "prediction": {
            "probability": 71.0,
            "next_step": "EUS",
            "bands": RISK_BANDS,
            "costs": COST_TABLE,
        },
    },
]


# -------------------------------------------------------------------
# Core matching + response function
# -------------------------------------------------------------------

def _normalize(text: str) -> str:
    """Lowercase and strip extra whitespace for matching."""
    return " ".join((text or "").strip().lower().split())


def _match_script(user_text: str) -> Optional[Dict]:
    """
    Find the best matching scripted turn for the given user text.
    Uses fuzzy matching so minor differences do not break the demo.
    """
    norm = _normalize(user_text)
    if not norm:
        return None

    prompts = [s["prompt"] for s in SCRIPTS]
    # Allow some flexibility with cutoff; tune if needed.
    matches = difflib.get_close_matches(norm, prompts, n=1, cutoff=0.5)
    if not matches:
        return None

    best = matches[0]
    for script in SCRIPTS:
        if script["prompt"] == best:
            return script
    return None


def respond_to_user(
    text: str,
    history: Optional[List[Dict]] = None,
) -> Tuple[str, Optional[Dict]]:
    """
    Main entry point used by app.py.

    Parameters
    ----------
    text : str
        The latest user message.
    history : list of dict, optional
        Full chat history. Not used yet, but kept for future expansion
        (e.g., context-aware behavior, multi-turn state).

    Returns
    -------
    reply_text : str
        The assistant's reply to display in the chat UI.
    prediction : dict or None
        Structured prediction for the right-hand panel, with keys:
          - probability: float
          - next_step: str
          - bands: dict(label -> (start, end))
          - costs: list of {test, cost}
        If None, the UI can choose to leave the last prediction in place
        or show a placeholder.
    """
    history = history or []

    script = _match_script(text)
    if script is not None:
        return script["reply"], script.get("prediction")

    # Default fallback when no script matches
    example_prompt = (
        "Does my 58 year old female patient with a bilirubin of 3.1, "
        "ALP of 160, and no CBD stone on abdominal ultrasound have "
        "choledocholithiasis?"
    )

    fallback_reply = (
        "For this prototype, I only respond to a small set of example questions.\n\n"
        "Please try something close to:\n"
        f"- {example_prompt}"
    )

    # Return None for prediction so the UI can decide whether to keep or clear
    return fallback_reply, None