"""
Research Agency Lab — Core multi-agent system
Hierarchical Research Director + specialist team + rich tools + memory support
"""

from __future__ import annotations

import os
from typing import List, Optional

from dotenv import load_dotenv
from crewai import Agent, Task, Crew, Process
from crewai.llm import LLM

load_dotenv()

# ---------------------------------------------------------------------------
# Tools factory
# ---------------------------------------------------------------------------

def build_tools(
    enable_web_search: bool = True,
    enable_arxiv: bool = True,
    enable_code: bool = True,
    enable_files: bool = True,
    enable_scrape: bool = True,
) -> list:
    """Build the toolset based on availability and user toggles."""
    tools = []

    try:
        from crewai_tools import (
            SerperDevTool,
            ScrapeWebsiteTool,
            WebsiteSearchTool,
            FileReadTool,
            DirectoryReadTool,
            ArxivPaperTool,
            CodeInterpreterTool,
            PDFSearchTool,
        )
    except ImportError as e:
        print(f"⚠️  Some crewai-tools unavailable: {e}")
        return tools

    # Web search (Serper – best quality when key present)
    if enable_web_search and os.getenv("SERPER_API_KEY"):
        try:
            tools.append(SerperDevTool())
        except Exception as e:
            print(f"Serper tool failed: {e}")

    # Academic papers
    if enable_arxiv:
        try:
            tools.append(ArxivPaperTool(download_pdfs=False, max_results=8))
        except Exception:
            pass

    # Code execution (sandboxed by CrewAI)
    if enable_code:
        try:
            tools.append(CodeInterpreterTool())
        except Exception:
            pass

    # File / directory tools
    if enable_files:
        try:
            tools.extend([FileReadTool(), DirectoryReadTool()])
        except Exception:
            pass

    # Scraping & site search
    if enable_scrape:
        try:
            tools.extend([ScrapeWebsiteTool(), WebsiteSearchTool()])
        except Exception:
            pass

    return tools


# ---------------------------------------------------------------------------
# LLM helpers
# ---------------------------------------------------------------------------

def make_llm(model: str, temperature: float = 0.4) -> LLM:
    return LLM(model=model, temperature=temperature)


# ---------------------------------------------------------------------------
# Agents factory
# ---------------------------------------------------------------------------

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
            "deliver rigorous, high-quality final reports."
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


# ---------------------------------------------------------------------------
# Main research runner
# ---------------------------------------------------------------------------

def run_research(
    user_request: str,
    model: str = "gpt-4o-mini",
    manager_model: Optional[str] = None,
    temperature: float = 0.4,
    enable_web_search: bool = True,
    enable_arxiv: bool = True,
    enable_code: bool = True,
    enable_memory: bool = False,
    verbose: bool = True,
) -> str:
    """
    Launch the full hierarchical Research Agency Lab on a user request.
    Returns the final report as a string.
    """

    tools = build_tools(
        enable_web_search=enable_web_search,
        enable_arxiv=enable_arxiv,
        enable_code=enable_code,
    )

    agents = create_agents(
        model=model,
        manager_model=manager_model,
        temperature=temperature,
        tools=tools,
    )

    main_task = Task(
        description=f"""You are leading a research investigation for the Research Agency Lab.

USER REQUEST:
\"\"\"{user_request}\"\"\"

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
        memory=enable_memory,
    )

    result = lab.kickoff()
    return str(result)
