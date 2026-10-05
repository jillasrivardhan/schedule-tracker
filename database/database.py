import sqlite3
from pathlib import Path


# --------------------------------------------------
# Database location
# --------------------------------------------------

BASE_DIR = Path(__file__).resolve().parent
DATABASE_PATH = BASE_DIR / "schedule.db"


# --------------------------------------------------
# Get database connection
# --------------------------------------------------

def get_connection():
    return sqlite3.connect(DATABASE_PATH)


# --------------------------------------------------
# Create tables
# --------------------------------------------------

def create_tables():

    connection = get_connection()

    cursor = connection.cursor()

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

    connection.commit()
    connection.close()


# --------------------------------------------------
# Add task
# --------------------------------------------------

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


# --------------------------------------------------
# Get tasks
# --------------------------------------------------

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


# --------------------------------------------------
# Initialize database
# --------------------------------------------------

if __name__ == "__main__":

    create_tables()

    print("Database created successfully.")