from datetime import datetime


# ============================================================
# TIME HELPERS
# ============================================================

def time_to_minutes(time_string: str) -> int:
    """
    Convert HH:MM into minutes since midnight.
    """

    hour, minute = map(
        int,
        time_string.split(":")
    )

    return hour * 60 + minute


# ============================================================
# CHECK TIME RANGE
# ============================================================

def validate_time_range(event):

    start = time_to_minutes(
        event["start_time"]
    )

    end = time_to_minutes(
        event["end_time"]
    )

    if start >= end:

        return (
            False,
            f"Invalid time range for "
            f"'{event['activity']}': "
            f"start time must be before end time."
        )

    return True, None


# ============================================================
# CHECK OVERLAPPING EVENTS
# ============================================================

def validate_overlaps(events):

    sorted_events = sorted(
        events,
        key=lambda event:
        time_to_minutes(event["start_time"])
    )

    for i in range(len(sorted_events) - 1):

        current = sorted_events[i]
        next_event = sorted_events[i + 1]

        current_end = time_to_minutes(
            current["end_time"]
        )

        next_start = time_to_minutes(
            next_event["start_time"]
        )

        if current_end > next_start:

            return (
                False,
                (
                    f"Schedule conflict detected: "
                    f"'{current['activity']}' "
                    f"({current['start_time']}-"
                    f"{current['end_time']}) overlaps with "
                    f"'{next_event['activity']}' "
                    f"({next_event['start_time']}-"
                    f"{next_event['end_time']})."
                )
            )

    return True, None


# ============================================================
# CHECK CALENDAR CONFLICTS
# ============================================================

def validate_calendar_conflicts(
    schedule_events,
    calendar_events
):

    for schedule_event in schedule_events:

        schedule_start = time_to_minutes(
            schedule_event["start_time"]
        )

        schedule_end = time_to_minutes(
            schedule_event["end_time"]
        )

        for calendar_event in calendar_events:

            calendar_start = time_to_minutes(
                calendar_event["start_time"]
            )

            calendar_end = time_to_minutes(
                calendar_event["end_time"]
            )

            if (
                schedule_start < calendar_end
                and schedule_end > calendar_start
            ):

                return (
                    False,
                    (
                        f"'{schedule_event['activity']}' "
                        f"conflicts with existing calendar "
                        f"event '{calendar_event['title']}' "
                        f"({calendar_event['start_time']}-"
                        f"{calendar_event['end_time']})."
                    )
                )

    return True, None


# ============================================================
# CHECK WAKE/SLEEP BOUNDARIES
# ============================================================

def validate_sleep_boundaries(
    events,
    wake_time,
    sleep_time
):

    wake = time_to_minutes(wake_time)
    sleep = time_to_minutes(sleep_time)

    for event in events:

        start = time_to_minutes(
            event["start_time"]
        )

        end = time_to_minutes(
            event["end_time"]
        )

        if start < wake:

            return (
                False,
                (
                    f"'{event['activity']}' starts at "
                    f"{event['start_time']}, before the "
                    f"user's wake time of {wake_time}."
                )
            )

        if end > sleep:

            return (
                False,
                (
                    f"'{event['activity']}' ends at "
                    f"{event['end_time']}, after the "
                    f"user's sleep time of {sleep_time}."
                )
            )

    return True, None


# ============================================================
# CHECK WORKING HOURS
# ============================================================

def validate_working_hours(
    events,
    work_start,
    work_end
):

    work_start_minutes = time_to_minutes(
        work_start
    )

    work_end_minutes = time_to_minutes(
        work_end
    )

    work_types = {
        "work",
        "study",
        "deep_work"
    }

    for event in events:

        if event["event_type"] not in work_types:
            continue

        start = time_to_minutes(
            event["start_time"]
        )

        end = time_to_minutes(
            event["end_time"]
        )

        if start < work_start_minutes:

            return (
                False,
                (
                    f"'{event['activity']}' starts "
                    f"before preferred working hours."
                )
            )

        if end > work_end_minutes:

            return (
                False,
                (
                    f"'{event['activity']}' ends "
                    f"after preferred working hours."
                )
            )

    return True, None


# ============================================================
# MAIN VALIDATOR
# ============================================================

def validate_schedule(
    schedule,
    preferences,
    calendar_events
):

    events = schedule["events"]

    # --------------------------------------------
    # 1. Validate individual time ranges
    # --------------------------------------------

    for event in events:

        valid, error = validate_time_range(
            event
        )

        if not valid:
            return {
                "valid": False,
                "error": error
            }

    # --------------------------------------------
    # 2. Check overlaps
    # --------------------------------------------

    valid, error = validate_overlaps(
        events
    )

    if not valid:

        return {
            "valid": False,
            "error": error
        }

    # --------------------------------------------
    # 3. Check calendar conflicts
    # --------------------------------------------

    valid, error = validate_calendar_conflicts(
        events,
        calendar_events
    )

    if not valid:

        return {
            "valid": False,
            "error": error
        }

    # --------------------------------------------
    # 4. Check sleep boundaries
    # --------------------------------------------

    valid, error = validate_sleep_boundaries(
        events,
        preferences["wake_time"],
        preferences["sleep_time"]
    )

    if not valid:

        return {
            "valid": False,
            "error": error
        }

    # --------------------------------------------
    # 5. Check working hours
    # --------------------------------------------

    valid, error = validate_working_hours(
        events,
        preferences["preferred_work_start"],
        preferences["preferred_work_end"]
    )

    if not valid:

        return {
            "valid": False,
            "error": error
        }

    # --------------------------------------------
    # Everything passed
    # --------------------------------------------

    return {
        "valid": True,
        "error": None
    }