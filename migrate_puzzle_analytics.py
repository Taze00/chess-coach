"""
Migration script to add analytics columns to puzzle_progress table.
Run this to update the database schema.
"""
from app import app, db

def migrate_puzzle_progress():
    """Add new columns for puzzle analytics."""
    with app.app_context():
        try:
            # Add new columns using raw SQL (SQLite compatible)
            with db.engine.connect() as conn:
                # Get existing columns
                result = conn.execute(db.text("PRAGMA table_info(puzzle_progress)"))
                existing_columns = [row[1] for row in result]

                print(f"Existing columns: {existing_columns}")

                # Add solve_time_seconds if not exists
                if 'solve_time_seconds' not in existing_columns:
                    conn.execute(db.text("""
                        ALTER TABLE puzzle_progress
                        ADD COLUMN solve_time_seconds INTEGER
                    """))
                    conn.commit()
                    print("[OK] Added solve_time_seconds column")
                else:
                    print("[SKIP] solve_time_seconds already exists")

                # Add rating if not exists
                if 'rating' not in existing_columns:
                    conn.execute(db.text("""
                        ALTER TABLE puzzle_progress
                        ADD COLUMN rating INTEGER
                    """))
                    conn.commit()
                    print("[OK] Added rating column")
                else:
                    print("[SKIP] rating already exists")

                # Add tactical_pattern if not exists
                if 'tactical_pattern' not in existing_columns:
                    conn.execute(db.text("""
                        ALTER TABLE puzzle_progress
                        ADD COLUMN tactical_pattern VARCHAR(100)
                    """))
                    conn.commit()
                    print("[OK] Added tactical_pattern column")
                else:
                    print("[SKIP] tactical_pattern already exists")

            print("\n=== Migration completed successfully ===")
            print("New columns added to puzzle_progress table:")
            print("  - solve_time_seconds: Track solving time")
            print("  - rating: Puzzle difficulty rating")
            print("  - tactical_pattern: Primary tactical theme")

        except Exception as e:
            print(f"Error during migration: {e}")
            import traceback
            traceback.print_exc()

if __name__ == '__main__':
    print("Starting puzzle_progress table migration...")
    migrate_puzzle_progress()
