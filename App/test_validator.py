from App.validator import validate_schedule


schedule = {
    "events": [
        {
            "start_time": "09:00",
            "end_time": "12:00",
            "activity": "College",
            "event_type": "routine",
            "priority": "none",
            "reason": "Existing commitment"
        },
        {
            "start_time": "10:00",
            "end_time": "11:30",
            "activity": "RAG Project",
            "event_type": "deep_work",
            "priority": "high",
            "reason": "Important deadline"
        }
    ]
}


preferences = {
    "wake_time": "06:00",
    "sleep_time": "22:30",
    "preferred_work_start": "08:00",
    "preferred_work_end": "20:00"
}


calendar_events = [
    {
        "title": "College",
        "start_time": "09:00",
        "end_time": "12:00"
    }
]


result = validate_schedule(
    schedule,
    preferences,
    calendar_events
)


print("\nValidation Result:")
print(result)