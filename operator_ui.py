from __future__ import annotations

import json
import os
from pathlib import Path

import streamlit as st

from groundpatrol.agent import build_agent


SCENARIOS = {
    "Clear operating envelope": "clear",
    "Person enters operating envelope": "people_nearby",
    "Protected habitat": "protected_habitat",
    "Access closed": "access_closed",
    "High wind": "high_wind",
    "Low visibility": "low_visibility",
    "Stale evidence": "stale",
}


def _latest_json(directory: str) -> dict | None:
    root = Path(directory)
    if not root.exists():
        return None
    files = sorted(root.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not files:
        return None
    try:
        return json.loads(files[0].read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None


def _work_order_for_receipt(receipt_id: str | None) -> dict | None:
    if not receipt_id:
        return None
    root = Path("executions")
    if not root.exists():
        return None
    for path in root.glob("*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if payload.get("receipt_id") == receipt_id:
            return payload
    return None


def _render_result(message) -> None:
    if isinstance(message, dict):
        content = message.get("content")
        if isinstance(content, list):
            text_parts = [
                item.get("text", "")
                for item in content
                if isinstance(item, dict) and item.get("text")
            ]
            if text_parts:
                st.markdown("\n\n".join(text_parts))
                with st.expander("Raw agent message"):
                    st.json(message)
                return
        st.json(message)
    elif isinstance(message, list):
        st.json(message)
    else:
        st.markdown(str(message))


st.set_page_config(
    page_title="GroundPatrol",
    page_icon="🦀",
    layout="wide",
)

st.title("GroundPatrol")
st.caption("Governed coastal operations: observe → authorise → verify → dispatch or hand off")

with st.sidebar:
    st.header("Patrol controls")
    beach_id = st.selectbox("Beach", ["west-bay-01"])
    feed_label = st.radio(
        "Evidence mode",
        ["Deterministic fixture", "Live weather overlay"],
        help="Live mode replaces only wind and visibility with Open-Meteo observations.",
    )
    scenario_label = st.selectbox("Operating state", list(SCENARIOS))
    st.divider()
    st.caption(
        "Access, habitat, people-presence and debris are synthetic demo inputs. "
        "Live mode does not relabel them as sensor observations."
    )

objective = st.text_area(
    "Patrol objective",
    value=(
        "Assess the debris situation. If an autonomous collection pass is cleared, "
        "create the bounded collection work order; otherwise stop or hand off safely."
    ),
    height=110,
)

run = st.button("Run governed patrol", type="primary", use_container_width=True)

if run:
    selected_feed = "fixture" if feed_label == "Deterministic fixture" else "live"
    selected_scenario = SCENARIOS[scenario_label]
    os.environ["GROUNDPATROL_FEED"] = selected_feed
    os.environ["GROUNDPATROL_SCENARIO"] = selected_scenario

    prompt = f"Patrol {beach_id}. {objective}"
    with st.spinner("GroundPatrol is observing and evaluating the operating envelope..."):
        try:
            result = build_agent()(prompt)
        except Exception as exc:  # surface operational failures rather than hiding them
            st.error(f"Patrol failed before completion: {type(exc).__name__}: {exc}")
        else:
            receipt = _latest_json("receipts")
            receipt_id = receipt.get("receipt_sha256") if receipt else None
            st.session_state["last_result"] = result.message
            st.session_state["current_receipt"] = receipt
            st.session_state["current_work_order"] = _work_order_for_receipt(receipt_id)
            st.session_state["last_run_controls"] = {
                "beach_id": beach_id,
                "feed": selected_feed,
                "scenario": selected_scenario,
            }
            st.success("Patrol cycle completed")

receipt = st.session_state.get("current_receipt")
receipt_id = receipt.get("receipt_sha256") if receipt else None
work_order = st.session_state.get("current_work_order")
last_controls = st.session_state.get("last_run_controls")
current_controls = {
    "beach_id": beach_id,
    "feed": "fixture" if feed_label == "Deterministic fixture" else "live",
    "scenario": SCENARIOS[scenario_label],
}

if last_controls and current_controls != last_controls:
    st.warning(
        "Controls have changed since the displayed patrol result. "
        "Run a new governed patrol before treating the result as current."
    )

col1, col2, col3 = st.columns(3)

with col1:
    st.subheader("Agent outcome")
    if "last_result" in st.session_state:
        _render_result(st.session_state["last_result"])
    else:
        st.info("Run a patrol to populate the governed outcome.")

with col2:
    st.subheader("Decision receipt for this run")
    if receipt:
        gate = receipt.get("gate_result", {})
        st.metric("Gate", gate.get("decision", "UNKNOWN"))
        st.caption(f"Snapshot: {str(receipt.get('snapshot_id', ''))[:16]}…")
        st.caption(f"Receipt: {str(receipt_id or '')[:16]}…")
        with st.expander("Inspect receipt"):
            st.json(receipt)
    else:
        st.info("No patrol has been run in this UI session yet.")

with col3:
    st.subheader("Work order for this decision")
    if work_order:
        st.metric("Dispatch", work_order.get("status", "UNKNOWN"))
        st.caption(f"Work order: {work_order.get('work_order_id', '')}")
        st.caption(f"Beach: {work_order.get('beach_id', '')}")
        with st.expander("Inspect work order"):
            st.json(work_order)
    elif receipt:
        st.info("No work order was dispatched from this decision receipt.")
    else:
        st.info("No patrol decision exists in this UI session yet.")

st.divider()
st.caption(
    "GroundPatrol does not let the language model authorise consequential action. "
    "The model proposes; deterministic controls decide; the finalizer checks; the trace records."
)
