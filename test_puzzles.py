"""
Test script to check Lichess puzzle data format.
"""
import requests
import bz2
import csv
import tempfile

LICHESS_PUZZLE_URL = "https://database.lichess.org/lichess_db_puzzle.csv.bz2"

print("Downloading and checking first 20 puzzles...")

try:
    # Download
    response = requests.get(LICHESS_PUZZLE_URL, stream=True, timeout=60)
    response.raise_for_status()

    # Save to temp file
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.csv.bz2')
    temp_path = temp_file.name

    for chunk in response.iter_content(chunk_size=8192):
        if chunk:
            temp_file.write(chunk)
    temp_file.close()

    print("Download complete! Checking first 20 puzzles:\n")

    # Read first 20 puzzles
    with bz2.open(temp_path, 'rt', encoding='utf-8') as f:
        csv_reader = csv.DictReader(f)

        # Print headers
        first_row = next(csv_reader)
        print("CSV Headers:")
        print(list(first_row.keys()))
        print()

        print("First puzzle data:")
        for key, value in first_row.items():
            print(f"  {key}: {value}")
        print()

        # Print next 5 puzzles
        for i in range(5):
            row = next(csv_reader)
            print(f"Puzzle {i+2}:")
            print(f"  Data keys: {list(row.keys())[:5]}")
            print(f"  First value: {list(row.values())[0]}")
            print()

    # Cleanup
    import os
    os.unlink(temp_path)

except Exception as e:
    print(f"Error: {e}")
