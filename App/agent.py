from typing import TypedDict
from datetime import datetime
from zoneinfo import ZoneInfo

from langchain_ollama import ChatOllama
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END


# ============================================================
# 1. AGENT STATE
# ============================================================

class AgentState(TypedDict):
    messages: list


# ============================================================
# 2. TOOL
# ============================================================

@tool
def get_current_time() -> str:
    """
    Get the current date and time in India.

    Use this tool whenever the user asks about the current
    date or time, or when the current date/time is required
    for planning.
    """

    india_time = datetime.now(ZoneInfo("Asia/Kolkata"))

    return india_time.strftime(
        "%A, %d %B %Y, %I:%M:%S %p"
    )


# ============================================================
# 3. LLM
# ============================================================

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


# Give the model access to the tool
llm_with_tools = llm.bind_tools(
    [get_current_time]
)


# ============================================================
# 4. AGENT NODE
# ============================================================

def agent_node(state: AgentState):

    messages = state["messages"]

    response = llm_with_tools.invoke(messages)

    return {
        "messages": messages + [response]
    }


# ============================================================
# 5. TOOL NODE
# ============================================================

def tool_node(state: AgentState):

    messages = state["messages"]

    last_message = messages[-1]

    tool_calls = last_message.tool_calls

    tool_results = []

    for tool_call in tool_calls:

        if tool_call["name"] == "get_current_time":

            result = get_current_time.invoke(
                tool_call["args"]
            )

            tool_results.append(
                {
                    "role": "tool",
                    "content": result,
                    "tool_call_id": tool_call["id"]
                }
            )

    return {
        "messages": messages + tool_results
    }


# ============================================================
# 6. DECISION FUNCTION
# ============================================================

def should_continue(state: AgentState):

    last_message = state["messages"][-1]

    if getattr(last_message, "tool_calls", None):

        return "tool"

    return END


# ============================================================
# 7. BUILD GRAPH
# ============================================================

graph_builder = StateGraph(AgentState)

graph_builder.add_node(
    "agent",
    agent_node
)

graph_builder.add_node(
    "tool",
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
        "tool": "tool",
        END: END
    }
)

graph_builder.add_edge(
    "tool",
    "agent"
)


agent = graph_builder.compile()


# ============================================================
# 8. RUN AGENT
# ============================================================

if __name__ == "__main__":

    print("\n===================================")
    print("       AI TOOL-CALLING AGENT")
    print("===================================\n")

    user_input = input("You: ")

    result = agent.invoke(
        {
            "messages": [
                {
                    "role": "user",
                    "content": user_input
                }
            ]
        }
    )

    print("\nAgent:")

    final_message = result["messages"][-1]

    print(final_message.content)