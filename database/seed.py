from database import create_tables, add_task


create_tables()


add_task(
    title="Finish RAG project",
    description="Complete the retrieval and generation pipeline.",
    priority="high",
    deadline="2026-10-07",
    duration=120
)


add_task(
    title="Learn LangGraph",
    description="Study LangGraph state, nodes, edges and tool calling.",
    priority="medium",
    deadline="2026-10-10",
    duration=90
)


add_task(
    title="Exercise",
    description="Daily workout.",
    priority="medium",
    deadline=None,
    duration=60
)


add_task(
    title="Read AI research paper",
    description="Read and take notes from one AI paper.",
    priority="low",
    deadline="2026-10-12",
    duration=45
)


print("Sample tasks added successfully.")