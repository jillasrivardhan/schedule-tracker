import streamlit as st
from langchain_core.messages import HumanMessage

from App.agent import agent


# ============================================================
# PAGE CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Daily Schedule Planner",
    page_icon="📅",
    layout="wide"
)


# ============================================================
# HEADER
# ============================================================

st.title("📅 AI Daily Schedule Planner")

st.write(
    "Let your AI agent plan your day around your tasks, "
    "preferences, and existing calendar events."
)


# ============================================================
# USER INPUT
# ============================================================

user_request = st.text_area(
    "What would you like me to plan?",
    placeholder=(
        "Example: Create my schedule for tomorrow and "
        "prioritize my high priority tasks."
    ),
    height=120
)


# ============================================================
# GENERATE BUTTON
# ============================================================

if st.button(
    "✨ Generate Schedule",
    type="primary"
):

    if not user_request.strip():

        st.warning(
            "Please enter what you want to plan."
        )

    else:

        with st.spinner(
            "🤖 AI is planning your day..."
        ):

            result = agent.invoke(
                {
                    "messages": [
            HumanMessage(
                content=user_request
            )
        ],
                    "planning_context": "",
                    "schedule": {},
                    "preferences": {},
                    "calendar_events": [],
                    "validation_error": "",
                    "retry_count": 0
                }
            )

        schedule = result["schedule"]

        # ----------------------------------------------------
        # DISPLAY DATE
        # ----------------------------------------------------

        st.subheader(
            f"📅 {schedule['date']}"
        )

        # ----------------------------------------------------
        # DISPLAY EVENTS
        # ----------------------------------------------------

        for event in schedule["events"]:

            with st.container():

                col1, col2, col3 = st.columns(
                    [1.5, 4, 1.5]
                )

                with col1:
                    st.write(
                        f"**{event['start_time']}**"
                    )

                    st.write(
                        f"**{event['end_time']}**"
                    )

                with col2:
                    st.write(
                        f"### {event['activity']}"
                    )

                    st.write(
                        event["reason"]
                    )

                with col3:
                    st.write(
                        f"**{event['event_type']}**"
                    )

                    st.write(
                        f"Priority: {event['priority']}"
                    )

                st.divider()

        # ----------------------------------------------------
        # PLANNING SUMMARY
        # ----------------------------------------------------

        st.subheader(
            "🧠 Planning Summary"
        )

        st.info(
            schedule["planning_summary"]
        )