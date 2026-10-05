from App.planner import generate_schedule


planning_context = """
DATE: 2026-10-06

TASKS:
1. Finish RAG project
   Priority: high
   Duration: 120 minutes
   Deadline: 2026-10-07

2. Learn LangGraph
   Priority: medium
   Duration: 90 minutes
   Deadline: 2026-10-10

3. Exercise
   Priority: medium
   Duration: 60 minutes

PREFERENCES:
Wake time: 06:00
Sleep time: 22:30
Working hours: 08:00 - 20:00
Preferred deep work: morning
Break duration: 15 minutes
Exercise preference: evening

CALENDAR:
09:00 - 12:00 College
13:00 - 14:00 Lunch
16:00 - 17:00 Project Meeting
"""


schedule = generate_schedule(planning_context)

print("\nGenerated Schedule:\n")

print(schedule.model_dump_json(indent=2))