import os
import streamlit as st
from datetime import datetime
from langchain_core.messages import HumanMessage
from main import app, stateless_app

st.set_page_config(
    page_title="Travel Planning Console",
    page_icon="🧭",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ══════════════════════════════════════════════════════════════════════════════
# Styling — light, neutral, enterprise look
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

:root {
    --bg: #f5f7fa;
    --surface: #ffffff;
    --border: #e2e8f0;
    --border-strong: #cbd5e1;
    --text: #0f172a;
    --text-muted: #64748b;
    --accent: #1d4ed8;
    --accent-hover: #1e40af;
    --accent-soft: #eff4ff;
    --success: #15803d;
    --success-soft: #ecfdf3;
}

html, body, .stApp {
    font-family: 'Inter', -apple-system, 'Segoe UI', sans-serif;
    background-color: var(--bg);
    color: var(--text);
}

/* Layout */
.block-container { padding-top: 1.5rem; padding-bottom: 3rem; max-width: 1180px; }
#MainMenu, footer { visibility: hidden; }
header[data-testid="stHeader"] { background: transparent; }

/* Page header */
.page-header {
    display: flex; justify-content: space-between; align-items: flex-end;
    padding-bottom: 1rem; margin-bottom: 1.5rem;
    border-bottom: 1px solid var(--border);
}
.page-title { font-size: 1.5rem; font-weight: 700; color: var(--text); margin: 0; letter-spacing: -0.01em; }
.page-sub { font-size: 0.9rem; color: var(--text-muted); margin-top: 0.25rem; }
.page-meta { font-size: 0.8rem; color: var(--text-muted); text-align: right; }

/* Section labels */
.section-label {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em;
    text-transform: uppercase; color: var(--text-muted); margin: 0 0 0.5rem;
}
.section-title {
    font-size: 1.05rem; font-weight: 600; color: var(--text);
    margin: 1.75rem 0 0.75rem;
}

/* Inputs */
.stTextArea textarea, .stTextInput input {
    background: var(--surface) !important;
    border: 1px solid var(--border-strong) !important;
    border-radius: 8px !important;
    color: var(--text) !important;
    font-size: 0.95rem !important;
}
.stTextArea textarea:focus, .stTextInput input:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px rgba(29,78,216,0.12) !important;
}
.stTextArea textarea::placeholder { color: #94a3b8 !important; }
.stTextInput label, .stTextArea label {
    color: var(--text) !important; font-size: 0.85rem !important; font-weight: 500 !important;
}

/* Buttons — secondary (templates) */
div[data-testid="stButton"] > button {
    background: var(--surface);
    color: var(--text);
    border: 1px solid var(--border-strong);
    border-radius: 8px;
    font-size: 0.85rem;
    font-weight: 500;
    padding: 0.45rem 0.9rem;
    transition: border-color 0.15s, background 0.15s;
}
div[data-testid="stButton"] > button:hover {
    border-color: var(--accent); color: var(--accent); background: var(--accent-soft);
}

/* Buttons — primary */
div[data-testid="stButton"] > button[kind="primary"] {
    background: var(--accent); color: #ffffff; border: 1px solid var(--accent);
    font-weight: 600; font-size: 0.95rem; padding: 0.65rem 1.5rem;
}
div[data-testid="stButton"] > button[kind="primary"]:hover {
    background: var(--accent-hover); border-color: var(--accent-hover); color: #ffffff;
}

/* Download button */
div[data-testid="stDownloadButton"] > button {
    background: var(--surface); color: var(--text);
    border: 1px solid var(--border-strong); border-radius: 8px; font-weight: 500;
}
div[data-testid="stDownloadButton"] > button:hover {
    border-color: var(--accent); color: var(--accent);
}

/* Pipeline tracker */
.tracker { display: flex; gap: 0.75rem; margin: 0.5rem 0 1rem; }
.step {
    flex: 1; background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 0.85rem 1rem;
}
.step-num { font-size: 0.7rem; font-weight: 600; letter-spacing: 0.08em; color: var(--text-muted); text-transform: uppercase; }
.step-name { font-size: 0.95rem; font-weight: 600; margin-top: 0.15rem; color: var(--text); }
.step-state { font-size: 0.78rem; margin-top: 0.35rem; color: var(--text-muted); }
.step.done { border-color: #bbf7d0; background: var(--success-soft); }
.step.done .step-state { color: var(--success); font-weight: 500; }
.step.active { border-color: var(--accent); background: var(--accent-soft); }
.step.active .step-state { color: var(--accent); font-weight: 500; }

/* Metrics */
.metric-row { display: flex; gap: 0.75rem; margin: 0.5rem 0 0.5rem; }
.metric-box {
    flex: 1; background: var(--surface); border: 1px solid var(--border);
    border-radius: 10px; padding: 0.9rem 1.1rem;
}
.metric-lbl { font-size: 0.72rem; font-weight: 600; color: var(--text-muted); text-transform: uppercase; letter-spacing: 0.08em; }
.metric-val { font-size: 1.4rem; font-weight: 700; color: var(--text); margin-top: 0.2rem; }
.metric-val.ok { color: var(--success); }

/* Result panels */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--surface);
    border-radius: 10px;
}
.stTabs [data-baseweb="tab-list"] { gap: 0.25rem; border-bottom: 1px solid var(--border); }
.stTabs [data-baseweb="tab"] {
    font-weight: 500; font-size: 0.9rem; color: var(--text-muted); padding: 0.6rem 1rem;
}
.stTabs [aria-selected="true"] { color: var(--accent) !important; }
.stTabs [data-baseweb="tab-highlight"] { background-color: var(--accent) !important; }

/* Markdown content */
.stMarkdown p, .stMarkdown li, .stMarkdown td, .stMarkdown th { color: var(--text); line-height: 1.65; }
.stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4 { color: var(--text); }
.stMarkdown code { background: #f1f5f9; color: #0f172a; padding: 0.1em 0.4em; border-radius: 4px; }

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}
.side-brand { font-size: 1rem; font-weight: 700; color: var(--text); }
.side-brand-sub { font-size: 0.78rem; color: var(--text-muted); margin-bottom: 0.5rem; }
.side-heading {
    font-size: 0.72rem; font-weight: 600; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-muted); margin: 1.25rem 0 0.5rem;
}
.side-item {
    display: flex; justify-content: space-between; padding: 0.4rem 0;
    font-size: 0.85rem; color: var(--text); border-bottom: 1px solid #f1f5f9;
}
.side-item span:last-child { color: var(--text-muted); }

/* Save notice */
.save-note {
    background: var(--surface); border: 1px solid var(--border); border-radius: 8px;
    padding: 0.65rem 1rem; color: var(--text-muted); font-size: 0.85rem;
}
.save-note code { font-size: 0.82rem; }
</style>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════════════
PIPELINE = [
    ("flight_agent", "Flight Search"),
    ("hotel_agent", "Accommodation"),
    ("itinerary_agent", "Itinerary"),
    ("final_agent", "Final Plan"),
]

TEMPLATES = {
    "Japan, 7 days": "Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs",
    "Paris, 5 days": "Plan a 5-day Paris trip including flights, hotels and sightseeing",
    "Dubai, weekend": "Plan a weekend trip to Dubai including flights, hotels and key attractions",
    "Bali, 10 days": "Plan a 10-day budget trip to Bali including flights, hotels and activities",
}

if "query_text" not in st.session_state:
    st.session_state.query_text = ""
if "result" not in st.session_state:
    st.session_state.result = None


def set_template(text: str):
    st.session_state.query_text = text


def render_tracker(states: dict) -> str:
    html = "<div class='tracker'>"
    for i, (key, label) in enumerate(PIPELINE, start=1):
        state = states.get(key, "pending")
        text = {"done": "Completed", "active": "In progress", "pending": "Pending"}[state]
        html += (
            f"<div class='step {state}'>"
            f"<div class='step-num'>Step {i}</div>"
            f"<div class='step-name'>{label}</div>"
            f"<div class='step-state'>{text}</div>"
            f"</div>"
        )
    return html + "</div>"


# ══════════════════════════════════════════════════════════════════════════════
# Sidebar
# ══════════════════════════════════════════════════════════════════════════════
with st.sidebar:
    st.markdown("<div class='side-brand'>Travel Planning Console</div>", unsafe_allow_html=True)
    st.markdown("<div class='side-brand-sub'>Multi-agent trip planning</div>", unsafe_allow_html=True)

    st.markdown("<div class='side-heading'>Session</div>", unsafe_allow_html=True)
    thread_id = st.text_input(
        "User ID (optional)",
        value="",
        help="Leave blank for a one-off request. Enter the same ID again to save and resume that user's conversation history.",
    )
    if thread_id.strip():
        st.caption("Conversation history will be saved for this ID.")
    else:
        st.caption("Without a user ID, this request won't be saved as conversation history.")

    st.markdown("<div class='side-heading'>Workflow</div>", unsafe_allow_html=True)
    for i, (_, label) in enumerate(PIPELINE, start=1):
        st.markdown(
            f"<div class='side-item'><span>{label}</span><span>Step {i}</span></div>",
            unsafe_allow_html=True,
        )

    st.markdown("<div class='side-heading'>Platform</div>", unsafe_allow_html=True)
    for name, role in [
        ("LangGraph", "Orchestration"),
        ("Groq · LLaMA 3.3 70B", "Language model"),
        ("PostgreSQL", "Persistence"),
        ("Tavily", "Web search"),
        ("AviationStack", "Flight data"),
    ]:
        st.markdown(
            f"<div class='side-item'><span>{name}</span><span>{role}</span></div>",
            unsafe_allow_html=True,
        )

# ══════════════════════════════════════════════════════════════════════════════
# Header
# ══════════════════════════════════════════════════════════════════════════════
st.markdown(f"""
<div class="page-header">
    <div>
        <div class="page-title">Travel Planning Console</div>
        <div class="page-sub">Generate flight, accommodation and itinerary recommendations from a single request.</div>
    </div>
    <div class="page-meta">{datetime.now().strftime("%A, %d %B %Y")}</div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# Request form
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("<div class='section-label'>New request</div>", unsafe_allow_html=True)

with st.container(border=True):
    st.markdown("<div class='section-label'>Templates</div>", unsafe_allow_html=True)
    tcols = st.columns(len(TEMPLATES))
    for tc, (label, text) in zip(tcols, TEMPLATES.items()):
        with tc:
            st.button(label, key=f"tpl_{label}", on_click=set_template, args=(text,),
                      use_container_width=True)

    user_query = st.text_area(
        "Trip description",
        key="query_text",
        placeholder="Example: Plan a complete 7-day Japan trip including flights, hotels and sightseeing under ₹2 lakhs",
        height=110,
    )

    generate = st.button("Generate travel plan", type="primary", use_container_width=True)

# ══════════════════════════════════════════════════════════════════════════════
# Pipeline execution
# ══════════════════════════════════════════════════════════════════════════════
if generate:
    if not user_query.strip():
        st.warning("Enter a trip description before generating a plan.")
    else:
        user_id = thread_id.strip()
        runner = app if user_id else stateless_app
        config = {"configurable": {"thread_id": user_id}} if user_id else {}
        collected = {"flight_results": "", "hotel_results": "",
                     "itinerary": "", "final_response": "", "llm_calls": 0}

        st.markdown("<div class='section-title'>Processing</div>", unsafe_allow_html=True)
        tracker_slot = st.empty()
        states = {key: "pending" for key, _ in PIPELINE}
        states[PIPELINE[0][0]] = "active"
        tracker_slot.markdown(render_tracker(states), unsafe_allow_html=True)

        error = None
        try:
            with st.spinner("Agents are working on your request..."):
                for chunk in runner.stream(
                    {
                        "messages": [HumanMessage(content=user_query)],
                        "user_query": user_query,
                        "flight_results": "",
                        "hotel_results": "",
                        "itinerary": "",
                        "llm_calls": 0,
                    },
                    config=config,
                    stream_mode="updates",
                ):
                    for node_name, state_update in chunk.items():
                        if node_name == "flight_agent":
                            collected["flight_results"] = state_update.get("flight_results", "")
                        elif node_name == "hotel_agent":
                            collected["hotel_results"] = state_update.get("hotel_results", "")
                        elif node_name == "itinerary_agent":
                            collected["itinerary"] = state_update.get("itinerary", "")
                        elif node_name == "final_agent":
                            msgs = state_update.get("messages", [])
                            collected["final_response"] = msgs[-1].content if msgs else ""

                        collected["llm_calls"] = state_update.get("llm_calls", collected["llm_calls"])

                        # Update tracker
                        if node_name in states:
                            states[node_name] = "done"
                            keys = [k for k, _ in PIPELINE]
                            idx = keys.index(node_name)
                            if idx + 1 < len(keys):
                                states[keys[idx + 1]] = "active"
                            tracker_slot.markdown(render_tracker(states), unsafe_allow_html=True)
        except Exception as exc:  # surface failures clearly instead of a raw traceback
            error = exc

        if error:
            st.error(f"The request could not be completed: {error}")
        else:
            now = datetime.now()
            filename = f"travel_plan_{now.strftime('%Y%m%d_%H%M%S')}.md"
            file_content = f"""# Travel Plan
**Query:** {user_query}
**Generated:** {now.strftime("%Y-%m-%d %H:%M:%S")}
**User ID:** {user_id or 'Not provided (history not saved)'}

---

## Flight Information
{collected['flight_results'] or 'N/A'}

---

## Accommodation
{collected['hotel_results'] or 'N/A'}

---

## Itinerary
{collected['itinerary'] or 'N/A'}

---

## Final Travel Plan
{collected['final_response'] or 'N/A'}

---
*LLM Calls: {collected['llm_calls']}*
"""
            save_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "travel_plans")
            os.makedirs(save_dir, exist_ok=True)
            with open(os.path.join(save_dir, filename), "w", encoding="utf-8") as f:
                f.write(file_content)

            # Persist so results survive reruns (e.g. clicking Download)
            st.session_state.result = {
                "collected": collected,
                "query": user_query,
                "user": user_id,
                "generated": now.strftime("%d %b %Y, %H:%M"),
                "filename": filename,
                "file_content": file_content,
            }

# ══════════════════════════════════════════════════════════════════════════════
# Results
# ══════════════════════════════════════════════════════════════════════════════
res = st.session_state.result
if res:
    c = res["collected"]

    st.markdown("<div class='section-title'>Results</div>", unsafe_allow_html=True)

    st.markdown(f"""
    <div class="metric-row">
        <div class="metric-box"><div class="metric-lbl">Agents run</div><div class="metric-val">{len(PIPELINE)}</div></div>
        <div class="metric-box"><div class="metric-lbl">LLM calls</div><div class="metric-val">{c['llm_calls']}</div></div>
        <div class="metric-box"><div class="metric-lbl">Generated</div><div class="metric-val" style="font-size:1rem;padding-top:0.35rem;">{res['generated']}</div></div>
        <div class="metric-box"><div class="metric-lbl">Status</div><div class="metric-val ok" style="font-size:1.1rem;padding-top:0.3rem;">Completed</div></div>
    </div>
    """, unsafe_allow_html=True)

    st.caption(f"Request: {res['query']}")

    tab_plan, tab_flights, tab_hotels, tab_itin = st.tabs(
        ["Final plan", "Flights", "Accommodation", "Itinerary"]
    )
    with tab_plan:
        with st.container(border=True):
            st.markdown(c["final_response"] or "_No final response._")
    with tab_flights:
        with st.container(border=True):
            st.markdown(c["flight_results"] or "_No flight data returned._")
    with tab_hotels:
        with st.container(border=True):
            st.markdown(c["hotel_results"] or "_No accommodation data returned._")
    with tab_itin:
        with st.container(border=True):
            st.markdown(c["itinerary"] or "_No itinerary generated._")

    st.markdown("<br>", unsafe_allow_html=True)
    dl_col, info_col = st.columns([1, 3])
    with dl_col:
        st.download_button(
            "Download plan (.md)",
            data=res["file_content"],
            file_name=res["filename"],
            mime="text/markdown",
            use_container_width=True,
        )
    with info_col:
        st.markdown(
            f"<div class='save-note'>Saved to <code>travel_plans/{res['filename']}</code></div>",
            unsafe_allow_html=True,
        )