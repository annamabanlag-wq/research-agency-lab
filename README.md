# 🔬 Research Agency Lab

**Controllable hierarchical multi-agent research system**

A Research Director manages a team of specialists (Literature Analyst, Data Scientist, Experiment Designer, Research Writer).  
Includes a full **Streamlit control panel** so you can run, configure, and monitor research projects from one app.

---

## Features

- ✅ Hierarchical multi-agent system (true manager + specialists)
- ✅ **Streamlit web UI** — one app you control
- ✅ Pre-built research templates (Literature Review, Experiment Design, Competitive Analysis, etc.)
- ✅ Rich tools: Serper web search, arXiv, Code Interpreter, file tools, website scraping
- ✅ Cloud models (OpenAI, Anthropic, Groq, Gemini…) + **local Ollama**
- ✅ Agent memory toggle
- ✅ Report history + Markdown download
- ✅ CLI fallback

---

## Quick Start

```bash
cd research-agency-lab

python -m venv venv
source venv/bin/activate          # Windows: venv\Scripts\activate

pip install -r requirements.txt

cp .env.example .env
# Edit .env and add at least OPENAI_API_KEY (or configure Ollama)
```

### Launch the controllable app

```bash
streamlit run app.py
```

The browser will open with the full control panel.

### CLI alternative

```bash
python agency.py "Your research question here"
```

---

## Using the App

1. **Sidebar**
   - Choose model preset or custom model
   - Set manager model (stronger model recommended for the Director)
   - Toggle tools (web search, arXiv, code interpreter)
   - Enable/disable memory
   - Check API key status

2. **Main panel**
   - Pick a research template or start from blank
   - Enter / refine your research question
   - Click **Launch Research Lab**
   - Watch progress and receive the final report
   - Download Markdown or browse history

---

## Local Models (Ollama)

```bash
ollama pull llama3.2
# or llama3.1:8b / mistral / qwen2.5
```

In the app sidebar choose the Ollama preset, or set in `.env`:

```env
MODEL=ollama/llama3.2
MANAGER_MODEL=ollama/llama3.1:8b
```

---

## Recommended Setup for Quality Research

```env
OPENAI_API_KEY=sk-...
SERPER_API_KEY=...          # free at serper.dev
MODEL=gpt-4o-mini
MANAGER_MODEL=gpt-4o        # stronger director
```

---

## Project Structure

```
research-agency-lab/
├── app.py                 # Streamlit control panel (main entry)
├── agency.py              # CLI entry point
├── lab/
│   ├── core.py            # Agents, tools, hierarchical crew
│   └── templates.py       # Pre-built research templates
├── outputs/               # Saved reports
├── requirements.txt
├── .env.example
└── README.md
```

---

## Templates Included

| Template | Purpose |
|----------|---------|
| Literature Review | Systematic evidence synthesis |
| Competitive / Landscape Analysis | Map players & opportunities |
| Experiment Design | Rigorous methodology & metrics |
| Technical Deep Dive | Architecture / algorithm analysis |
| Research Briefing / Memo | Executive-style decision support |
| Gap Analysis & Research Agenda | Open questions + project ideas |
| Custom Research | Free-form |

---

## Tips

- Use a **stronger model for the Manager** (Research Director).
- Enable **Serper** for current web knowledge.
- Enable **arXiv** for scientific topics.
- Start with focused questions — the lab performs best on well-scoped goals.
- Reports are automatically saved under `outputs/`.

---

Built as a practical, controllable research agency you can run and extend yourself.
