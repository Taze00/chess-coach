"""
Script to download and import Lichess puzzle database.
Source: https://database.lichess.org/lichess_db_puzzle.csv.bz2
"""
import requests
import bz2
import csv
from io import TextIOWrapper
from app import app, db
from models import Puzzle
from sqlalchemy.exc import IntegrityError

# Lichess provides a compressed CSV with all puzzles
LICHESS_PUZZLE_URL = "https://database.lichess.org/lichess_db_puzzle.csv.bz2"

def download_and_import_puzzles(limit=100000, min_rating=1000, max_rating=2500):
    """
    Download and import Lichess puzzles.

    Args:
        limit: Maximum number of puzzles to import (default 100,000)
        min_rating: Minimum puzzle rating (default 1000)
        max_rating: Maximum puzzle rating (default 2500)
    """
    print(f"Downloading Lichess puzzle database from {LICHESS_PUZZLE_URL}...")
    print("This may take a few minutes (file is ~200MB compressed)...")

    import tempfile
    import os

    try:
        # Download with streaming to avoid memory issues
        response = requests.get(LICHESS_PUZZLE_URL, stream=True, timeout=60)
        response.raise_for_status()

        print("Download complete! Saving to temporary file...")

        # Save to temporary file first
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv.bz2')
        temp_path = temp_file.name

        # Write compressed data to temp file
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                temp_file.write(chunk)
        temp_file.close()

        print("Decompressing and importing puzzles...")

        # Import puzzles
        imported_count = 0
        skipped_count = 0

        # Decompress using bz2.open and process
        # NOTE: Lichess CSV has NO header row - first line is already a puzzle
        with bz2.open(temp_path, 'rt', encoding='utf-8') as f:
            csv_reader = csv.reader(f)

            with app.app_context():
                for i, row in enumerate(csv_reader):
                    if imported_count >= limit:
                        print(f"\nReached import limit of {limit} puzzles")
                        break

                    # Progress indicator
                    if i % 1000 == 0:
                        print(f"Processing puzzle {i}... (imported: {imported_count}, skipped: {skipped_count})")

                    try:
                        # Parse puzzle data
                        # CSV format (no header): PuzzleId,FEN,Moves,Rating,RatingDeviation,Popularity,NbPlays,Themes,GameUrl,OpeningTags
                        if len(row) < 8:
                            skipped_count += 1
                            continue

                        puzzle_id = row[0]
                        fen = row[1]
                        moves = row[2]
                        rating = int(row[3]) if row[3] else 0
                        rating_deviation = int(row[4]) if row[4] else 0
                        popularity = int(row[5]) if row[5] else 0
                        nb_plays = int(row[6]) if row[6] else 0
                        themes = row[7] if len(row) > 7 else ''
                        game_url = row[8] if len(row) > 8 else ''
                        opening_tags = row[9] if len(row) > 9 else ''

                        # Filter by rating
                        if rating < min_rating or rating > max_rating:
                            skipped_count += 1
                            continue

                        # Create puzzle
                        puzzle = Puzzle(
                            puzzle_id=puzzle_id,
                            fen=fen,
                            moves=moves,
                            rating=rating,
                            rating_deviation=rating_deviation,
                            popularity=popularity,
                            nb_plays=nb_plays,
                            themes=themes,
                            game_url=game_url,
                            opening_tags=opening_tags
                        )

                        db.session.add(puzzle)
                        imported_count += 1

                        # Commit in batches of 1000 for performance
                        if imported_count % 1000 == 0:
                            db.session.commit()
                            print(f"  → Committed {imported_count} puzzles to database")

                    except IntegrityError:
                        # Puzzle already exists
                        db.session.rollback()
                        skipped_count += 1
                        continue
                    except Exception as e:
                        print(f"Error importing puzzle {puzzle_id}: {e}")
                        db.session.rollback()
                        skipped_count += 1
                        continue

                # Final commit
                db.session.commit()

                print("\n=== Import Complete ===")
                print(f"Total puzzles imported: {imported_count}")
                print(f"Total puzzles skipped: {skipped_count}")
                print(f"Rating range: {min_rating} - {max_rating}")

                # Show some statistics
                total_in_db = Puzzle.query.count()
                avg_rating = db.session.query(db.func.avg(Puzzle.rating)).scalar()

                print(f"\n=== Database Statistics ===")
                print(f"Total puzzles in database: {total_in_db}")
                print(f"Average puzzle rating: {avg_rating:.0f}")

        # Cleanup temp file
        try:
            os.unlink(temp_path)
        except:
            pass

    except requests.exceptions.RequestException as e:
        print(f"Error downloading puzzle database: {e}")
        print("\nAlternative: Download manually from:")
        print("https://database.lichess.org/")
        print("And place the .csv file in the project directory")
        return False
    except Exception as e:
        print(f"Unexpected error: {e}")
        return False

    return True


def import_from_local_file(filepath, limit=100000, min_rating=1000, max_rating=2500):
    """
    Import puzzles from a local CSV file (if manually downloaded).

    Args:
        filepath: Path to the .csv file
        limit: Maximum number of puzzles to import
        min_rating: Minimum puzzle rating
        max_rating: Maximum puzzle rating
    """
    print(f"Importing puzzles from {filepath}...")

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            # NOTE: Lichess CSV has NO header row
            csv_reader = csv.reader(f)

            imported_count = 0
            skipped_count = 0

            with app.app_context():
                for i, row in enumerate(csv_reader):
                    if imported_count >= limit:
                        break

                    if i % 1000 == 0:
                        print(f"Processing puzzle {i}... (imported: {imported_count})")

                    try:
                        if len(row) < 8:
                            skipped_count += 1
                            continue

                        puzzle_id = row[0]
                        fen = row[1]
                        moves = row[2]
                        rating = int(row[3]) if row[3] else 0

                        if rating < min_rating or rating > max_rating:
                            skipped_count += 1
                            continue

                        puzzle = Puzzle(
                            puzzle_id=puzzle_id,
                            fen=fen,
                            moves=moves,
                            rating=rating,
                            rating_deviation=int(row[4]) if row[4] else 0,
                            popularity=int(row[5]) if row[5] else 0,
                            nb_plays=int(row[6]) if row[6] else 0,
                            themes=row[7] if len(row) > 7 else '',
                            game_url=row[8] if len(row) > 8 else '',
                            opening_tags=row[9] if len(row) > 9 else ''
                        )

                        db.session.add(puzzle)
                        imported_count += 1

                        if imported_count % 1000 == 0:
                            db.session.commit()

                    except IntegrityError:
                        db.session.rollback()
                        skipped_count += 1
                        continue

                db.session.commit()
                print(f"\nImported {imported_count} puzzles successfully!")

    except FileNotFoundError:
        print(f"File not found: {filepath}")
        return False
    except Exception as e:
        print(f"Error: {e}")
        return False

    return True


if __name__ == '__main__':
    print("=== Lichess Puzzle Database Importer ===\n")
    print("This will download and import puzzles from Lichess.")
    print("Recommended: Import 50,000-100,000 puzzles (balanced size/variety)")
    print()

    # Configuration
    IMPORT_LIMIT = 50000  # Import 50k puzzles (good balance)
    MIN_RATING = 800      # Beginner-friendly
    MAX_RATING = 2500     # Up to advanced

    print(f"Configuration:")
    print(f"  - Import limit: {IMPORT_LIMIT:,} puzzles")
    print(f"  - Rating range: {MIN_RATING} - {MAX_RATING}")
    print()

    print("Starting download...")
    download_and_import_puzzles(
        limit=IMPORT_LIMIT,
        min_rating=MIN_RATING,
        max_rating=MAX_RATING
    )
