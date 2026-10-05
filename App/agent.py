from typing import TypedDict, Annotated

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import (
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from datetime import datetime
from zoneinfo import ZoneInfo

from database.database import (
    get_all_tasks,
    get_user_preferences,
    get_calendar_events,
)

from App.prompts import SCHEDULE_PLANNER_PROMPT
from App.planner import generate_schedule
from App.validator import validate_schedule


# --------------------------------------------------
# STATE
# --------------------------------------------------

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]
    planning_context: str
    schedule: dict
    preferences: dict
    calendar_events: list
    validation_error: str
    retry_count: int


# --------------------------------------------------
# LLM
# --------------------------------------------------

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


# --------------------------------------------------
# TOOLS
# --------------------------------------------------

@tool
def get_current_time() -> str:
    """
    Get the current date and time in India.

    Use this tool whenever the current date or time
    is required for planning.
    """

    india_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return india_time.strftime(
        "%A, %d %B %Y, %I:%M:%S %p"
    )


@tool
def get_tasks() -> str:
    """Get all pending tasks."""

    tasks = get_all_tasks()

    if not tasks:
        return "No pending tasks."

    return "\n".join(
        f"{task['title']} | "
        f"priority={task['priority']} | "
        f"duration={task['duration']}m | "
        f"deadline={task['deadline']}"
        for task in tasks
    )


@tool
def get_preferences() -> str:
    """Get the user's scheduling preferences."""

    preferences = get_user_preferences()

    if not preferences:
        return "No preferences found."

    return (
        f"wake={preferences['wake_time']} | "
        f"sleep={preferences['sleep_time']} | "
        f"work={preferences['preferred_work_start']}-"
        f"{preferences['preferred_work_end']} | "
        f"deep_work={preferences['preferred_deep_work_time']} | "
        f"break={preferences['break_duration']}m | "
        f"exercise={preferences['exercise_preference']}"
    )



@tool
def get_calendar(date: str) -> str:
    """Get calendar events for a specific date."""

    events = get_calendar_events(date)

    if not events:
        return f"No events on {date}."

    return "\n".join(
        f"{event['start_time']}-{event['end_time']} | "
        f"{event['title']}"
        for event in events
    )


tools = [
    get_tasks,
    get_preferences,
    get_calendar,
]


llm_with_tools = llm.bind_tools(tools)


# --------------------------------------------------
# AGENT NODE
# --------------------------------------------------

def agent_node(state: AgentState):

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# --------------------------------------------------
# TOOL NODE
# --------------------------------------------------

tool_node = ToolNode(tools)


# --------------------------------------------------
# BUILD PLANNING CONTEXT
# --------------------------------------------------

def build_planning_context(state: AgentState):

    tool_messages = []

    for message in state["messages"]:

        if message.type == "tool":
            tool_messages.append(message.content)

    planning_context = "\n\n".join(tool_messages)

    # Get the actual preferences directly from database
    preferences = get_user_preferences()

    # Get calendar events for tomorrow
    tomorrow = (
        datetime.now(ZoneInfo("Asia/Kolkata"))
        .date()
    )

    calendar_events = get_calendar_events(
        tomorrow.isoformat()
    )

    return {
        "planning_context": planning_context,
        "preferences": preferences or {},
        "calendar_events": calendar_events
    }


# --------------------------------------------------
# PLANNING NODE
# --------------------------------------------------

def planning_node(state: AgentState):

    schedule = generate_schedule(
        state["planning_context"]
    )

    return {
        "schedule": schedule.model_dump()
    }


# --------------------------------------------------
# VALIDATION NODE
# --------------------------------------------------

def validation_node(state: AgentState):

    schedule = state["schedule"]

    preferences = state["preferences"]

    calendar_events = state["calendar_events"]

    result = validate_schedule(
        schedule,
        preferences,
        calendar_events
    )

    if not result["valid"]:

        print("\n❌ Schedule validation failed:")
        print(result["error"])

        return {
            "validation_error": result["error"],
            "retry_count": state["retry_count"] + 1
        }

    print("\n✅ Schedule validation successful.")

    return {
        "validation_error": "",
    }

#--------------------------------------------------
# replanning node
#--------------------------------------------------

def replanning_node(state: AgentState):

    print("\n🔄 Re-planning schedule...")

    retry_prompt = f"""
The previous schedule was invalid.

Validation error:
{state["validation_error"]}

Create a corrected schedule.

Original planning context:
{state["planning_context"]}

Do not repeat the validation error.
Return ONLY valid JSON in the required DailySchedule format.
"""

    schedule = generate_schedule(
        retry_prompt
    )

    return {
        "schedule": schedule.model_dump()
    }

# --------------------------------------------------
# ROUTING
# --------------------------------------------------

def route_after_agent(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):
        return "tools"

    return "planning_context"


def route_after_validation(state: AgentState):

    if state["validation_error"]:

        if state["retry_count"] < 3:
            return "replan"

        print("\n⚠️ Maximum replanning attempts reached.")

    return "end"

# --------------------------------------------------
# GRAPH
# --------------------------------------------------

graph = StateGraph(AgentState)


graph.add_node(
    "agent",
    agent_node
)

graph.add_node(
    "tools",
    tool_node
)

graph.add_node(
    "planning_context",
    build_planning_context
)

graph.add_node(
    "planner",
    planning_node
)

graph.add_node(
    "validator",
    validation_node
)

graph.add_node(
    "replanner",
    replanning_node
)

graph.add_edge(
    START,
    "agent"
)

graph.add_conditional_edges(
    "agent",
    route_after_agent,
    {
        "tools": "tools",
        "planning_context": "planning_context",
    }
)

graph.add_edge(
    "tools",
    "agent"
)

graph.add_edge(
    "planning_context",
    "planner"
)

graph.add_edge(
    "planner",
    "validator"
)

graph.add_conditional_edges(
    "validator",
    route_after_validation,
    {
        "replan": "replanner",
        "end": END
    }
)

graph.add_edge(
    "replanner",
    "validator"
)


agent = graph.compile()


# ============================================================
# RUN AGENT FROM TERMINAL
# ============================================================

if __name__ == "__main__":

    user_input = input(
        "\nWhat would you like me to plan? "
    )

    messages = [
        SystemMessage(
            content=SCHEDULE_PLANNER_PROMPT
        ),
        HumanMessage(
            content=user_input
        ),
    ]

    result = agent.invoke(
        {
            "messages": messages,
            "planning_context": "",
            "schedule": {},
            "preferences": {},
            "calendar_events": [],
            "validation_error": "",
            "retry_count": 0
        }
    )

    print("\n" + "=" * 50)
    print("FINAL SCHEDULE")
    print("=" * 50)

    schedule = result["schedule"]

    print("\nDate:", schedule["date"])

    print("\nEvents:")

    for event in schedule["events"]:

        print(
            f"{event['start_time']} - "
            f"{event['end_time']} | "
            f"{event['activity']} | "
            f"{event['event_type']} | "
            f"{event['priority']}"
        )

    print("\nPlanning Summary:")

    print(
        schedule["planning_summary"]
    )