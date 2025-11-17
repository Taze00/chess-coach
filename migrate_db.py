"""
Database migration script to add new columns to errors table
"""
import sqlite3
import os

def migrate_database():
    """Add new columns to errors table"""
    db_path = 'instance/chess_coach.db'

    if not os.path.exists(db_path):
        print("Database not found. Will be created on next run.")
        return

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Check if columns already exist
    cursor.execute("PRAGMA table_info(errors)")
    columns = [col[1] for col in cursor.fetchall()]

    print(f"Current columns: {columns}")

    # Add missing columns
    new_columns = {
        'move_number': 'INTEGER',
        'evaluation_before': 'REAL',
        'evaluation_after': 'REAL',
        'centipawn_loss': 'INTEGER'
    }

    for col_name, col_type in new_columns.items():
        if col_name not in columns:
            print(f"Adding column: {col_name}")
            cursor.execute(f"ALTER TABLE errors ADD COLUMN {col_name} {col_type}")
        else:
            print(f"Column {col_name} already exists")

    conn.commit()
    conn.close()
    print("Migration completed successfully!")

if __name__ == '__main__':
    migrate_database()
