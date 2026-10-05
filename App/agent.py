from typing import Annotated, TypedDict
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langchain_core.messages import (
    BaseMessage,
    HumanMessage
)
from langgraph.graph import (
    StateGraph,
    START,
    END
)
from langgraph.graph.message import add_messages
from langgraph.prebuilt import ToolNode

from database.database import (
    get_all_tasks,
    get_user_preferences,
    get_calendar_events
)


# ============================================================
# 1. AGENT STATE
# ============================================================

class AgentState(TypedDict):
    messages: Annotated[list[BaseMessage], add_messages]


# ============================================================
# 2. CURRENT TIME TOOL
# ============================================================

@tool
def get_current_time() -> str:
    """
    Get the current date and time in India.

    Use this tool whenever the current date or time
    is required.
    """

    india_time = datetime.now(
        ZoneInfo("Asia/Kolkata")
    )

    return india_time.strftime(
        "%A, %d %B %Y, %I:%M:%S %p"
    )


# ============================================================
# 3. TASK TOOL
# ============================================================

@tool
def get_tasks() -> str:
    """
    Get all pending tasks from the user's task database.

    Use this tool whenever you need to know what tasks
    the user needs to complete.
    """

    tasks = get_all_tasks()

    if not tasks:
        return "The user has no pending tasks."

    result = "Pending tasks:\n\n"

    for task in tasks:

        result += (
            f"Task ID: {task['id']}\n"
            f"Title: {task['title']}\n"
            f"Description: {task['description']}\n"
            f"Priority: {task['priority']}\n"
            f"Deadline: {task['deadline']}\n"
            f"Duration: {task['duration_minutes']} minutes\n"
            f"Status: {task['status']}\n"
            f"---\n"
        )

    return result

@tool
def get_preferences() -> str:
    """
    Get the user's daily scheduling preferences.

    Use this tool whenever you need to know how the user
    prefers their day to be organized.
    """

    preferences = get_user_preferences()

    if preferences is None:
        return "The user has not configured any preferences yet."

    return (
        f"Wake-up time: {preferences['wake_time']}\n"
        f"Sleep time: {preferences['sleep_time']}\n"
        f"Preferred work start: {preferences['preferred_work_start']}\n"
        f"Preferred work end: {preferences['preferred_work_end']}\n"
        f"Preferred deep work time: {preferences['preferred_deep_work_time']}\n"
        f"Break duration: {preferences['break_duration_minutes']} minutes\n"
        f"Exercise preference: {preferences['exercise_preference']}"
    )

@tool
def get_calendar(date: str) -> str:
    """
    Get the user's calendar events for a specific date.

    The date must be provided in YYYY-MM-DD format.

    Use this tool whenever you need to know when the user
    is already busy on a particular day.
    """

    events = get_calendar_events(date)

    if not events:
        return f"No calendar events found for {date}."

    result = f"Calendar events for {date}:\n\n"

    for event in events:

        result += (
            f"Event: {event['title']}\n"
            f"Start: {event['start_time']}\n"
            f"End: {event['end_time']}\n"
            f"Description: {event['description']}\n"
            f"---\n"
        )

    return result

# ============================================================
# 4. LLM
# ============================================================

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


# ============================================================
# 5. REGISTER TOOLS
# ============================================================

tools = [
    get_current_time,
    get_tasks,
    get_preferences,
    get_calendar
]

llm_with_tools = llm.bind_tools(tools)


# ============================================================
# 6. AGENT NODE
# ============================================================

def agent_node(state: AgentState):

    response = llm_with_tools.invoke(
        state["messages"]
    )

    return {
        "messages": [response]
    }


# ============================================================
# 7. TOOL NODE
# ============================================================

tool_node = ToolNode(tools)


# ============================================================
# 8. DECISION FUNCTION
# ============================================================

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if last_message.tool_calls:
        return "tools"

    return END


# ============================================================
# 9. BUILD GRAPH
# ============================================================

graph_builder = StateGraph(AgentState)


graph_builder.add_node(
    "agent",
    agent_node
)


graph_builder.add_node(
    "tools",
    tool_node
)


graph_builder.add_edge(
    START,
    "agent"
)


graph_builder.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)


graph_builder.add_edge(
    "tools",
    "agent"
)


agent = graph_builder.compile()


# ============================================================
# 10. RUN AGENT
# ============================================================

if __name__ == "__main__":

    print("\n======================================")
    print("       DAILY SCHEDULE AGENT")
    print("======================================")

    print("\nAvailable tools:")
    print("- get_current_time")
    print("- get_tasks")
    print("- get_preferences")
    print("- get_calendar")

    print("\nType 'exit' to quit.\n")

    while True:

        user_input = input("You: ")

        if user_input.lower() == "exit":
            break

        result = agent.invoke(
            {
                "messages": [
                    HumanMessage(
                        content=user_input
                    )
                ]
            }
        )

        final_message = result["messages"][-1]

        print("\nAgent:")
        print(final_message.content)
        print()