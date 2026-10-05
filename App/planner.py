import json

from langchain_ollama import ChatOllama
from App.models import DailySchedule


llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


def generate_schedule(planning_context: str) -> DailySchedule:

    prompt = f"""
You are a daily schedule planner.

Using the information below, create a realistic schedule.

PLANNING CONTEXT:
{planning_context}

IMPORTANT RULES:

- Do not invent tasks.
- Do not modify existing calendar events.
- Do not create overlapping events.
- Respect wake and sleep times.
- Respect preferred working hours.
- Prioritize high-priority tasks.
- Consider deadlines.
- Respect task durations.
- Include reasonable breaks.
- Include meals and exercise when appropriate.
- Keep the schedule realistic.
- Return events in chronological order.

Return ONLY valid JSON.

The JSON must have exactly this structure:

{{
    "date": "YYYY-MM-DD",
    "events": [
        {{
            "start_time": "HH:MM",
            "end_time": "HH:MM",
            "activity": "Activity name",
            "event_type": "work",
            "priority": "high",
            "reason": "Why this was scheduled here"
        }}
    ],
    "planning_summary": "Short explanation of the planning decisions"
}}
"""

    response = llm.invoke(prompt)

    content = response.content

    # Remove markdown code fences if the model adds them
    content = content.replace("```json", "").replace("```", "").strip()

    data = json.loads(content)

    schedule = DailySchedule.model_validate(data)

    return schedule