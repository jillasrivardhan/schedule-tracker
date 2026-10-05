
from typing import TypedDict

from langchain_ollama import ChatOllama
from langgraph.graph import StateGraph, START, END


# --------------------------------------------------
# 1. Define the Agent State
# --------------------------------------------------

class AgentState(TypedDict):
    user_input: str
    response: str


# --------------------------------------------------
# 2. Create the LLM
# --------------------------------------------------

llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


# --------------------------------------------------
# 3. Create the Agent Node
# --------------------------------------------------

def agent_node(state: AgentState):

    user_input = state["user_input"]

    response = llm.invoke(user_input)

    return {
        "response": response.content
    }


# --------------------------------------------------
# 4. Build the LangGraph
# --------------------------------------------------

graph_builder = StateGraph(AgentState)

graph_builder.add_node("agent", agent_node)

graph_builder.add_edge(START, "agent")
graph_builder.add_edge("agent", END)

agent = graph_builder.compile()


# --------------------------------------------------
# 5. Run the Agent
# --------------------------------------------------

if __name__ == "__main__":

    user_input = input("\nYou: ")

    result = agent.invoke({
        "user_input": user_input
    })

    print("\nAgent:")
    print(result["response"])