from langchain_ollama import ChatOllama


llm = ChatOllama(
    model="qwen2.5:3b",
    temperature=0
)


response = llm.invoke(
    "Explain in one sentence what an AI agent is."
)


print("\nModel response:")
print(response.content)