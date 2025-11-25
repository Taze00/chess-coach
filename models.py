"""
Database models for Chess Coach application.
"""
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime

db = SQLAlchemy()


class User(UserMixin, db.Model):
    """User account model."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    chesscom_username = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    games = db.relationship('Game', backref='user', lazy=True, cascade='all, delete-orphan')
    errors = db.relationship('Error', backref='user', lazy=True, cascade='all, delete-orphan')
    puzzle_progress = db.relationship('PuzzleProgress', backref='user', lazy=True, cascade='all, delete-orphan')
    error_stats = db.relationship('ErrorStats', backref='user', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.email}>'


class Game(db.Model):
    """Chess game imported from Chess.com."""
    __tablename__ = 'games'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    pgn = db.Column(db.Text, nullable=False)
    result = db.Column(db.String(20))  # 'win', 'loss', 'draw'
    played_at = db.Column(db.DateTime)
    analyzed = db.Column(db.Boolean, default=False)
    chesscom_url = db.Column(db.String(200), unique=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Relationships
    errors = db.relationship('Error', backref='game', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Game {self.id} - {self.result}>'


class Error(db.Model):
    """Chess error found by Stockfish analysis."""
    __tablename__ = 'errors'

    id = db.Column(db.Integer, primary_key=True)
    game_id = db.Column(db.Integer, db.ForeignKey('games.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    move_number = db.Column(db.Integer)  # Which move number
    error_type = db.Column(db.String(50), nullable=False)  # 'blunder', 'mistake', 'inaccuracy'
    tactical_pattern = db.Column(db.String(50))  # 'fork', 'pin', 'hangingPiece', 'mate', etc. (deprecated - use tactical_patterns)
    tactical_patterns = db.Column(db.Text)  # JSON array of patterns: ["fork", "mate", "advantage"]
    position = db.Column(db.String(100), nullable=False)  # FEN string
    move_played = db.Column(db.String(10))
    best_move = db.Column(db.String(10))
    explanation = db.Column(db.Text)
    evaluation_before = db.Column(db.Float)  # Position eval before move
    evaluation_after = db.Column(db.Float)  # Position eval after move
    centipawn_loss = db.Column(db.Integer)  # CP lost by this move
    severity = db.Column(db.Integer)  # 1-10 (deprecated, use centipawn_loss)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def get_tactical_patterns_list(self):
        """Return tactical patterns as a Python list."""
        if not self.tactical_patterns:
            return []
        import json
        try:
            return json.loads(self.tactical_patterns)
        except:
            return []

    def get_primary_pattern(self):
        """Return the most important (first) tactical pattern."""
        patterns = self.get_tactical_patterns_list()
        return patterns[0] if patterns else self.tactical_pattern

    def __repr__(self):
        return f'<Error {self.error_type} in Game {self.game_id}>'


class PuzzleProgress(db.Model):
    """User progress on Lichess puzzles."""
    __tablename__ = 'puzzle_progress'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    puzzle_id = db.Column(db.String(50), nullable=False)
    error_type = db.Column(db.String(50))  # Which error type is this training?
    attempts = db.Column(db.Integer, default=0)
    solved = db.Column(db.Boolean, default=False)
    last_attempt = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<PuzzleProgress {self.puzzle_id} - Solved: {self.solved}>'


class ErrorStats(db.Model):
    """Weekly aggregated error statistics for progress tracking."""
    __tablename__ = 'error_stats'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    error_type = db.Column(db.String(50), nullable=False)
    week = db.Column(db.String(10), nullable=False)  # Format: 'YYYY-WW'
    count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<ErrorStats {self.error_type} - Week {self.week}>'


class Puzzle(db.Model):
    """Lichess puzzle for training."""
    __tablename__ = 'puzzles'

    id = db.Column(db.Integer, primary_key=True)
    puzzle_id = db.Column(db.String(50), unique=True, nullable=False)  # Lichess puzzle ID
    fen = db.Column(db.String(100), nullable=False)  # Starting position
    moves = db.Column(db.String(200), nullable=False)  # Solution moves (UCI format)
    rating = db.Column(db.Integer)  # Puzzle difficulty rating
    rating_deviation = db.Column(db.Integer)
    popularity = db.Column(db.Integer)
    nb_plays = db.Column(db.Integer)
    themes = db.Column(db.String(200))  # Comma-separated themes (e.g., "fork,pin")
    game_url = db.Column(db.String(200))
    opening_tags = db.Column(db.String(200))  # Opening information
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Puzzle {self.puzzle_id} - Rating {self.rating}>'

    def get_themes_list(self):
        """Return themes as a list."""
        if not self.themes:
            return []
        # Lichess uses spaces to separate themes
        return [t.strip() for t in self.themes.split(' ') if t.strip()]
