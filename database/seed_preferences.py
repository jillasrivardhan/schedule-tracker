from database import create_tables, add_preferences


create_tables()


add_preferences(
    wake_time="06:00",
    sleep_time="22:30",
    preferred_work_start="08:00",
    preferred_work_end="20:00",
    preferred_deep_work_time="morning",
    break_duration=15,
    exercise_preference="evening"
)


print("User preferences added successfully.")