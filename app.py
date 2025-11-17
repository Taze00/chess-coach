from flask import Flask, render_template, redirect, url_for, request, flash, jsonify, abort, session
from flask_login import LoginManager, login_required, current_user
from dotenv import load_dotenv
import os
import time

from models import db, User, Game
from auth import auth, bcrypt
from chess_api import ChessComAPI
from stockfish_analyzer import StockfishAnalyzer

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


@app.route('/dashboard')
@login_required
def dashboard():
    """Main dashboard for logged-in users."""
    from models import Error

    # Get user statistics
    games_count = Game.query.filter_by(user_id=current_user.id).count()
    errors_count = Error.query.filter_by(user_id=current_user.id).count()

    stats = {
        'games_count': games_count,
        'errors_count': errors_count,
        'puzzles_solved': 0  # Will be populated in Phase 5
    }
    return render_template('dashboard.html', stats=stats)


@app.route('/games')
@login_required
def games():
    """Games list page."""
    # Get all games for current user, ordered by most recent first
    user_games = Game.query.filter_by(user_id=current_user.id).order_by(Game.played_at.desc()).all()
    return render_template('games.html', games=user_games)


@app.route('/errors')
@login_required
def errors():
    """Errors/mistakes overview page."""
    from models import Error

    # Get all errors for current user
    user_errors = Error.query.filter_by(user_id=current_user.id).order_by(Error.created_at.desc()).all()

    # Categorize errors
    categorized = {
        'blunders': [e for e in user_errors if e.error_type == 'blunder'],
        'mistakes': [e for e in user_errors if e.error_type == 'mistake'],
        'inaccuracies': [e for e in user_errors if e.error_type == 'inaccuracy']
    }

    return render_template('errors.html', errors=user_errors, categorized=categorized)


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
    """Training interface page (placeholder)."""
    return render_template('training.html')


@app.route('/progress')
@login_required
def progress():
    """Progress and analytics page (placeholder)."""
    return render_template('progress.html')


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
