"""
Reset script to delete all error analyses
Run this after updating the analysis engine to re-analyze all games
"""

from app import app, db
from models import Game, Error

def reset_errors():
    """Delete all errors and mark games as unanalyzed"""
    with app.app_context():
        # Count before deletion
        error_count = Error.query.count()
        game_count = Game.query.count()

        print(f"Found {error_count} errors in {game_count} games")

        # Delete all errors
        Error.query.delete()

        # Mark all games as unanalyzed
        Game.query.update({Game.analyzed: False})

        db.session.commit()

        print(f"[OK] Deleted all {error_count} errors")
        print(f"[OK] Marked {game_count} games as unanalyzed")
        print("\nYou can now re-analyze the games with the improved system!")

if __name__ == '__main__':
    print("Chess Coach - Reset Error Analyses")
    print("=" * 50)
    response = input("This will delete all error analyses. Continue? (yes/no): ")

    if response.lower() in ['yes', 'y']:
        reset_errors()
    else:
        print("Cancelled.")
