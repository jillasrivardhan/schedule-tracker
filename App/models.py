from pydantic import BaseModel, Field
from typing import List


# ============================================================
# SCHEDULE EVENT
# ============================================================

class ScheduleEvent(BaseModel):

    start_time: str = Field(
        description="Start time in HH:MM format"
    )

    end_time: str = Field(
        description="End time in HH:MM format"
    )

    activity: str = Field(
        description="Name of the activity"
    )

    event_type: str = Field(
        description="Type of activity such as work, study, break, meal, exercise or routine"
    )

    priority: str = Field(
        description="Priority: high, medium, low, or none"
    )

    reason: str = Field(
        description="Why this activity was scheduled at this time"
    )


# ============================================================
# DAILY SCHEDULE
# ============================================================

class DailySchedule(BaseModel):

    date: str = Field(
        description="Schedule date in YYYY-MM-DD format"
    )

    events: List[ScheduleEvent] = Field(
        description="All events in chronological order"
    )

    planning_summary: str = Field(
        description="Short explanation of how the day was planned"
    )