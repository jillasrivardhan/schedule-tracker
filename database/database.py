import sqlite3
from pathlib import Path


# ============================================================
# DATABASE LOCATION
# ============================================================

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "schedule.db"


# ============================================================
# DATABASE CONNECTION
# ============================================================

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


# ============================================================
# CREATE TABLES
# ============================================================

def create_tables():

    connection = get_connection()
    cursor = connection.cursor()

    # -----------------------------
    # Tasks table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            description TEXT,
            priority TEXT NOT NULL,
            deadline TEXT,
            duration INTEGER NOT NULL,
            status TEXT NOT NULL
        )
    """)

    # -----------------------------
    # Preferences table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS preferences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            wake_time TEXT NOT NULL,
            sleep_time TEXT NOT NULL,
            preferred_work_start TEXT NOT NULL,
            preferred_work_end TEXT NOT NULL,
            preferred_deep_work_time TEXT NOT NULL,
            break_duration INTEGER NOT NULL,
            exercise_preference TEXT NOT NULL
        )
    """)
        # -----------------------------
    # Calendar events table
    # -----------------------------

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calendar_events (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            date TEXT NOT NULL,
            start_time TEXT NOT NULL,
            end_time TEXT NOT NULL,
            description TEXT
        )
    """)


    connection.commit()
    connection.close()


# ============================================================
# ADD TASK
# ============================================================

def add_task(
    title,
    description,
    priority,
    deadline,
    duration,
    status="pending"
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO tasks
        (
            title,
            description,
            priority,
            deadline,
            duration,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        title,
        description,
        priority,
        deadline,
        duration,
        status
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET TASKS
# ============================================================

def get_all_tasks():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            description,
            priority,
            deadline,
            duration,
            status
        FROM tasks
        WHERE status = 'pending'
        ORDER BY
            CASE priority
                WHEN 'high' THEN 1
                WHEN 'medium' THEN 2
                WHEN 'low' THEN 3
                ELSE 4
            END,
            deadline
    """)

    rows = cursor.fetchall()

    connection.close()

    tasks = []

    for row in rows:

        tasks.append({
            "id": row[0],
            "title": row[1],
            "description": row[2],
            "priority": row[3],
            "deadline": row[4],
            "duration_minutes": row[5],
            "status": row[6]
        })

    return tasks


# ============================================================
# ADD PREFERENCES
# ============================================================

def add_preferences(
    wake_time,
    sleep_time,
    preferred_work_start,
    preferred_work_end,
    preferred_deep_work_time,
    break_duration,
    exercise_preference
):

    connection = get_connection()
    cursor = connection.cursor()

    # Only keep one preference profile for now
    cursor.execute("DELETE FROM preferences")

    cursor.execute("""
        INSERT INTO preferences
        (
            wake_time,
            sleep_time,
            preferred_work_start,
            preferred_work_end,
            preferred_deep_work_time,
            break_duration,
            exercise_preference
        )
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        wake_time,
        sleep_time,
        preferred_work_start,
        preferred_work_end,
        preferred_deep_work_time,
        break_duration,
        exercise_preference
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET PREFERENCES
# ============================================================

def get_user_preferences():

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            wake_time,
            sleep_time,
            preferred_work_start,
            preferred_work_end,
            preferred_deep_work_time,
            break_duration,
            exercise_preference
        FROM preferences
        LIMIT 1
    """)

    row = cursor.fetchone()

    connection.close()

    if row is None:
        return None

    return {
        "wake_time": row[0],
        "sleep_time": row[1],
        "preferred_work_start": row[2],
        "preferred_work_end": row[3],
        "preferred_deep_work_time": row[4],
        "break_duration_minutes": row[5],
        "exercise_preference": row[6]
    }

# ============================================================
# ADD CALENDAR EVENT
# ============================================================

def add_calendar_event(
    title,
    date,
    start_time,
    end_time,
    description=""
):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO calendar_events
        (
            title,
            date,
            start_time,
            end_time,
            description
        )
        VALUES (?, ?, ?, ?, ?)
    """, (
        title,
        date,
        start_time,
        end_time,
        description
    ))

    connection.commit()
    connection.close()


# ============================================================
# GET CALENDAR EVENTS
# ============================================================

def get_calendar_events(date):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT
            id,
            title,
            date,
            start_time,
            end_time,
            description
        FROM calendar_events
        WHERE date = ?
        ORDER BY start_time
    """, (date,))

    rows = cursor.fetchall()

    connection.close()

    events = []

    for row in rows:

        events.append({
            "id": row[0],
            "title": row[1],
            "date": row[2],
            "start_time": row[3],
            "end_time": row[4],
            "description": row[5]
        })

    return events

# ============================================================
# INITIALIZE DATABASE
# ============================================================

if __name__ == "__main__":

    create_tables()

    print("Database tables created successfully.")