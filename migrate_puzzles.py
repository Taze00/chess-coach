"""
Migration script to add Puzzle table to database.
"""
from app import app, db
from models import Puzzle
from puzzle_service import PuzzleService

def migrate():
    """Create puzzle table and load sample puzzles."""
    with app.app_context():
        print("Creating puzzle table...")
        db.create_all()
        print("Puzzle table created!")

        # Load sample puzzles
        print("\nLoading sample puzzles...")
        count = PuzzleService.load_sample_puzzles()
        print(f"Loaded {count} sample puzzles")

        # Show stats
        stats = PuzzleService.get_puzzle_stats()
        print(f"\nPuzzle Statistics:")
        print(f"  Total puzzles: {stats['total']}")
        print(f"  Average rating: {stats['avg_rating']}")
        print(f"  Themes: {stats['themes']}")

if __name__ == '__main__':
    migrate()
