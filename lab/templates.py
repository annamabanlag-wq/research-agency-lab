"""Pre-built research templates for the Research Agency Lab."""

TEMPLATES = {
    "Custom Research": {
        "description": "Free-form research question or project.",
        "prompt": "",
        "icon": "🔍",
    },
    "Literature Review": {
        "description": "Systematic review of existing research on a topic, key papers, gaps, and synthesis.",
        "prompt": (
            "Conduct a rigorous literature review on the following topic. "
            "Identify the most important papers and findings from the last 5–7 years, "
            "group them by theme, highlight consensus and disagreements, "
            "point out research gaps, and conclude with the current state of knowledge "
            "and promising future directions.\n\nTopic: "
        ),
        "icon": "📚",
    },
    "Competitive / Landscape Analysis": {
        "description": "Map the competitive or technology landscape for a domain or product category.",
        "prompt": (
            "Perform a comprehensive competitive and technology landscape analysis. "
            "Identify the main players, approaches, strengths/weaknesses, recent developments, "
            "market positioning, and open opportunities. Structure the report with clear sections "
            "and actionable recommendations.\n\nDomain / Product area: "
        ),
        "icon": "🗺️",
    },
    "Experiment Design": {
        "description": "Design a rigorous experiment or evaluation protocol.",
        "prompt": (
            "Design a rigorous, feasible experiment or evaluation framework for the following research question. "
            "Include: hypothesis or goals, variables, methodology, metrics/success criteria, "
            "controls, potential confounds, sample/data requirements, analysis plan, "
            "and ethical or practical considerations.\n\nResearch question: "
        ),
        "icon": "🧪",
    },
    "Technical Deep Dive": {
        "description": "In-depth technical analysis of a system, algorithm, or architecture.",
        "prompt": (
            "Produce a technical deep-dive report. Explain how it works, key components, "
            "trade-offs, implementation considerations, performance characteristics, "
            "limitations, and comparison to alternatives. Include diagrams descriptions "
            "where helpful and practical recommendations.\n\nSubject: "
        ),
        "icon": "⚙️",
    },
    "Research Briefing / Memo": {
        "description": "Concise executive-style research briefing for decision makers.",
        "prompt": (
            "Prepare a concise, high-signal research briefing (memo style) for a decision-maker. "
            "Lead with key takeaways, then supporting evidence, risks/uncertainties, "
            "and clear recommended next steps. Keep it focused and actionable.\n\nTopic: "
        ),
        "icon": "📋",
    },
    "Gap Analysis & Research Agenda": {
        "description": "Identify knowledge gaps and propose a research agenda.",
        "prompt": (
            "Analyze the current state of knowledge, identify the most important open questions "
            "and gaps, and propose a prioritized research agenda with specific project ideas, "
            "methods, and expected impact.\n\nField / Problem area: "
        ),
        "icon": "🎯",
    },
}


def get_template_names():
    return list(TEMPLATES.keys())


def get_template(name: str) -> dict:
    return TEMPLATES.get(name, TEMPLATES["Custom Research"])
