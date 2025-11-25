"""
Service for loading and managing Lichess puzzles.
"""
import csv
import requests
from io import StringIO
from models import db, Puzzle
from sqlalchemy.exc import IntegrityError


class PuzzleService:
    """Service for managing Lichess puzzles."""

    # Lichess puzzle database URL (CSV format)
    LICHESS_PUZZLE_URL = "https://database.lichess.org/lichess_db_puzzle.csv.zst"

    # Mapping of error types to Lichess puzzle themes
    ERROR_THEME_MAPPING = {
        'blunder': [
            'hangingPiece', 'mate', 'mateIn1', 'mateIn2', 'defensiveMove',
            'attraction', 'deflection', 'clearance', 'sacrifice'
        ],
        'mistake': [
            'fork', 'pin', 'skewer', 'discoveredAttack', 'doubleCheck',
            'exposedKing', 'trappedPiece', 'interference', 'zugzwang'
        ],
        'inaccuracy': [
            'advancedPawn', 'advantage', 'endgame', 'middlegame',
            'opening', 'promotion', 'quietMove', 'long'
        ]
    }

    @staticmethod
    def load_sample_puzzles(limit=100):
        """
        Load sample puzzles from Lichess API.
        Since the full database is huge, we'll use the Lichess API to get puzzles.
        """
        try:
            # Use Lichess API to get puzzles
            # Note: The full database is 2GB+, so we'll fetch via API instead
            print(f"Loading {limit} sample puzzles from Lichess...")

            # For now, we'll create some sample puzzles manually
            # In production, you'd either download the full DB or use the API
            sample_puzzles = [
                {
                    'puzzle_id': 'sample_fork_1',
                    'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4',
                    'moves': 'f3e5,c6e5,d1f3',
                    'rating': 1500,
                    'themes': 'fork,middlegame'
                },
                {
                    'puzzle_id': 'sample_fork_2',
                    'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3',
                    'moves': 'f3e5,d8g5,e5c6',
                    'rating': 1450,
                    'themes': 'fork,opening'
                },
                {
                    'puzzle_id': 'sample_pin_1',
                    'fen': 'r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R b KQkq - 3 3',
                    'moves': 'd8f6,c4f7,e8f7',
                    'rating': 1400,
                    'themes': 'pin,opening'
                },
                {
                    'puzzle_id': 'sample_pin_2',
                    'fen': 'r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/3P1N2/PPP2PPP/RNBQK2R w KQkq - 4 5',
                    'moves': 'c1g5',
                    'rating': 1550,
                    'themes': 'pin,middlegame'
                },
                {
                    'puzzle_id': 'sample_mate_1',
                    'fen': '6k1/5ppp/8/8/8/8/5PPP/4R1K1 w - - 0 1',
                    'moves': 'e1e8',
                    'rating': 1200,
                    'themes': 'mate,mateIn1,endgame'
                },
                {
                    'puzzle_id': 'sample_mate_2',
                    'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p2Q/2B1P3/8/PPPP1PPP/RNB1K1NR w KQkq - 4 4',
                    'moves': 'h5f7',
                    'rating': 1300,
                    'themes': 'mate,mateIn1,middlegame'
                },
                {
                    'puzzle_id': 'sample_hanging_1',
                    'fen': 'r1bqkb1r/pppp1ppp/2n5/4p3/2BnP3/5N2/PPPP1PPP/RNBQK2R w KQkq - 0 4',
                    'moves': 'c4d5',
                    'rating': 1300,
                    'themes': 'hangingPiece,middlegame'
                },
                {
                    'puzzle_id': 'sample_hanging_2',
                    'fen': 'rnbqkb1r/pppp1ppp/5n2/4p3/4P3/5N2/PPPP1PPP/RNBQKB1R w KQkq - 2 3',
                    'moves': 'f3e5',
                    'rating': 1250,
                    'themes': 'hangingPiece,opening'
                },
                {
                    'puzzle_id': 'sample_skewer_1',
                    'fen': '6k1/5ppp/8/8/8/8/5PPP/4RK2 w - - 0 1',
                    'moves': 'e1e8',
                    'rating': 1600,
                    'themes': 'skewer,endgame'
                },
                {
                    'puzzle_id': 'sample_discovered_1',
                    'fen': 'r1bqkb1r/pppp1ppp/2n2n2/4p3/2B1P3/2N2N2/PPPP1PPP/R1BQK2R w KQkq - 4 4',
                    'moves': 'c3d5',
                    'rating': 1650,
                    'themes': 'discoveredAttack,middlegame'
                },
                {
                    'puzzle_id': 'sample_double_attack_1',
                    'fen': 'r1bqk2r/pppp1ppp/2n2n2/2b1p3/2B1P3/2NP1N2/PPP2PPP/R1BQK2R w KQkq - 0 5',
                    'moves': 'c3d5',
                    'rating': 1500,
                    'themes': 'fork,middlegame'
                },
                {
                    'puzzle_id': 'sample_back_rank_1',
                    'fen': '6k1/5ppp/8/8/8/8/5PPP/3R2K1 w - - 0 1',
                    'moves': 'd1d8',
                    'rating': 1350,
                    'themes': 'mate,mateIn1,endgame'
                }
            ]

            loaded_count = 0
            for puzzle_data in sample_puzzles:
                try:
                    puzzle = Puzzle(
                        puzzle_id=puzzle_data['puzzle_id'],
                        fen=puzzle_data['fen'],
                        moves=puzzle_data['moves'],
                        rating=puzzle_data['rating'],
                        rating_deviation=puzzle_data.get('rating_deviation'),
                        popularity=puzzle_data.get('popularity'),
                        nb_plays=puzzle_data.get('nb_plays'),
                        themes=puzzle_data['themes']
                    )
                    db.session.add(puzzle)
                    db.session.commit()
                    loaded_count += 1
                except IntegrityError:
                    db.session.rollback()
                    # Puzzle already exists, skip
                    continue

            print(f"Successfully loaded {loaded_count} puzzles")
            return loaded_count

        except Exception as e:
            print(f"Error loading puzzles: {str(e)}")
            db.session.rollback()
            return 0

    @staticmethod
    def get_puzzle_for_error_type(error_type, user_rating=1500, exclude_ids=None):
        """
        Get a suitable puzzle for a specific error type.

        Args:
            error_type: 'blunder', 'mistake', or 'inaccuracy'
            user_rating: User's chess rating (default 1500)
            exclude_ids: List of puzzle IDs to exclude (default None)

        Returns:
            Puzzle object or None
        """
        if exclude_ids is None:
            exclude_ids = []

        # Get relevant themes for this error type
        themes = PuzzleService.ERROR_THEME_MAPPING.get(error_type, [])

        # Query puzzles with matching themes
        # Rating should be within ±200 of user rating
        min_rating = user_rating - 200
        max_rating = user_rating + 200

        import random

        # Try to find a puzzle with matching themes
        for theme in themes:
            query = Puzzle.query.filter(
                Puzzle.themes.like(f'%{theme}%'),
                Puzzle.rating >= min_rating,
                Puzzle.rating <= max_rating
            )

            # Exclude solved puzzles if list is provided
            if exclude_ids:
                query = query.filter(~Puzzle.puzzle_id.in_(exclude_ids))

            # Get all matching puzzles and pick one randomly
            puzzles = query.all()
            if puzzles:
                return random.choice(puzzles)

        # Fallback: return any puzzle in the rating range (excluding solved ones)
        query = Puzzle.query.filter(
            Puzzle.rating >= min_rating,
            Puzzle.rating <= max_rating
        )

        if exclude_ids:
            query = query.filter(~Puzzle.puzzle_id.in_(exclude_ids))

        # Get all and pick randomly
        puzzles = query.all()
        return random.choice(puzzles) if puzzles else None

    @staticmethod
    def get_puzzle_for_tactical_pattern(tactical_pattern, user_rating=1500, exclude_ids=None):
        """
        Get a suitable puzzle for a specific tactical pattern.

        Args:
            tactical_pattern: 'fork', 'pin', 'hangingPiece', 'mate', etc.
            user_rating: User's chess rating (default 1500)
            exclude_ids: List of puzzle IDs to exclude (default None)

        Returns:
            Puzzle object or None
        """
        if exclude_ids is None:
            exclude_ids = []

        # Query puzzles with matching pattern
        # Rating should be within ±200 of user rating
        min_rating = user_rating - 200
        max_rating = user_rating + 200

        import random

        # Try to find a puzzle with this specific pattern
        query = Puzzle.query.filter(
            Puzzle.themes.like(f'%{tactical_pattern}%'),
            Puzzle.rating >= min_rating,
            Puzzle.rating <= max_rating
        )

        # Exclude solved puzzles if list is provided
        if exclude_ids:
            query = query.filter(~Puzzle.puzzle_id.in_(exclude_ids))

        # Get all matching puzzles and pick one randomly
        puzzles = query.all()
        if puzzles:
            return random.choice(puzzles)

        # Fallback: return any puzzle in the rating range (excluding solved ones)
        query = Puzzle.query.filter(
            Puzzle.rating >= min_rating,
            Puzzle.rating <= max_rating
        )

        if exclude_ids:
            query = query.filter(~Puzzle.puzzle_id.in_(exclude_ids))

        # Get all and pick randomly
        puzzles = query.all()
        return random.choice(puzzles) if puzzles else None

    @staticmethod
    def get_random_puzzle(user_rating=1500):
        """Get a random puzzle appropriate for user's rating."""
        min_rating = user_rating - 200
        max_rating = user_rating + 200

        return Puzzle.query.filter(
            Puzzle.rating >= min_rating,
            Puzzle.rating <= max_rating
        ).order_by(db.func.random()).first()

    @staticmethod
    def get_puzzle_stats():
        """Get statistics about loaded puzzles."""
        total = Puzzle.query.count()

        if total == 0:
            return {
                'total': 0,
                'avg_rating': 0,
                'themes': {}
            }

        avg_rating = db.session.query(db.func.avg(Puzzle.rating)).scalar()

        # Count puzzles by theme
        theme_counts = {}
        puzzles = Puzzle.query.all()
        for puzzle in puzzles:
            for theme in puzzle.get_themes_list():
                theme_counts[theme] = theme_counts.get(theme, 0) + 1

        return {
            'total': total,
            'avg_rating': round(avg_rating, 0) if avg_rating else 0,
            'themes': theme_counts
        }
