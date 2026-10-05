from database import (
    create_tables,
    add_calendar_event
)


create_tables()


add_calendar_event(
    title="College",
    date="2026-10-06",
    start_time="09:00",
    end_time="12:00",
    description="College classes"
)


add_calendar_event(
    title="Lunch",
    date="2026-10-06",
    start_time="13:00",
    end_time="14:00",
    description="Lunch break"
)


add_calendar_event(
    title="Project Meeting",
    date="2026-10-06",
    start_time="16:00",
    end_time="17:00",
    description="Project discussion"
)


print("Calendar events added successfully.")