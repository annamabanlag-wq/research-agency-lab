"""
Research Agency Lab — Controllable Multi-User Simulation Environment
Streamlit app with auth, persistent labs, vector memory, hierarchical agents.
"""

from __future__ import annotations

import os
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List

import streamlit as st
import yaml
from dotenv import load_dotenv

load_dotenv()

from lab.templates import TEMPLATES, get_template, get_template_names
from lab.core import run_research
from lab.memory import get_lab_memory, CHROMA_AVAILABLE

# ---------------------------------------------------------------------------
# Paths & Constants
# ---------------------------------------------------------------------------

DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
LABS_DIR = DATA_DIR / "labs"
OUTPUTS_DIR = Path("outputs")
USERS_FILE = Path("config/users.yaml")

LABS_DIR.mkdir(parents=True, exist_ok=True)
OUTPUTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Page config
# ---------------------------------------------------------------------------

st.set_page_config(
    page_title="Research Agency Lab",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Simple Auth (streamlit-authenticator)
# ---------------------------------------------------------------------------

def load_auth():
    try:
        import streamlit_authenticator as stauth
        with open(USERS_FILE) as f:
            config = yaml.safe_load(f)
        authenticator = stauth.Authenticate(
            config["credentials"],
            config["cookie"]["name"],
            config["cookie"]["key"],
            config["cookie"]["expiry_days"],
        )
        return authenticator, config
    except Exception as e:
        st.warning(f"Auth not fully configured ({e}). Running in open mode.")
        return None, None


authenticator, auth_config = load_auth()

if authenticator:
    authenticator.login(location="main")
    if st.session_state.get("authentication_status") is False:
        st.error("Username/password is incorrect")
        st.stop()
    elif st.session_state.get("authentication_status") is None:
        st.info("Please log in. Default users: admin / admin123  or  researcher / research123")
        st.stop()
    name = st.session_state.get("name", "User")
    username = st.session_state.get("username", "user")
else:
    name = "Open User"
    username = "open"

# ---------------------------------------------------------------------------
# Lab (Simulation Environment) Management
# ---------------------------------------------------------------------------

def list_labs() -> List[Dict[str, Any]]:
    labs = []
    for p in LABS_DIR.glob("*.json"):
        try:
            labs.append(json.loads(p.read_text()))
        except Exception:
            pass
    return sorted(labs, key=lambda x: x.get("updated", ""), reverse=True)


def get_lab(lab_id: str) -> Dict[str, Any]:
    path = LABS_DIR / f"{lab_id}.json"
    if path.exists():
        return json.loads(path.read_text())
    return {}


def save_lab(lab: Dict[str, Any]) -> None:
    lab["updated"] = datetime.utcnow().isoformat()
    path = LABS_DIR / f"{lab['id']}.json"
    path.write_text(json.dumps(lab, indent=2))


def create_lab(name: str, description: str, owner: str) -> Dict[str, Any]:
    lab_id = f"lab_{int(time.time())}_{owner[:8]}"
    lab = {
        "id": lab_id,
        "name": name,
        "description": description,
        "owner": owner,
        "created": datetime.utcnow().isoformat(),
        "updated": datetime.utcnow().isoformat(),
        "runs": 0,
    }
    save_lab(lab)
    return lab


# ---------------------------------------------------------------------------
# Session state
# ---------------------------------------------------------------------------

if "current_lab" not in st.session_state:
    st.session_state.current_lab = None
if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "running" not in st.session_state:
    st.session_state.running = False

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🔬 Research Agency Lab")
    st.caption(f"Logged in as **{name}**")
    if authenticator:
        authenticator.logout("Logout", "sidebar")

    st.divider()
    st.subheader("🧪 Active Lab (Simulation)")

    labs = list_labs()
    lab_names = {l["id"]: f"{l['name']} ({l.get('runs', 0)} runs)" for l in labs}

    if labs:
        selected = st.selectbox(
            "Select Lab",
            options=list(lab_names.keys()),
            format_func=lambda x: lab_names.get(x, x),
            key="lab_select",
        )
        st.session_state.current_lab = get_lab(selected)
    else:
        st.info("No labs yet. Create one below.")

    with st.expander("➕ Create New Lab", expanded=not labs):
        new_name = st.text_input("Lab Name", placeholder="e.g. Multi-Agent Memory Study")
        new_desc = st.text_area("Description", height=80)
        if st.button("Create Lab", type="primary") and new_name:
            lab = create_lab(new_name, new_desc, username)
            st.session_state.current_lab = lab
            st.success(f"Created lab: {lab['name']}")
            st.rerun()

    if st.session_state.current_lab:
        lab = st.session_state.current_lab
        st.markdown(f"**{lab['name']}**")
        st.caption(lab.get("description", "")[:120])
        mem = get_lab_memory(lab["id"])
        st.metric("Knowledge entries", mem.count() if CHROMA_AVAILABLE else "N/A")

    st.divider()
    st.subheader("Model & Tools")

    provider = st.selectbox(
        "Model preset",
        [
            "OpenAI (gpt-4o-mini)",
            "OpenAI (gpt-4o)",
            "Local Ollama (llama3.2)",
            "Local Ollama (mistral)",
            "Groq (llama-3.3-70b)",
            "Custom",
        ],
    )
    model_map = {
        "OpenAI (gpt-4o-mini)": "gpt-4o-mini",
        "OpenAI (gpt-4o)": "gpt-4o",
        "Local Ollama (llama3.2)": "ollama/llama3.2",
        "Local Ollama (mistral)": "ollama/mistral",
        "Groq (llama-3.3-70b)": "groq/llama-3.3-70b-versatile",
    }
    if provider == "Custom":
        model = st.text_input("Specialist model", value=os.getenv("MODEL", "gpt-4o-mini"))
        manager_model = st.text_input("Manager model", value=os.getenv("MANAGER_MODEL", ""))
    else:
        model = model_map[provider]
        manager_model = st.text_input("Manager model (optional)", value="gpt-4o" if "Ollama" not in provider else "")

    temperature = st.slider("Temperature", 0.0, 1.0, 0.4, 0.05)

    enable_web = st.toggle("Web Search (Serper)", value=bool(os.getenv("SERPER_API_KEY")))
    enable_arxiv = st.toggle("arXiv", value=True)
    enable_code = st.toggle("Code Interpreter", value=True)
    enable_memory = st.toggle("Persistent Lab Memory", value=True)

    st.divider()
    st.caption("API Keys status")
    for k in ["OPENAI_API_KEY", "SERPER_API_KEY", "GROQ_API_KEY", "ANTHROPIC_API_KEY"]:
        st.write(f"{'✅' if os.getenv(k) else '❌'} {k}")

# ---------------------------------------------------------------------------
# Main Content
# ---------------------------------------------------------------------------

st.title("🔬 Research Agency Lab — Simulation Environment")
st.markdown(
    "Multi-user hierarchical research laboratory. "
    "Create **Labs**, run research simulations, build shared knowledge with persistent vector memory."
)

if not st.session_state.current_lab:
    st.warning("Create or select a Lab in the sidebar to begin a research simulation.")
    st.stop()

lab = st.session_state.current_lab
st.info(f"**Active Simulation Lab:** {lab['name']}  ·  Owner: {lab.get('owner')}  ·  ID: `{lab['id']}`")

# Templates
col1, col2 = st.columns([1, 2])
with col1:
    template_name = st.selectbox(
        "Research Template",
        get_template_names(),
        format_func=lambda n: f"{TEMPLATES[n]['icon']} {n}",
    )
template = get_template(template_name)
with col2:
    st.info(template["description"])

user_input = st.text_area(
    "Research Question / Simulation Brief",
    value=template["prompt"],
    height=140,
)

run_clicked = st.button(
    "🚀 Launch Research Simulation",
    type="primary",
    disabled=st.session_state.running or not user_input.strip(),
    use_container_width=False,
)

# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

if run_clicked and user_input.strip():
    st.session_state.running = True
    full_request = user_input.strip()

    with st.status("🔬 Lab simulation in progress...", expanded=True) as status:
        st.write(f"Lab: **{lab['name']}**")
        st.write(f"Model: `{model}` | Manager: `{manager_model or model}`")
        st.write(f"Memory: {'ON' if enable_memory else 'OFF'} | Tools: web={enable_web}, arxiv={enable_arxiv}, code={enable_code}")

        try:
            start = time.time()
            result = run_research(
                user_request=full_request,
                lab_id=lab["id"],
                model=model,
                manager_model=manager_model or None,
                temperature=temperature,
                enable_web_search=enable_web,
                enable_arxiv=enable_arxiv,
                enable_code=enable_code,
                enable_memory=enable_memory,
                verbose=True,
            )
            elapsed = time.time() - start

            # Update lab stats
            lab["runs"] = lab.get("runs", 0) + 1
            save_lab(lab)

            status.update(label=f"✅ Simulation complete in {elapsed:.1f}s", state="complete")

            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            out_path = OUTPUTS_DIR / f"{lab['id']}_{ts}.md"
            out_path.write_text(
                f"# Research Report\n\n**Lab:** {lab['name']}\n**Request:** {full_request}\n\n---\n\n{result}",
                encoding="utf-8",
            )

            st.session_state.last_result = {
                "request": full_request,
                "result": result,
                "model": model,
                "elapsed": elapsed,
                "path": str(out_path),
                "timestamp": ts,
                "lab": lab["name"],
            }
            st.session_state.history.insert(0, st.session_state.last_result)

        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(str(e))
            st.exception(e)
        finally:
            st.session_state.running = False

# ---------------------------------------------------------------------------
# Results & History
# ---------------------------------------------------------------------------

if st.session_state.last_result:
    res = st.session_state.last_result
    st.divider()
    st.subheader("📄 Latest Simulation Report")
    st.caption(f"Lab: {res.get('lab')} · Model: `{res['model']}` · {res['elapsed']:.1f}s · `{res['path']}`")
    st.markdown(res["result"])
    st.download_button("⬇️ Download Markdown", data=res["result"], file_name=f"report_{res['timestamp']}.md")

if st.session_state.history:
    with st.expander(f"📚 Session History ({len(st.session_state.history)})"):
        for i, item in enumerate(st.session_state.history):
            st.markdown(f"**{item['request'][:90]}...**")
            st.caption(f"{item.get('lab')} · {item['timestamp']} · {item['elapsed']:.1f}s")
            if st.button("View", key=f"h_{i}"):
                st.markdown(item["result"])
