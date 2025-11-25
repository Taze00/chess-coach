"""
Migration script to add tactical_pattern column to Error table.
"""
from app import app, db

def migrate():
    """Add tactical_pattern column to errors table."""
    with app.app_context():
        print("Adding tactical_pattern column...")

        try:
            # Try to add the column using raw SQL
            db.session.execute(db.text("ALTER TABLE errors ADD COLUMN tactical_pattern VARCHAR(50)"))
            db.session.commit()
            print("Column added successfully!")
        except Exception as e:
            if "duplicate column name" in str(e).lower():
                print("Column already exists!")
            else:
                print(f"Error: {e}")
                db.session.rollback()

if __name__ == '__main__':
    migrate()
