"""
Research Agency Lab — Core multi-agent system
Hierarchical Research Director + specialist team + tools + persistent memory
"""

from __future__ import annotations

import os
from typing import Optional, List
from datetime import datetime

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

from lab.tools import build_tools
from lab.memory import get_lab_memory, LabMemory

load_dotenv()


def make_llm(model: str, temperature: float = 0.4) -> LLM:
    return LLM(model=model, temperature=temperature)


def create_agents(
    model: str = "gpt-4o-mini",
    manager_model: Optional[str] = None,
    temperature: float = 0.4,
    tools: Optional[list] = None,
) -> dict:
    tools = tools or []
    manager_model = manager_model or model

    specialist_llm = make_llm(model, temperature)
    manager_llm = make_llm(manager_model, max(0.2, temperature - 0.1))

    research_director = Agent(
        role="Research Director",
        goal=(
            "Lead the research laboratory: decompose complex questions, "
            "delegate to the right specialists, synthesize findings, and "
            "deliver rigorous, high-quality final reports. Use lab memory when available."
        ),
        backstory=(
            "You are the Director of a high-performing research laboratory with a PhD "
            "and 15+ years leading interdisciplinary teams. You excel at problem "
            "decomposition, rigorous synthesis, and never accept superficial work."
        ),
        llm=manager_llm,
        verbose=True,
        allow_delegation=True,
        tools=tools,
    )

    literature_analyst = Agent(
        role="Literature & Evidence Analyst",
        goal="Find, evaluate, and synthesize the most relevant existing research, data, and expert knowledge.",
        backstory=(
            "Meticulous literature analyst specializing in systematic reviews and "
            "evidence synthesis. Expert at assessing source credibility and spotting gaps."
        ),
        llm=specialist_llm,
        verbose=True,
        allow_delegation=False,
        tools=tools,
    )

    data_scientist = Agent(
        role="Data & Insights Scientist",
        goal="Analyze quantitative and qualitative information, identify patterns, and extract actionable insights.",
        backstory=(
            "Sharp data scientist who combines statistical thinking with domain curiosity. "
            "Careful about correlation vs causation and turns raw information into clear insight."
        ),
        llm=specialist_llm,
        verbose=True,
        allow_delegation=False,
        tools=tools,
    )

    experiment_designer = Agent(
        role="Experiment & Methodology Designer",
        goal="Design rigorous research methodologies, experiments, evaluation frameworks, and validation approaches.",
        backstory=(
            "Expert in research design and scientific methodology. Creates clear protocols, "
            "defines success metrics, and anticipates confounds."
        ),
        llm=specialist_llm,
        verbose=True,
        allow_delegation=False,
        tools=tools,
    )

    report_writer = Agent(
        role="Lead Research Writer",
        goal="Produce clear, structured, publication-quality research reports and briefings.",
        backstory=(
            "Skilled research communicator who turns complex findings into precise, "
            "readable reports for both technical and executive audiences."
        ),
        llm=specialist_llm,
        verbose=True,
        allow_delegation=False,
        tools=tools,
    )

    return {
        "director": research_director,
        "literature": literature_analyst,
        "data": data_scientist,
        "experiment": experiment_designer,
        "writer": report_writer,
    }


def run_research(
    user_request: str,
    lab_id: str = "default",
    model: str = "gpt-4o-mini",
    manager_model: Optional[str] = None,
    temperature: float = 0.4,
    enable_web_search: bool = True,
    enable_arxiv: bool = True,
    enable_code: bool = True,
    enable_memory: bool = True,
    verbose: bool = True,
) -> str:
    """
    Launch the hierarchical Research Agency Lab.
    Results are optionally stored in the lab's persistent vector memory.
    """

    tools = build_tools(
        enable_web_search=enable_web_search,
        enable_arxiv=enable_arxiv,
        enable_code=enable_code,
    )

    # Inject relevant memory context if available
    memory_context = ""
    lab_memory: Optional[LabMemory] = None
    if enable_memory:
        lab_memory = get_lab_memory(lab_id)
        prior = lab_memory.query(user_request, n_results=4)
        if prior:
            snippets = "\n\n".join(
                f"- {p['text'][:400]}..." if len(p['text']) > 400 else f"- {p['text']}"
                for p in prior
            )
            memory_context = f"\n\nRELEVANT PRIOR LAB KNOWLEDGE:\n{snippets}\n"

    agents = create_agents(
        model=model,
        manager_model=manager_model,
        temperature=temperature,
        tools=tools,
    )

    main_task = Task(
        description=f"""You are leading a research investigation inside Research Lab \"{lab_id}\".

USER REQUEST:
\"\"\"{user_request}\"\"\"
{memory_context}
As Research Director you must:
1. Fully understand the research goal.
2. Break the work into clear sub-tasks.
3. Delegate to the most appropriate specialists:
   - Literature & Evidence Analyst
   - Data & Insights Scientist
   - Experiment & Methodology Designer
   - Lead Research Writer
4. Synthesize everything into a rigorous, well-structured final research report.
5. Ensure the deliverable is accurate, evidence-based, and actionable.

Final output requirements:
- Executive summary / key takeaways at the top
- Clear structure with headings
- Evidence and reasoning
- Limitations and uncertainties
- Concrete recommendations or next steps where appropriate
""",
        expected_output=(
            "A complete, high-quality research report that fully addresses the original request. "
            "Include executive summary, key findings, analysis, methodology notes if relevant, "
            "limitations, and recommendations."
        ),
        agent=agents["director"],
    )

    lab = Crew(
        agents=[
            agents["literature"],
            agents["data"],
            agents["experiment"],
            agents["writer"],
        ],
        tasks=[main_task],
        process=Process.hierarchical,
        manager_agent=agents["director"],
        verbose=verbose,
        memory=False,  # We handle persistence ourselves via Chroma
    )

    result = lab.kickoff()
    result_str = str(result)

    # Persist the new knowledge into the lab's vector store
    if lab_memory and enable_memory:
        lab_memory.add(
            texts=[f"Research Request: {user_request}\n\nReport:\n{result_str[:8000]}"],
            metadatas=[{
                "type": "research_report",
                "lab_id": lab_id,
                "timestamp": datetime.utcnow().isoformat(),
                "request": user_request[:200],
            }],
        )

    return result_str
