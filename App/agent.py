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
    """
    Get all pending user tasks.
    """

    tasks = get_all_tasks()

    if not tasks:
        return "No pending tasks."

    result = []

    for task in tasks:
        result.append(
            f"""
Task: {task['title']}
Description: {task['description']}
Priority: {task['priority']}
Deadline: {task['deadline']}
Duration: {task['duration']} minutes
Status: {task['status']}
"""
        )

    return "\n".join(result)


@tool
def get_preferences() -> str:
    """
    Get the user's scheduling preferences.
    """

    preferences = get_user_preferences()

    if not preferences:
        return "No scheduling preferences found."

    return f"""
Wake time: {preferences['wake_time']}
Sleep time: {preferences['sleep_time']}
Preferred work start: {preferences['preferred_work_start']}
Preferred work end: {preferences['preferred_work_end']}
Preferred deep work time: {preferences['preferred_deep_work_time']}
Break duration: {preferences['break_duration']} minutes
Exercise preference: {preferences['exercise_preference']}
"""


@tool
def get_calendar(date: str) -> str:
    """
    Get calendar events for a specific date.

    Date must be YYYY-MM-DD.
    """

    events = get_calendar_events(date)

    if not events:
        return f"No calendar events found for {date}."

    result = []

    for event in events:
        result.append(
            f"""
Event: {event['title']}
Date: {event['date']}
Start: {event['start_time']}
End: {event['end_time']}
Description: {event['description']}
"""
        )

    return "\n".join(result)


tools = [
    get_current_time,
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

            tool_messages.append(
                message.content
            )

    planning_context = "\n\n".join(
        tool_messages
    )

    return {
        "planning_context": planning_context
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

    result = validate_schedule(
        schedule
    )

    if not result["valid"]:

        print("\n❌ Schedule validation failed:")
        print(result["error"])

        return {
            "messages": [
                HumanMessage(
                    content=f"""
The generated schedule is invalid.

Validation error:
{result['error']}

Create a corrected schedule.
"""
                )
            ]
        }

    print("\n✅ Schedule validation successful.")

    return {}


# --------------------------------------------------
# ROUTING
# --------------------------------------------------

def route_after_agent(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):

        return "tools"

    return "planning_context"


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

graph.add_edge(
    "validator",
    END
)


agent = graph.compile()


# --------------------------------------------------
# RUN AGENT
# --------------------------------------------------

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
        }
    )

    print("\n" + "=" * 50)
    print("FINAL SCHEDULE")
    print("=" * 50)

    print(
        result["schedule"]
    )