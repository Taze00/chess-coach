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
    position = db.Column(db.String(100), nullable=False)  # FEN string
    move_played = db.Column(db.String(10))
    best_move = db.Column(db.String(10))
    explanation = db.Column(db.Text)
    evaluation_before = db.Column(db.Float)  # Position eval before move
    evaluation_after = db.Column(db.Float)  # Position eval after move
    centipawn_loss = db.Column(db.Integer)  # CP lost by this move
    severity = db.Column(db.Integer)  # 1-10 (deprecated, use centipawn_loss)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

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
