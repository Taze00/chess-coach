"""
Migration script to add tactical_patterns (plural, JSON) column to Error table.
This replaces the singular tactical_pattern column.
"""
from app import app, db
from sqlalchemy import text

def migrate():
    """Add tactical_patterns JSON column to errors table."""
    with app.app_context():
        print("Adding tactical_patterns column...")

        try:
            # Check if column already exists
            result = db.session.execute(text("PRAGMA table_info(errors)"))
            columns = [row[1] for row in result]

            if 'tactical_patterns' in columns:
                print("Column 'tactical_patterns' already exists!")
                return

            # Add new JSON column for multiple patterns
            db.session.execute(text("ALTER TABLE errors ADD COLUMN tactical_patterns TEXT"))
            db.session.commit()
            print("Column 'tactical_patterns' added successfully!")

            print("\nMigrating existing data from tactical_pattern to tactical_patterns...")

            # Migrate existing single pattern to JSON array format
            # SQLite doesn't have native JSON, so we use TEXT with JSON string
            db.session.execute(text("""
                UPDATE errors
                SET tactical_patterns = '["' || tactical_pattern || '"]'
                WHERE tactical_pattern IS NOT NULL
            """))
            db.session.commit()

            print("Data migration completed!")
            print("\nNote: Old 'tactical_pattern' column still exists for backwards compatibility.")
            print("You can manually drop it later if needed: ALTER TABLE errors DROP COLUMN tactical_pattern")

        except Exception as e:
            print(f"Error: {e}")
            db.session.rollback()

if __name__ == '__main__':
    migrate()
