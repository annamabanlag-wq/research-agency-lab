# 🔬 Research Agency Lab — Simulation Environment

**Multi-user hierarchical multi-agent research laboratory** with persistent vector memory, Docker support, and cloud-ready deployment.

A Research Director manages specialist agents inside **Labs** (simulation environments). Each Lab has its own long-term knowledge base powered by ChromaDB.

---

## Features

| Feature | Description |
|---------|-------------|
| **Hierarchical Agents** | Research Director + Literature, Data, Experiment, Writer specialists |
| **Labs (Sim Environment)** | Create multiple research labs; each has isolated persistent memory |
| **Persistent Vector Memory** | ChromaDB — knowledge accumulates across runs inside a Lab |
| **Multi-user Auth** | Simple login system (streamlit-authenticator) |
| **Rich Tools** | Serper, arXiv, Code Interpreter, file tools, scraping |
| **Templates** | Literature Review, Experiment Design, Competitive Analysis, etc. |
| **Docker** | One-command local or cloud deployment |
| **Cloud Ready** | Works on Render, Railway, Fly.io, any Docker host |

---

## Quick Start (Local)

```bash
git clone https://github.com/annamabanlag-wq/research-agency-lab.git
cd research-agency-lab

python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Add OPENAI_API_KEY and ideally SERPER_API_KEY

streamlit run app.py
```

Default logins (change in `config/users.yaml`):
- `admin` / `admin123`
- `researcher` / `research123`

---

## Docker

```bash
# Build & run
docker compose up --build

# Or
docker build -t research-agency-lab .
docker run -p 8501:8501 --env-file .env -v $(pwd)/data:/app/data research-agency-lab
```

App available at http://localhost:8501

---

## Cloud Deployment

### Render / Railway / Fly.io (recommended)

1. Push this repo to GitHub (already done).
2. Create a new Web Service and connect the repo.
3. Set environment variables (`OPENAI_API_KEY`, `SERPER_API_KEY`, etc.).
4. Use the included `Dockerfile`.
5. Add a persistent disk/volume for `/app/data` so Chroma memory survives restarts.

### Example Render settings
- Runtime: Docker
- Port: 8501
- Disk: mount at `/app/data`

---

## How the Simulation Works

1. **Log in**
2. **Create a Lab** (e.g. “Agent Memory 2026 Study”)
3. Select the Lab → it becomes your active simulation environment
4. Choose a research template or write a free-form brief
5. Launch the Research Director + specialist team
6. Results are saved and **embedded into the Lab’s vector memory**
7. Future runs in the same Lab automatically retrieve relevant prior knowledge

This creates a growing, persistent research environment instead of isolated one-shot queries.

---

## Project Structure

```
research-agency-lab/
├── app.py                  # Multi-user Streamlit control panel
├── agency.py               # CLI entry
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
├── config/users.yaml       # Auth users (change passwords!)
├── lab/
│   ├── core.py             # Hierarchical crew + memory integration
│   ├── tools.py            # Expanded tool factory
│   ├── memory.py           # ChromaDB persistent memory
│   └── templates.py
├── data/                   # Persistent (labs + chroma)
└── outputs/                # Generated reports
```

---

## Security Note

Before any public deployment:
- Change all passwords in `config/users.yaml`
- Change the cookie key
- Prefer stronger auth (Auth0, Supabase, etc.) for production multi-tenant use

---

Enjoy running your own research simulation facility.
