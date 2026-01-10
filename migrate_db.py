import sqlite3
import os

db_path = 'data/social_media_agent.db'
if os.path.exists(db_path):
    conn = sqlite3.connect(db_path)
    try:
        conn.execute('ALTER TABLE news_items ADD COLUMN category VARCHAR(50) DEFAULT "general"')
        conn.commit()
        print("Column 'category' added to news_items table.")
    except sqlite3.OperationalError as e:
        if "duplicate column name" in str(e).lower():
            print("Column already exists.")
        else:
            print(f"Error: {e}")
    finally:
        conn.close()
else:
    print("Database not found.")
