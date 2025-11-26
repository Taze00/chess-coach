from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort, session
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv
import os
import time

from models import db, User, Game, Puzzle, PuzzleProgress, Error
from auth import auth, bcrypt
from chess_api import ChessComAPI
from stockfish_analyzer import StockfishAnalyzer
from puzzle_service import PuzzleService
from datetime import datetime

# Global progress tracker
analysis_progress = {}

# Load environment variables
load_dotenv(override=True)

# Initialize Flask app
app = Flask(__name__)

# Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chess_coach.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db.init_app(app)
bcrypt.init_app(app)

# Initialize Login Manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth.login'
login_manager.login_message = 'Bitte einloggen um auf diese Seite zuzugreifen.'
login_manager.login_message_category = 'info'


@login_manager.user_loader
def load_user(user_id):
    """Load user by ID for Flask-Login."""
    return User.query.get(int(user_id))


# Register blueprints
app.register_blueprint(auth)


# Routes
@app.route('/')
def index():
    """Landing page."""
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    return render_template('index.html')


@app.route('/api/dashboard-stats', methods=['GET'])
@login_required
def get_dashboard_stats():
    """Get comprehensive dashboard statistics for the user."""
    from datetime import datetime, timedelta
    from models import Error

    try:
        # Get current date
        now = datetime.utcnow()
        week_ago = now - timedelta(days=7)
        two_weeks_ago = now - timedelta(days=14)

        # === CURRENT WEEK STATS ===
        current_week_puzzles = PuzzleProgress.query.filter(
            PuzzleProgress.user_id == current_user.id,
            PuzzleProgress.last_attempt >= week_ago
        ).all()

        current_week_solved = [p for p in current_week_puzzles if p.solved]
        current_week_count = len(current_week_solved)
        current_week_success = (len(current_week_solved) / len(current_week_puzzles) * 100) if current_week_puzzles else 0

        # Average time this week
        current_week_times = [p.solve_time_seconds for p in current_week_solved if p.solve_time_seconds]
        current_week_avg_time = sum(current_week_times) / len(current_week_times) if current_week_times else 0

        # === LAST WEEK STATS ===
        last_week_puzzles = PuzzleProgress.query.filter(
            PuzzleProgress.user_id == current_user.id,
            PuzzleProgress.last_attempt >= two_weeks_ago,
            PuzzleProgress.last_attempt < week_ago
        ).all()

        last_week_solved = [p for p in last_week_puzzles if p.solved]
        last_week_count = len(last_week_solved)
        last_week_success = (len(last_week_solved) / len(last_week_puzzles) * 100) if last_week_puzzles else 0

        last_week_times = [p.solve_time_seconds for p in last_week_solved if p.solve_time_seconds]
        last_week_avg_time = sum(last_week_times) / len(last_week_times) if last_week_times else 0

        # === STREAK CALCULATION ===
        # Get all solved puzzles ordered by date
        all_solved = PuzzleProgress.query.filter(
            PuzzleProgress.user_id == current_user.id,
            PuzzleProgress.solved == True,
            PuzzleProgress.last_attempt.isnot(None)
        ).order_by(PuzzleProgress.last_attempt.desc()).all()

        # Calculate streak
        streak_days = 0
        if all_solved:
            current_date = now.date()
            checked_dates = set()

            for puzzle in all_solved:
                puzzle_date = puzzle.last_attempt.date()

                # Skip if we've already counted this date
                if puzzle_date in checked_dates:
                    continue

                checked_dates.add(puzzle_date)

                # Check if this date is consecutive
                expected_date = current_date - timedelta(days=streak_days)
                if puzzle_date == expected_date:
                    streak_days += 1
                elif puzzle_date < expected_date:
                    # Gap found, streak ends
                    break

        # === TOP 3 WEAKNESSES ===
        pattern_stats = {}
        all_progress = PuzzleProgress.query.filter_by(user_id=current_user.id).all()

        for progress in all_progress:
            if progress.tactical_pattern:
                pattern = progress.tactical_pattern
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {'total': 0, 'solved': 0}
                pattern_stats[pattern]['total'] += 1
                if progress.solved:
                    pattern_stats[pattern]['solved'] += 1

        # Calculate success rates
        weaknesses = []
        for pattern, stats in pattern_stats.items():
            if stats['total'] >= 3:  # Only patterns with at least 3 attempts
                success_rate = (stats['solved'] / stats['total'] * 100)
                weaknesses.append({
                    'pattern': pattern,
                    'success_rate': round(success_rate, 1),
                    'total': stats['total'],
                    'solved': stats['solved']
                })

        # Sort by success rate (ascending) and take top 3
        weaknesses.sort(key=lambda x: x['success_rate'])
        top_weaknesses = weaknesses[:3]

        # === RECENT ACTIVITY ===
        recent_puzzles = PuzzleProgress.query.filter_by(
            user_id=current_user.id
        ).order_by(PuzzleProgress.last_attempt.desc()).limit(10).all()

        recent_activity = []
        for p in recent_puzzles:
            # Get puzzle details
            puzzle = Puzzle.query.filter_by(puzzle_id=p.puzzle_id).first()

            # Calculate time ago
            time_diff = now - p.last_attempt
            if time_diff.seconds < 60:
                time_ago = f"vor {time_diff.seconds} Sek"
            elif time_diff.seconds < 3600:
                time_ago = f"vor {time_diff.seconds // 60} Min"
            elif time_diff.days == 0:
                time_ago = f"vor {time_diff.seconds // 3600} Std"
            else:
                time_ago = f"vor {time_diff.days} Tag{'en' if time_diff.days > 1 else ''}"

            recent_activity.append({
                'solved': p.solved,
                'pattern': p.tactical_pattern,
                'rating': p.rating,
                'time_ago': time_ago,
                'is_retry': p.attempts > 1
            })

        # === ACHIEVEMENTS ===
        total_solved = PuzzleProgress.query.filter_by(
            user_id=current_user.id,
            solved=True
        ).count()

        overall_success_rate = (total_solved / len(all_progress) * 100) if all_progress else 0

        achievements = [
            {
                'title': '50 Puzzles gelöst',
                'current': total_solved,
                'target': 50,
                'progress': min((total_solved / 50 * 100), 100)
            },
            {
                'title': '80% Erfolgsrate',
                'current': round(overall_success_rate, 1),
                'target': 80,
                'progress': min((overall_success_rate / 80 * 100), 100)
            },
            {
                'title': '10 Tage Streak',
                'current': streak_days,
                'target': 10,
                'progress': min((streak_days / 10 * 100), 100)
            }
        ]

        # === OVERALL STATS ===
        games_count = Game.query.filter_by(user_id=current_user.id).count()
        errors_count = Error.query.filter_by(user_id=current_user.id).count()

        return jsonify({
            'success': True,
            'current_week': {
                'puzzles_solved': current_week_count,
                'success_rate': round(current_week_success, 1),
                'avg_time': int(current_week_avg_time)
            },
            'last_week': {
                'puzzles_solved': last_week_count,
                'success_rate': round(last_week_success, 1),
                'avg_time': int(last_week_avg_time)
            },
            'streak_days': streak_days,
            'weaknesses': top_weaknesses,
            'recent_activity': recent_activity,
            'achievements': achievements,
            'overall': {
                'total_solved': total_solved,
                'total_games': games_count,
                'total_errors': errors_count,
                'success_rate': round(overall_success_rate, 1)
            }
        })

    except Exception as e:
        print(f"Error getting dashboard stats: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for logged-in users."""
    from models import Error

    # Get user statistics
    games_count = Game.query.filter_by(user_id=current_user.id).count()
    errors_count = Error.query.filter_by(user_id=current_user.id).count()

    # Get tactical pattern distribution
    pattern_stats = {}
    errors = Error.query.filter_by(user_id=current_user.id).all()

    for error in errors:
        # Count primary pattern
        if error.tactical_pattern:
            pattern_stats[error.tactical_pattern] = pattern_stats.get(error.tactical_pattern, 0) + 1

    # Sort by count (descending)
    pattern_stats_sorted = sorted(pattern_stats.items(), key=lambda x: -x[1])

    # Get top 10 most common patterns
    top_patterns = pattern_stats_sorted[:10]

    # German translations for patterns
    pattern_translations = {
        'advantage': 'Vorteil',
        'mate': 'Matt',
        'fork': 'Gabel',
        'pin': 'Fesselung',
        'skewer': 'Spieß',
        'discoveredAttack': 'Abzugsangriff',
        'hangingPiece': 'Hängende Figur',
        'castling': 'Rochade',
        'sacrifice': 'Opfer',
        'attackingF2F7': 'Angriff auf f2/f7',
        'exposedKing': 'Exponierter König',
        'trappedPiece': 'Gefangene Figur',
        'backRankMate': 'Grundreihenmatt',
        'smotheredMate': 'Ersticktes Matt'
    }

    stats = {
        'games_count': games_count,
        'errors_count': errors_count,
        'puzzles_solved': 0,  # Will be populated in Phase 5
        'pattern_stats': top_patterns,
        'pattern_translations': pattern_translations
    }
    return render_template('dashboard.html', stats=stats)


@app.route('/analyse')
@login_required
def analyse():
    """Analysis page: Import games, view errors, and performance stats."""
    from models import Error
    from flask import request

    # Get optional pattern filter from query string
    pattern_filter = request.args.get('pattern')

    # Get all errors for current user
    query = Error.query.filter_by(user_id=current_user.id)

    # Apply pattern filter if specified
    if pattern_filter:
        # Filter by tactical_pattern (single pattern) or tactical_patterns (multi-pattern JSON)
        query = query.filter(
            db.or_(
                Error.tactical_pattern == pattern_filter,
                Error.tactical_patterns.like(f'%{pattern_filter}%')
            )
        )

    user_errors = query.order_by(Error.created_at.desc()).all()

    # Categorize errors
    categorized = {
        'blunders': [e for e in user_errors if e.error_type == 'blunder'],
        'mistakes': [e for e in user_errors if e.error_type == 'mistake'],
        'inaccuracies': [e for e in user_errors if e.error_type == 'inaccuracy']
    }

    # German translations for tactical patterns
    pattern_translations = {
        'advantage': 'Vorteil',
        'mate': 'Matt',
        'mateIn1': 'Matt in 1',
        'mateIn2': 'Matt in 2',
        'mateIn3': 'Matt in 3',
        'fork': 'Gabel',
        'pin': 'Fesselung',
        'skewer': 'Spieß',
        'discoveredAttack': 'Abzugsangriff',
        'hangingPiece': 'Hängende Figur',
        'castling': 'Rochade',
        'sacrifice': 'Opfer',
        'backRankMate': 'Grundreihenmatt',
        'smotheredMate': 'Ersticktes Matt',
        'trappedPiece': 'Gefangene Figur',
        'exposedKing': 'Exponierter König',
        'kingsideAttack': 'Königsflügel-Angriff',
        'queensideAttack': 'Damenflügel-Angriff',
        'middlegame': 'Mittelspiel',
        'endgame': 'Endspiel',
        'opening': 'Eröffnung',
        'defensiveMove': 'Verteidigung',
        'quietMove': 'Ruhiger Zug',
        'crushing': 'Vernichtend'
    }

    return render_template('analyse.html',
                          errors=user_errors,
                          categorized=categorized,
                          pattern_translations=pattern_translations,
                          pattern_filter=pattern_filter)


@app.route('/errors/<int:error_id>')
@login_required
def error_detail(error_id):
    """Detailed error analysis page with chess board."""
    from models import Error
    import chess.pgn
    from io import StringIO

    # Get error and verify ownership
    error = Error.query.get_or_404(error_id)

    if error.user_id != current_user.id:
        abort(403)

    # Get the game to access full PGN
    game = Game.query.get(error.game_id)

    # Parse PGN to get all moves
    pgn = chess.pgn.read_game(StringIO(game.pgn))

    # Extract all moves from the game
    moves = []
    board = pgn.board()
    for move in pgn.mainline_moves():
        moves.append({
            'uci': move.uci(),
            'san': board.san(move),
            'fen': board.fen()
        })
        board.push(move)

    return render_template('error_detail.html', error=error, game=game, moves=moves)


@app.route('/training')
@login_required
def training():
    """Training interface page with personalized puzzles."""
    from flask import request

    # Get optional pattern filter from query string
    pattern_filter = request.args.get('pattern')

    # Get user's most common error type
    error_stats = db.session.query(
        Error.error_type,
        db.func.count(Error.id).label('count')
    ).filter_by(user_id=current_user.id).group_by(Error.error_type).order_by(
        db.func.count(Error.id).desc()
    ).all()

    # Calculate total errors and percentages
    total_errors = sum([stat[1] for stat in error_stats])
    error_distribution = {
        stat[0]: {
            'count': stat[1],
            'percentage': round((stat[1] / total_errors * 100), 1) if total_errors > 0 else 0
        }
        for stat in error_stats
    }

    # Get puzzle stats
    puzzle_stats = PuzzleService.get_puzzle_stats()

    # Get user's solved puzzle count
    solved_count = PuzzleProgress.query.filter_by(
        user_id=current_user.id,
        solved=True
    ).count()

    # German translations for tactical patterns
    pattern_translations = {
        'advantage': 'Vorteil',
        'mate': 'Matt',
        'mateIn1': 'Matt in 1',
        'mateIn2': 'Matt in 2',
        'mateIn3': 'Matt in 3',
        'fork': 'Gabel',
        'pin': 'Fesselung',
        'skewer': 'Spieß',
        'discoveredAttack': 'Abzugsangriff',
        'hangingPiece': 'Hängende Figur',
        'castling': 'Rochade',
        'sacrifice': 'Opfer',
        'backRankMate': 'Grundreihenmatt',
        'smotheredMate': 'Ersticktes Matt',
        'trappedPiece': 'Gefangene Figur',
        'exposedKing': 'Exponierter König'
    }

    return render_template(
        'training.html',
        error_distribution=error_distribution,
        puzzle_stats=puzzle_stats,
        solved_count=solved_count,
        pattern_filter=pattern_filter,
        pattern_translations=pattern_translations
    )


@app.route('/api/get-puzzle', methods=['GET'])
@login_required
def get_puzzle():
    """
    Get a personalized puzzle based on user's error patterns.

    Query params:
        error_type: Optional specific error type to train (blunder/mistake/inaccuracy)

    Returns:
        JSON with puzzle data
    """
    try:
        # Get tactical pattern from query params or use most common
        tactical_pattern = request.args.get('pattern')

        if not tactical_pattern:
            # Find user's most common tactical pattern (excluding generic ones)
            most_common = db.session.query(
                Error.tactical_pattern,
                db.func.count(Error.id).label('count')
            ).filter(
                Error.user_id == current_user.id,
                Error.tactical_pattern.isnot(None),
                # Exclude very generic patterns to focus on specific tactics
                ~Error.tactical_pattern.in_(['advantage', 'middlegame', 'endgame', 'opening'])
            ).group_by(Error.tactical_pattern).order_by(
                db.func.count(Error.id).desc()
            ).first()

            if most_common:
                tactical_pattern = most_common[0]
                print(f"Most common SPECIFIC pattern: {tactical_pattern} ({most_common[1]} occurrences)")
            else:
                # If no specific pattern found, try all patterns including generic ones
                fallback = db.session.query(
                    Error.tactical_pattern,
                    db.func.count(Error.id).label('count')
                ).filter(
                    Error.user_id == current_user.id,
                    Error.tactical_pattern.isnot(None)
                ).group_by(Error.tactical_pattern).order_by(
                    db.func.count(Error.id).desc()
                ).first()

                tactical_pattern = fallback[0] if fallback else 'fork'
                print(f"Fallback pattern: {tactical_pattern}")

        # SPACED REPETITION SYSTEM
        # 1. Get failed puzzles that should be reviewed (not attempted in last 24 hours)
        from datetime import datetime, timedelta

        review_threshold = datetime.utcnow() - timedelta(hours=24)
        failed_puzzles = PuzzleProgress.query.filter(
            PuzzleProgress.user_id == current_user.id,
            PuzzleProgress.solved == False,
            PuzzleProgress.attempts > 0,
            PuzzleProgress.last_attempt < review_threshold
        ).all()

        # 2. Get successfully solved puzzles (exclude these)
        solved_puzzle_ids = [p.puzzle_id for p in PuzzleProgress.query.filter_by(
            user_id=current_user.id,
            solved=True
        ).all()]

        # 3. Track seen puzzles in this session (to avoid immediate repeats)
        if 'seen_puzzles' not in session:
            session['seen_puzzles'] = []

        # 4. Combine solved and recently seen
        exclude_ids = list(set(solved_puzzle_ids + session['seen_puzzles']))

        print(f"Tactical pattern: {tactical_pattern}")
        print(f"Solved puzzle IDs: {solved_puzzle_ids}")
        print(f"Failed puzzles to review: {len(failed_puzzles)}")
        print(f"Seen in session: {session['seen_puzzles']}")
        print(f"Total puzzles in DB: {Puzzle.query.count()}")

        # 5. PRIORITY: Try to get a failed puzzle that matches the tactical pattern first
        puzzle = None
        if failed_puzzles:
            # Filter failed puzzles by tactical pattern
            matching_failed = [fp for fp in failed_puzzles
                             if fp.puzzle_id not in session['seen_puzzles']]

            if matching_failed:
                # Get the actual Puzzle objects for failed attempts
                failed_puzzle_ids = [fp.puzzle_id for fp in matching_failed]
                puzzle = Puzzle.query.filter(
                    Puzzle.puzzle_id.in_(failed_puzzle_ids),
                    Puzzle.themes.like(f'%{tactical_pattern}%')
                ).first()

                if puzzle:
                    print(f"[SPACED REPETITION] Returning failed puzzle: {puzzle.puzzle_id}")

        # 6. If no failed puzzle found, get a new puzzle (excluding solved and seen ones)
        if not puzzle:
            puzzle = PuzzleService.get_puzzle_for_tactical_pattern(tactical_pattern, user_rating=1500, exclude_ids=exclude_ids)

        print(f"Puzzle for pattern '{tactical_pattern}': {puzzle.puzzle_id if puzzle else 'None'}")

        # If no unsolved puzzles found, clear session history and try again
        if not puzzle:
            session['seen_puzzles'] = []
            puzzle = PuzzleService.get_puzzle_for_tactical_pattern(tactical_pattern, user_rating=1500, exclude_ids=solved_puzzle_ids)

        # Still nothing? Get any random puzzle
        if not puzzle:
            puzzle = PuzzleService.get_random_puzzle(user_rating=1500)
            print(f"Random puzzle: {puzzle.puzzle_id if puzzle else 'None'}")

        if not puzzle:
            return jsonify({
                'success': False,
                'message': 'Keine passenden Puzzles gefunden.'
            }), 404

        # Add to seen puzzles in session
        if puzzle.puzzle_id not in session['seen_puzzles']:
            session['seen_puzzles'].append(puzzle.puzzle_id)
            # Keep only last 20 seen puzzles
            if len(session['seen_puzzles']) > 20:
                session['seen_puzzles'] = session['seen_puzzles'][-20:]
            session.modified = True

        print(f"Selected puzzle: {puzzle.puzzle_id}")

        # Check if user has already attempted this puzzle
        progress = PuzzleProgress.query.filter_by(
            user_id=current_user.id,
            puzzle_id=puzzle.puzzle_id
        ).first()

        return jsonify({
            'success': True,
            'puzzle': {
                'id': puzzle.puzzle_id,
                'fen': puzzle.fen,
                'moves': puzzle.moves.split(' ') if puzzle.moves else [],  # Lichess uses spaces
                'rating': puzzle.rating,
                'themes': puzzle.get_themes_list(),
                'tactical_pattern': tactical_pattern
            },
            'progress': {
                'attempts': progress.attempts if progress else 0,
                'solved': progress.solved if progress else False
            }
        })

    except Exception as e:
        print(f"Error getting puzzle: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Fehler beim Laden des Puzzles.'
        }), 500


@app.route('/api/submit-puzzle', methods=['POST'])
@login_required
def submit_puzzle():
    """
    Submit a puzzle solution attempt.

    JSON body:
        puzzle_id: Puzzle ID
        moves: List of moves played by user (UCI format)
        solved: Boolean indicating if puzzle was solved
        error_type: Error type being trained

    Returns:
        JSON with result
    """
    try:
        data = request.get_json()
        puzzle_id = data.get('puzzle_id')
        solved = data.get('solved', False)
        error_type = data.get('error_type')
        solve_time = data.get('solve_time_seconds')  # Time in seconds
        rating = data.get('rating')  # Puzzle rating
        tactical_pattern = data.get('tactical_pattern')  # Primary pattern

        if not puzzle_id:
            return jsonify({
                'success': False,
                'message': 'Puzzle ID fehlt.'
            }), 400

        # Get or create progress record
        progress = PuzzleProgress.query.filter_by(
            user_id=current_user.id,
            puzzle_id=puzzle_id
        ).first()

        if not progress:
            progress = PuzzleProgress(
                user_id=current_user.id,
                puzzle_id=puzzle_id,
                error_type=error_type
            )
            db.session.add(progress)

        # Update progress
        progress.attempts += 1
        progress.last_attempt = datetime.utcnow()

        # Save analytics data
        if solve_time:
            progress.solve_time_seconds = solve_time
        if rating:
            progress.rating = rating
        if tactical_pattern:
            progress.tactical_pattern = tactical_pattern

        if solved and not progress.solved:
            progress.solved = True

        db.session.commit()

        return jsonify({
            'success': True,
            'solved': progress.solved,
            'attempts': progress.attempts,
            'message': 'Richtig! Gut gemacht!' if solved else 'Nicht ganz, versuch es nochmal!'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error submitting puzzle: {e}")
        return jsonify({
            'success': False,
            'message': 'Fehler beim Speichern.'
        }), 500


@app.route('/api/puzzle-statistics', methods=['GET'])
@login_required
def get_puzzle_statistics():
    """
    Get detailed puzzle statistics for the current user.

    Returns:
        JSON with comprehensive analytics:
        - Total puzzles attempted/solved
        - Success rate by tactical pattern
        - Average solve time
        - Difficulty breakdown
        - Recent progress
    """
    try:
        # Get all puzzle progress for user
        all_progress = PuzzleProgress.query.filter_by(
            user_id=current_user.id
        ).all()

        solved_puzzles = [p for p in all_progress if p.solved]

        # Overall statistics
        total_attempted = len(all_progress)
        total_solved = len(solved_puzzles)
        success_rate = (total_solved / total_attempted * 100) if total_attempted > 0 else 0

        # Average solve time (only for solved puzzles with time data)
        solve_times = [p.solve_time_seconds for p in solved_puzzles if p.solve_time_seconds]
        avg_solve_time = sum(solve_times) / len(solve_times) if solve_times else 0

        # Pattern-based statistics
        pattern_stats = {}
        for progress in solved_puzzles:
            if progress.tactical_pattern:
                pattern = progress.tactical_pattern
                if pattern not in pattern_stats:
                    pattern_stats[pattern] = {'solved': 0, 'total': 0, 'avg_time': []}
                pattern_stats[pattern]['solved'] += 1
                if progress.solve_time_seconds:
                    pattern_stats[pattern]['avg_time'].append(progress.solve_time_seconds)

        # Count total attempts per pattern
        for progress in all_progress:
            if progress.tactical_pattern:
                pattern = progress.tactical_pattern
                if pattern in pattern_stats:
                    pattern_stats[pattern]['total'] += 1

        # Calculate success rates and average times per pattern
        pattern_breakdown = []
        for pattern, stats in pattern_stats.items():
            success_rate_pattern = (stats['solved'] / stats['total'] * 100) if stats['total'] > 0 else 0
            avg_time_pattern = sum(stats['avg_time']) / len(stats['avg_time']) if stats['avg_time'] else 0

            pattern_breakdown.append({
                'pattern': pattern,
                'solved': stats['solved'],
                'total': stats['total'],
                'success_rate': round(success_rate_pattern, 1),
                'avg_time_seconds': round(avg_time_pattern, 1)
            })

        # Sort by success rate (lowest first - needs practice)
        pattern_breakdown.sort(key=lambda x: x['success_rate'])

        # Difficulty breakdown
        difficulty_stats = {
            'easy': {'solved': 0, 'total': 0},
            'medium': {'solved': 0, 'total': 0},
            'hard': {'solved': 0, 'total': 0}
        }

        for progress in all_progress:
            if progress.rating:
                if progress.rating < 1400:
                    difficulty = 'easy'
                elif progress.rating > 1700:
                    difficulty = 'hard'
                else:
                    difficulty = 'medium'

                difficulty_stats[difficulty]['total'] += 1
                if progress.solved:
                    difficulty_stats[difficulty]['solved'] += 1

        # Recent activity (last 7 days)
        from datetime import timedelta
        seven_days_ago = datetime.utcnow() - timedelta(days=7)
        recent_puzzles = [p for p in all_progress if p.last_attempt and p.last_attempt >= seven_days_ago]
        recent_solved = [p for p in recent_puzzles if p.solved]

        return jsonify({
            'success': True,
            'statistics': {
                'overall': {
                    'total_attempted': total_attempted,
                    'total_solved': total_solved,
                    'success_rate': round(success_rate, 1),
                    'avg_solve_time_seconds': round(avg_solve_time, 1)
                },
                'pattern_breakdown': pattern_breakdown,
                'difficulty': {
                    'easy': {
                        'solved': difficulty_stats['easy']['solved'],
                        'total': difficulty_stats['easy']['total'],
                        'success_rate': round((difficulty_stats['easy']['solved'] / difficulty_stats['easy']['total'] * 100) if difficulty_stats['easy']['total'] > 0 else 0, 1)
                    },
                    'medium': {
                        'solved': difficulty_stats['medium']['solved'],
                        'total': difficulty_stats['medium']['total'],
                        'success_rate': round((difficulty_stats['medium']['solved'] / difficulty_stats['medium']['total'] * 100) if difficulty_stats['medium']['total'] > 0 else 0, 1)
                    },
                    'hard': {
                        'solved': difficulty_stats['hard']['solved'],
                        'total': difficulty_stats['hard']['total'],
                        'success_rate': round((difficulty_stats['hard']['solved'] / difficulty_stats['hard']['total'] * 100) if difficulty_stats['hard']['total'] > 0 else 0, 1)
                    }
                },
                'recent': {
                    'last_7_days': {
                        'attempted': len(recent_puzzles),
                        'solved': len(recent_solved)
                    }
                }
            }
        })

    except Exception as e:
        print(f"Error getting puzzle statistics: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': 'Fehler beim Laden der Statistiken.'
        }), 500


@app.route('/api/import-games', methods=['POST'])
@login_required
def import_games():
    """
    Import games from Chess.com for the current user.

    Returns:
        JSON response with import status
    """
    try:
        # Get username from current user
        username = current_user.chesscom_username

        # Initialize Chess.com API client
        chess_api = ChessComAPI()

        # Validate username
        if not chess_api.validate_username(username):
            return jsonify({
                'success': False,
                'message': f'Chess.com User "{username}" nicht gefunden.'
            }), 404

        # Fetch recent games (limit 1000 for comprehensive analysis)
        games_data = chess_api.get_recent_games(username, limit=1000)

        if not games_data:
            return jsonify({
                'success': False,
                'message': 'Keine Spiele gefunden.'
            }), 404

        # Import games to database
        imported_count = 0
        skipped_count = 0

        for game_data in games_data:
            # Check if game already exists (duplicate check)
            existing_game = Game.query.filter_by(
                user_id=current_user.id,
                chesscom_url=game_data['url']
            ).first()

            if existing_game:
                skipped_count += 1
                continue

            # Create new game
            new_game = Game(
                user_id=current_user.id,
                pgn=game_data['pgn'],
                result=game_data['result'],
                played_at=game_data['played_at'],
                chesscom_url=game_data['url'],
                analyzed=False
            )

            db.session.add(new_game)
            imported_count += 1

        # Commit to database
        db.session.commit()

        return jsonify({
            'success': True,
            'imported': imported_count,
            'skipped': skipped_count,
            'message': f'{imported_count} neue Spiele importiert, {skipped_count} bereits vorhanden.'
        })

    except Exception as e:
        db.session.rollback()
        print(f"Error importing games: {e}")
        return jsonify({
            'success': False,
            'message': 'Fehler beim Importieren der Spiele.'
        }), 500


@app.route('/api/analysis-progress', methods=['GET'])
@login_required
def analysis_progress_endpoint():
    """Get current analysis progress for the user"""
    progress_key = f"analysis_{current_user.id}"
    progress = analysis_progress.get(progress_key, {
        'current': 0,
        'total': 0,
        'percent': 0,
        'estimated_seconds': 0,
        'current_action': 'Warte...',
        'errors_found': 0
    })
    return jsonify(progress)


@app.route('/api/analyze-games', methods=['POST'])
@login_required
def analyze_games():
    """
    Analyze all unanalyzed games for the current user using Stockfish.

    Returns:
        JSON response with analysis status
    """
    try:
        # Get all unanalyzed games for the current user
        unanalyzed_games = Game.query.filter_by(
            user_id=current_user.id,
            analyzed=False
        ).all()

        if not unanalyzed_games:
            return jsonify({
                'success': True,
                'analyzed': 0,
                'message': 'Alle Spiele bereits analysiert!'
            })

        # Initialize Stockfish analyzer
        analyzer = StockfishAnalyzer()

        analyzed_count = 0
        total_errors = 0
        total_games = len(unanalyzed_games)

        start_time = time.time()
        progress_key = f"analysis_{current_user.id}"

        for idx, game in enumerate(unanalyzed_games, 1):
            # Update progress
            elapsed = time.time() - start_time
            avg_time_per_game = elapsed / idx if idx > 0 else 0
            remaining_games = total_games - idx
            estimated_time_left = avg_time_per_game * remaining_games

            analysis_progress[progress_key] = {
                'current': idx,
                'total': total_games,
                'percent': int((idx / total_games) * 100),
                'estimated_seconds': int(estimated_time_left),
                'current_action': f'Analysiere Spiel {idx}/{total_games}...',
                'errors_found': total_errors
            }

            # Determine player color from PGN
            import chess.pgn
            from io import StringIO

            pgn_io = StringIO(game.pgn)
            chess_game = chess.pgn.read_game(pgn_io)

            # Get player names from headers
            white_player = chess_game.headers.get('White', '').lower()
            black_player = chess_game.headers.get('Black', '').lower()
            username = current_user.chesscom_username.lower()

            # Determine which color the user played
            if username in white_player:
                player_color = 'white'
            elif username in black_player:
                player_color = 'black'
            else:
                # Skip if we can't determine color
                continue

            # Update: Analyzing with Stockfish
            analysis_progress[progress_key]['current_action'] = f'Stockfish analysiert Spiel {idx}/{total_games}...'

            # Analyze the game
            errors = analyzer.analyze_game(game.pgn, player_color)

            # Update: Saving errors
            analysis_progress[progress_key]['current_action'] = f'Speichere {len(errors)} Fehler...'

            # Save errors to database
            from models import Error

            for error_data in errors:
                new_error = Error(
                    game_id=game.id,
                    user_id=current_user.id,
                    move_number=error_data['move_number'],
                    position=error_data['fen'],
                    move_played=error_data['player_move'],
                    best_move=error_data['best_move'],
                    evaluation_before=error_data['evaluation_before'],
                    evaluation_after=error_data['evaluation_after'],
                    centipawn_loss=error_data['centipawn_loss'],
                    error_type=error_data['error_type'],
                    explanation=error_data['description']
                )
                db.session.add(new_error)
                total_errors += 1

            # Mark game as analyzed
            game.analyzed = True
            analyzed_count += 1
            analysis_progress[progress_key]['errors_found'] = total_errors

        # Commit all changes
        db.session.commit()

        # Clear progress
        if progress_key in analysis_progress:
            del analysis_progress[progress_key]

        return jsonify({
            'success': True,
            'analyzed': analyzed_count,
            'errors_found': total_errors,
            'message': f'{analyzed_count} Spiele analysiert, {total_errors} Fehler gefunden!'
        })

    except FileNotFoundError as e:
        return jsonify({
            'success': False,
            'message': 'Stockfish Engine nicht gefunden. Bitte .env Datei konfigurieren.'
        }), 500

    except Exception as e:
        db.session.rollback()
        print(f"Error analyzing games: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'message': f'Fehler bei der Analyse: {str(e)}'
        }), 500


# Database initialization
with app.app_context():
    db.create_all()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
