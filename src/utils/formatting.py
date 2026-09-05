"""
src/utils/formatting.py
-----------------------
Pure-Python helpers for converting the stored JSON workout plan
into human-readable Markdown and plain text.  No Streamlit dependency.
"""
from __future__ import annotations

import json


def format_plan_as_markdown(plan: str) -> str:
    """
    Convert a JSON workout plan string into a well-formatted Markdown document.
    Falls back to returning the raw string if the plan is not valid JSON.
    """
    try:
        data = json.loads(plan)
    except json.JSONDecodeError:
        return plan

    md = f"# {data.get('program_name', 'Workout Plan')}\n\n"
    md += f"*{data.get('split_rationale', '')}*\n\n---\n\n"

    for day in data.get("days", []):
        md += f"## Day {day.get('day_number', '')}: {day.get('title', '')}\n\n"

        if day.get("warmup"):
            md += "**Warm-up:**\n"
            for item in day["warmup"]:
                md += f"- {item}\n"
            md += "\n"

        if day.get("exercises"):
            md += "**Exercises:**\n\n"
            for ex in day["exercises"]:
                md += f"### {ex.get('number', '')}. {ex.get('name', '')}\n"
                md += f"- **Sets:** {ex.get('sets', '')}\n"
                md += f"- **Reps:** {ex.get('reps', '')}\n"
                md += f"- **Rest:** {ex.get('rest', '')}\n"
                md += f"- **Cue:** *{ex.get('form_cue', '')}*\n\n"

        if day.get("cooldown"):
            md += "**Cool-down:**\n"
            for item in day["cooldown"]:
                md += f"- {item}\n"
            md += "\n"

        md += "---\n\n"

    if data.get("progression_guidelines"):
        md += "### Progression Guidelines\n"
        md += f"{data['progression_guidelines']}\n\n"

    if data.get("recovery_tips"):
        md += "### Recovery Tips\n"
        md += f"{data['recovery_tips']}\n\n"

    if data.get("disclaimer"):
        md += "### Disclaimer\n"
        md += f"{data['disclaimer']}\n\n"

    return md


def format_plan_as_text(plan: str) -> str:
    """
    Convert a JSON workout plan string into plain text by stripping Markdown syntax.
    """
    md = format_plan_as_markdown(plan)
    txt = (
        md
        .replace("# ", "")
        .replace("## ", "")
        .replace("### ", "")
        .replace("**", "")
        .replace("*", "")
    )
    return txt
