"""
Migration script to load sample puzzles into the database.
Run this after creating the database to populate it with sample puzzles.
"""
from app import app
from models import db
from puzzle_service import PuzzleService

if __name__ == '__main__':
    with app.app_context():
        # Create all tables
        db.create_all()

        # Load sample puzzles
        print("Loading sample puzzles into database...")
        count = PuzzleService.load_sample_puzzles()
        print(f"Loaded {count} puzzles successfully!")

        # Show stats
        stats = PuzzleService.get_puzzle_stats()
        print(f"\nPuzzle Statistics:")
        print(f"Total puzzles: {stats['total']}")
        print(f"Average rating: {stats['avg_rating']}")
        print(f"Themes: {stats['themes']}")
