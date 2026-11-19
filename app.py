"""
Research Agency Lab — Controllable Web App
Streamlit control panel for the hierarchical multi-agent research system.
"""

import os
import time
from datetime import datetime
from pathlib import Path

import streamlit as st
from dotenv import load_dotenv

load_dotenv()

from lab.templates import TEMPLATES, get_template, get_template_names
from lab.core import run_research

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
# Session state
# ---------------------------------------------------------------------------

if "history" not in st.session_state:
    st.session_state.history = []
if "last_result" not in st.session_state:
    st.session_state.last_result = None
if "running" not in st.session_state:
    st.session_state.running = False

OUTPUTS_DIR = Path("outputs")
OUTPUTS_DIR.mkdir(exist_ok=True)

# ---------------------------------------------------------------------------
# Sidebar — Control Panel
# ---------------------------------------------------------------------------

with st.sidebar:
    st.title("🔬 Control Panel")
    st.caption("Research Agency Lab")

    st.divider()
    st.subheader("Model Settings")

    provider_hint = st.selectbox(
        "Quick preset",
        [
            "OpenAI (gpt-4o-mini)",
            "OpenAI (gpt-4o)",
            "Local Ollama (llama3.2)",
            "Local Ollama (mistral)",
            "Groq (llama-3.3-70b)",
            "Custom",
        ],
        index=0,
    )

    model_map = {
        "OpenAI (gpt-4o-mini)": "gpt-4o-mini",
        "OpenAI (gpt-4o)": "gpt-4o",
        "Local Ollama (llama3.2)": "ollama/llama3.2",
        "Local Ollama (mistral)": "ollama/mistral",
        "Groq (llama-3.3-70b)": "groq/llama-3.3-70b-versatile",
    }

    if provider_hint == "Custom":
        model = st.text_input("Specialist model", value=os.getenv("MODEL", "gpt-4o-mini"))
        manager_model = st.text_input("Manager model (optional)", value=os.getenv("MANAGER_MODEL", ""))
    else:
        model = model_map[provider_hint]
        manager_model = st.text_input(
            "Manager model (optional, stronger recommended)",
            value="" if "Ollama" in provider_hint else "gpt-4o",
            help="Leave empty to use the same model as specialists",
        )

    temperature = st.slider("Temperature", 0.0, 1.0, 0.4, 0.05)

    st.divider()
    st.subheader("Tools & Capabilities")

    enable_web = st.toggle("Web Search (Serper)", value=bool(os.getenv("SERPER_API_KEY")), help="Requires SERPER_API_KEY")
    enable_arxiv = st.toggle("arXiv Academic Search", value=True)
    enable_code = st.toggle("Code Interpreter", value=True)
    enable_memory = st.toggle("Agent Memory", value=False, help="Remember across runs in this session (experimental)")

    st.divider()
    st.subheader("API Keys Status")

    def key_status(name: str) -> str:
        return "✅" if os.getenv(name) else "❌"

    st.markdown(
        f"""
| Provider | Status |
|----------|--------|
| OpenAI | {key_status("OPENAI_API_KEY")} |
| Anthropic | {key_status("ANTHROPIC_API_KEY")} |
| Groq | {key_status("GROQ_API_KEY")} |
| Serper | {key_status("SERPER_API_KEY")} |
"""
    )
    st.caption("Set keys in `.env` file. Restart app after changes.")

    st.divider()
    if st.button("🗑️ Clear History", use_container_width=True):
        st.session_state.history = []
        st.session_state.last_result = None
        st.rerun()

# ---------------------------------------------------------------------------
# Main area
# ---------------------------------------------------------------------------

st.title("🔬 Research Agency Lab")
st.markdown(
    "Hierarchical multi-agent research system. "
    "A **Research Director** manages Literature Analyst, Data Scientist, "
    "Experiment Designer, and Research Writer."
)

# Template selector
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

# Query input
default_prompt = template["prompt"]
user_input = st.text_area(
    "Research Question / Topic",
    value=default_prompt,
    height=140,
    placeholder="Enter your research question or complete the template prompt...",
)

run_col, status_col = st.columns([1, 3])

with run_col:
    run_clicked = st.button(
        "🚀 Launch Research Lab",
        type="primary",
        use_container_width=True,
        disabled=st.session_state.running or not user_input.strip(),
    )

# ---------------------------------------------------------------------------
# Execution
# ---------------------------------------------------------------------------

if run_clicked and user_input.strip():
    st.session_state.running = True
    full_request = user_input.strip()

    with st.status("🔬 Research Lab is working...", expanded=True) as status:
        st.write("Initializing agents and tools...")
        st.write(f"**Model:** `{model}`")
        if manager_model:
            st.write(f"**Manager:** `{manager_model}`")
        st.write(f"**Tools:** web={enable_web}, arxiv={enable_arxiv}, code={enable_code}, memory={enable_memory}")

        try:
            start = time.time()
            result = run_research(
                user_request=full_request,
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

            status.update(label=f"✅ Research complete in {elapsed:.1f}s", state="complete")

            # Save
            ts = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_name = "".join(c if c.isalnum() or c in "-_" else "_" for c in full_request[:40])
            out_path = OUTPUTS_DIR / f"{ts}_{safe_name}.md"
            out_path.write_text(f"# Research Report\n\n**Request:** {full_request}\n\n---\n\n{result}", encoding="utf-8")

            st.session_state.last_result = {
                "request": full_request,
                "result": result,
                "model": model,
                "elapsed": elapsed,
                "path": str(out_path),
                "timestamp": ts,
            }
            st.session_state.history.insert(0, st.session_state.last_result)

        except Exception as e:
            status.update(label="❌ Error", state="error")
            st.error(f"Research failed: {e}")
            st.exception(e)
        finally:
            st.session_state.running = False

# ---------------------------------------------------------------------------
# Results
# ---------------------------------------------------------------------------

if st.session_state.last_result:
    res = st.session_state.last_result
    st.divider()
    st.subheader("📄 Latest Report")
    st.caption(f"Model: `{res['model']}` · Time: {res['elapsed']:.1f}s · Saved: `{res['path']}`")

    st.markdown(res["result"])

    st.download_button(
        "⬇️ Download Markdown",
        data=res["result"],
        file_name=f"research_{res['timestamp']}.md",
        mime="text/markdown",
    )

# ---------------------------------------------------------------------------
# History
# ---------------------------------------------------------------------------

if st.session_state.history:
    st.divider()
    with st.expander(f"📚 Research History ({len(st.session_state.history)})", expanded=False):
        for i, item in enumerate(st.session_state.history):
            st.markdown(f"**{i+1}. {item['request'][:80]}...**")
            st.caption(f"{item['timestamp']} · {item['model']} · {item['elapsed']:.1f}s")
            if st.button("Show", key=f"show_{i}"):
                st.markdown(item["result"])
            st.divider()
