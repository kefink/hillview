import sqlite3

def init_db():
    conn = sqlite3.connect("kirima_primary.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS marks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            grade TEXT,
            stream TEXT,
            student_name TEXT,
            subject TEXT,
            mark INTEGER
        )
    """)
    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_db()