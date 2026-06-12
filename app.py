"""
Weak Signals - Process Safety Drill
A single-file Streamlit application.

Run with:
    pip install streamlit
    streamlit run app.py
"""

import streamlit as st

# --------------------------------------------------------------------------- #
# Static game data
# --------------------------------------------------------------------------- #

APP_TITLE = "Weak Signals — Pump House Process Safety Drill"

RISK_OPTIONS = ["Low", "Medium", "High", "Critical"]

# API RP 754 Tier / Workplace classification choices
TIER_OPTIONS = [
    "Tier 1 — LOPC w/ greater consequence",
    "Tier 2 — LOPC w/ lesser consequence",
    "Tier 3 — Challenge to safety system",
    "Tier 4 — Operating discipline / workplace",
]

# The 5 Pump House hazards.
HAZARDS = [
    {
        "id": 1,
        "title": "Seal Weep on P-101A",
        "signal": (
            "Operators report a light, intermittent weep at the mechanical "
            "seal of centrifugal pump P-101A (light hydrocarbon service). "
            "No pooling, but a faint odor is present in the bay."
        ),
        "correct_risk": "Medium",
        "correct_tier": "Tier 3 — Challenge to safety system",
        "feedback": (
            "A weeping seal is a classic **weak signal**. There is no measurable "
            "loss-of-primary-containment (LOPC) threshold breach yet, so it is a "
            "**Tier 3 challenge to a safety system** (the seal). Risk is **Medium**: "
            "credible escalation path to a Tier 1/2 release if the seal degrades."
        ),
    },
    {
        "id": 2,
        "title": "Bypassed Low-Flow Trip",
        "signal": (
            "During the shift handover you discover the low-flow protective trip "
            "on P-102 has been jumpered out for 'troubleshooting' three shifts ago "
            "with no MOC or work order on record."
        ),
        "correct_risk": "High",
        "correct_tier": "Tier 4 — Operating discipline / workplace",
        "feedback": (
            "A defeated safeguard with no Management of Change is an **operating "
            "discipline failure** — **Tier 4**. Risk is **High**: the protective "
            "layer is gone *and* the breakdown in MOC suggests systemic discipline "
            "issues. Restore the trip and open an incident."
        ),
    },
    {
        "id": 3,
        "title": "Flange Spray to Atmosphere",
        "signal": (
            "A pinhole spray of process fluid is observed from a flange on the "
            "P-103 discharge line. Estimated release exceeds the threshold "
            "quantity but is contained within the bunded area with no fire or injury."
        ),
        "correct_risk": "High",
        "correct_tier": "Tier 2 — LOPC w/ lesser consequence",
        "feedback": (
            "This is an actual **loss of primary containment above the threshold "
            "quantity** but without greater consequence (no fire, injury, or large "
            "release) — that is a **Tier 2** event. Risk **High**: active release "
            "to atmosphere demands immediate isolation."
        ),
    },
    {
        "id": 4,
        "title": "Vibration Trend Drift",
        "signal": (
            "The condition-monitoring dashboard shows P-104 bearing vibration has "
            "drifted upward ~15% over two weeks, still under the alarm setpoint. "
            "No alarm, no leak — just a trend."
        ),
        "correct_risk": "Low",
        "correct_tier": "Tier 4 — Operating discipline / workplace",
        "feedback": (
            "A sub-alarm rising trend is the weakest of weak signals — predictive, "
            "not yet a containment or safeguard event. Classify as **Tier 4** "
            "(operating discipline / proactive indicator). Risk **Low** *today*, "
            "but trend it and schedule maintenance before it becomes Tier 1/2."
        ),
    },
    {
        "id": 5,
        "title": "Vapor Cloud + Ignition Source",
        "signal": (
            "A significant LOPC from P-105 forms a visible vapor cloud in the "
            "pump house. A non-rated portable light is energized within the cloud "
            "boundary. No ignition has occurred yet."
        ),
        "correct_risk": "Critical",
        "correct_tier": "Tier 1 — LOPC w/ greater consequence",
        "feedback": (
            "A large release with potential for greater consequence (fire/explosion "
            "given the live ignition source) is **Tier 1**. Risk **Critical**: this "
            "is a near-miss to a major accident event. Evacuate, isolate, and "
            "eliminate the ignition source immediately."
        ),
    },
]

POINTS_PER_CORRECT = 1  # one point for risk, one for tier


# --------------------------------------------------------------------------- #
# State management
# --------------------------------------------------------------------------- #

def init_state() -> None:
    """Initialise all session_state keys exactly once."""
    defaults = {
        "phase": "briefing",          # briefing | playing | scorecard
        "current": 0,                 # index into HAZARDS
        "score": 0,                   # cumulative points
        "max_score": len(HAZARDS) * 2,
        "submitted": False,           # has the current hazard been graded?
        "results": [],                # per-hazard result dicts
    }
    for key, value in defaults.items():
        st.session_state.setdefault(key, value)


def reset_game() -> None:
    """Reset to a fresh briefing screen."""
    st.session_state.phase = "briefing"
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.submitted = False
    st.session_state.results = []


def start_game() -> None:
    st.session_state.phase = "playing"
    st.session_state.current = 0
    st.session_state.score = 0
    st.session_state.submitted = False
    st.session_state.results = []


# --------------------------------------------------------------------------- #
# Sidebar — persistent score tracker
# --------------------------------------------------------------------------- #

def render_sidebar() -> None:
    with st.sidebar:
        st.header("📊 Drill Tracker")
        phase = st.session_state.phase

        if phase == "briefing":
            st.info("Awaiting briefing acknowledgement.")
        else:
            answered = len(st.session_state.results)
            total = len(HAZARDS)
            st.metric("Score", f"{st.session_state.score} / {st.session_state.max_score}")
            st.progress(answered / total if total else 0.0,
                        text=f"Hazard {min(answered + (0 if phase=='scorecard' else 1), total)} of {total}")

        st.divider()
        if st.button("🔄 Restart Drill", use_container_width=True):
            reset_game()
            st.rerun()

        st.caption(
            "Classifications follow **API RP 754** process safety "
            "performance indicators (Tier 1–4)."
        )


# --------------------------------------------------------------------------- #
# Screens
# --------------------------------------------------------------------------- #

def render_briefing() -> None:
    st.title(APP_TITLE)
    with st.container(border=True):
        st.subheader("Mission Briefing")
        st.markdown(
            """
            Welcome to the **Pump House Process Safety Drill**.

            Your job is to interpret **weak signals** — early, often ambiguous
            indicators that precede major process safety events. For each of the
            **5 hazards** you will:

            1. Assign a **Risk Priority** — *Low, Medium, High, or Critical*.
            2. Classify the event under **API RP 754** — *Tier 1 through Tier 4*.

            You earn **1 point** for the correct risk priority and **1 point** for
            the correct tier. Read each signal carefully — not every leak is a
            Tier 1, and not every quiet trend is harmless.
            """
        )
        st.warning("Stay sharp. The weakest signals often precede the worst outcomes.")
        if st.button("▶️ Begin Drill", type="primary", use_container_width=True):
            start_game()
            st.rerun()


def render_hazard() -> None:
    idx = st.session_state.current
    hazard = HAZARDS[idx]

    st.title(APP_TITLE)
    st.caption(f"Hazard {idx + 1} of {len(HAZARDS)}")

    # --- Scenario container ------------------------------------------------ #
    with st.container(border=True):
        st.subheader(f"⚠️ {hazard['title']}")
        st.markdown(f"**Field Signal:**\n\n> {hazard['signal']}")

    # --- Answer form ------------------------------------------------------- #
    if not st.session_state.submitted:
        with st.form(key=f"form_{hazard['id']}", border=True):
            st.markdown("#### Your Assessment")
            col1, col2 = st.columns(2)
            with col1:
                risk_choice = st.radio(
                    "Risk Priority", RISK_OPTIONS, index=None, key=f"risk_{hazard['id']}"
                )
            with col2:
                tier_choice = st.radio(
                    "API RP 754 Classification", TIER_OPTIONS, index=None,
                    key=f"tier_{hazard['id']}"
                )
            submitted = st.form_submit_button(
                "✅ Submit Assessment", type="primary", use_container_width=True
            )

        if submitted:
            if risk_choice is None or tier_choice is None:
                st.error("Select **both** a Risk Priority and an API RP 754 Tier before submitting.")
            else:
                grade_hazard(hazard, risk_choice, tier_choice)
                st.rerun()
    else:
        render_feedback(hazard)


def grade_hazard(hazard: dict, risk_choice: str, tier_choice: str) -> None:
    risk_ok = risk_choice == hazard["correct_risk"]
    tier_ok = tier_choice == hazard["correct_tier"]
    gained = (POINTS_PER_CORRECT if risk_ok else 0) + (POINTS_PER_CORRECT if tier_ok else 0)

    st.session_state.score += gained
    st.session_state.submitted = True
    st.session_state.results.append(
        {
            "title": hazard["title"],
            "risk_choice": risk_choice,
            "tier_choice": tier_choice,
            "correct_risk": hazard["correct_risk"],
            "correct_tier": hazard["correct_tier"],
            "risk_ok": risk_ok,
            "tier_ok": tier_ok,
            "gained": gained,
        }
    )


def render_feedback(hazard: dict) -> None:
    result = st.session_state.results[-1]

    with st.container(border=True):
        st.markdown("#### 🧪 Technical Feedback")

        col1, col2 = st.columns(2)
        with col1:
            if result["risk_ok"]:
                st.success(f"Risk Priority ✔ **{result['risk_choice']}**")
            else:
                st.error(
                    f"Risk Priority �’✗ You chose **{result['risk_choice']}** — "
                    f"correct: **{result['correct_risk']}**"
                )
        with col2:
            if result["tier_ok"]:
                st.success(f"API RP 754 ✔ **{result['tier_choice']}**")
            else:
                st.error(
                    f"API RP 754 ✗ You chose **{result['tier_choice']}** — "
                    f"correct: **{result['correct_tier']}**"
                )

        st.info(hazard["feedback"])
        st.markdown(f"**Points earned this hazard: {result['gained']} / 2**")

    is_last = st.session_state.current >= len(HAZARDS) - 1
    label = "🏁 View Scorecard" if is_last else "➡️ Next Hazard"
    if st.button(label, type="primary", use_container_width=True):
        advance()
        st.rerun()


def advance() -> None:
    if st.session_state.current >= len(HAZARDS) - 1:
        st.session_state.phase = "scorecard"
    else:
        st.session_state.current += 1
        st.session_state.submitted = False


def render_scorecard() -> None:
    st.title("🏁 Drill Scorecard")
    score = st.session_state.score
    max_score = st.session_state.max_score
    pct = (score / max_score * 100) if max_score else 0

    with st.container(border=True):
        st.metric("Final Score", f"{score} / {max_score}", f"{pct:.0f}%")
        if pct == 100:
            st.success("Flawless. You read every weak signal correctly. 🥇")
        elif pct >= 70:
            st.info("Solid situational awareness — review the misses below.")
        else:
            st.warning("Several weak signals were missed. Recalibrate and re-run the drill.")

    st.markdown("#### Hazard-by-Hazard Review")
    for i, r in enumerate(st.session_state.results, start=1):
        with st.container(border=True):
            st.markdown(f"**{i}. {r['title']}** — {r['gained']} / 2 pts")
            c1, c2 = st.columns(2)
            with c1:
                icon = "✔" if r["risk_ok"] else "✗"
                st.markdown(
                    f"{icon} **Risk:** {r['risk_choice']} "
                    f"(correct: {r['correct_risk']})"
                )
            with c2:
                icon = "✔" if r["tier_ok"] else "✗"
                st.markdown(
                    f"{icon} **Tier:** {r['tier_choice']} "
                    f"(correct: {r['correct_tier']})"
                )

    if st.button("🔄 Run Drill Again", type="primary", use_container_width=True):
        reset_game()
        st.rerun()


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> None:
    st.set_page_config(page_title="Weak Signals Drill", page_icon="⚠️", layout="centered")
    init_state()
    render_sidebar()

    phase = st.session_state.phase
    if phase == "briefing":
        render_briefing()
    elif phase == "playing":
        render_hazard()
    elif phase == "scorecard":
        render_scorecard()


if __name__ == "__main__":
    main()
