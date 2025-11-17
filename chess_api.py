"""
Chess.com API Integration
Handles fetching games from Chess.com public API.
"""
import requests
from datetime import datetime
import chess.pgn
from io import StringIO


class ChessComAPI:
    """Client for Chess.com Public API."""

    BASE_URL = "https://api.chess.com/pub"

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Chess Coach App (https://github.com/Taze00/chess-coach)'
        })

    def get_player(self, username):
        """
        Get player profile information.

        Args:
            username (str): Chess.com username

        Returns:
            dict: Player profile data or None if not found
        """
        url = f"{self.BASE_URL}/player/{username.lower()}"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json()
            return None
        except requests.RequestException as e:
            print(f"Error fetching player: {e}")
            return None

    def get_game_archives(self, username):
        """
        Get list of monthly game archives for a player.

        Args:
            username (str): Chess.com username

        Returns:
            list: URLs to monthly game archives
        """
        url = f"{self.BASE_URL}/player/{username.lower()}/games/archives"
        try:
            response = self.session.get(url, timeout=10)
            if response.status_code == 200:
                return response.json().get('archives', [])
            return []
        except requests.RequestException as e:
            print(f"Error fetching archives: {e}")
            return []

    def get_games_from_archive(self, archive_url):
        """
        Get all games from a specific monthly archive.

        Args:
            archive_url (str): URL to monthly archive

        Returns:
            list: List of game dictionaries
        """
        try:
            response = self.session.get(archive_url, timeout=10)
            if response.status_code == 200:
                return response.json().get('games', [])
            return []
        except requests.RequestException as e:
            print(f"Error fetching games from archive: {e}")
            return []

    def get_recent_games(self, username, limit=20):
        """
        Get the most recent games for a player.

        Args:
            username (str): Chess.com username
            limit (int): Maximum number of games to fetch

        Returns:
            list: List of parsed game data
        """
        archives = self.get_game_archives(username)

        if not archives:
            return []

        # Get games from most recent archives first
        all_games = []
        for archive_url in reversed(archives):
            if len(all_games) >= limit:
                break

            games = self.get_games_from_archive(archive_url)
            all_games.extend(games)

        # Parse and return only the most recent games
        parsed_games = []
        for game in all_games[:limit]:
            parsed_game = self.parse_game(game, username)
            if parsed_game:
                parsed_games.append(parsed_game)

        return parsed_games

    def parse_game(self, game_data, username):
        """
        Parse a game from Chess.com API response.

        Args:
            game_data (dict): Raw game data from API
            username (str): User's username to determine their color

        Returns:
            dict: Parsed game data with relevant fields
        """
        try:
            # Get player color and result
            white_username = game_data['white']['username'].lower()
            black_username = game_data['black']['username'].lower()
            username_lower = username.lower()

            if username_lower == white_username:
                user_color = 'white'
                user_result = game_data['white']['result']
            elif username_lower == black_username:
                user_color = 'black'
                user_result = game_data['black']['result']
            else:
                return None

            # Determine result from user's perspective
            if 'win' in user_result:
                result = 'win'
            elif 'resigned' in user_result or 'checkmated' in user_result or 'timeout' in user_result:
                result = 'loss'
            else:
                result = 'draw'

            # Parse timestamp
            played_at = datetime.fromtimestamp(game_data['end_time'])

            return {
                'pgn': game_data['pgn'],
                'url': game_data['url'],
                'result': result,
                'user_color': user_color,
                'time_control': game_data.get('time_control', 'unknown'),
                'time_class': game_data.get('time_class', 'unknown'),
                'played_at': played_at,
                'white_rating': game_data['white'].get('rating', 0),
                'black_rating': game_data['black'].get('rating', 0),
                'white_username': white_username,
                'black_username': black_username
            }

        except (KeyError, ValueError) as e:
            print(f"Error parsing game: {e}")
            return None

    def validate_username(self, username):
        """
        Check if a Chess.com username exists.

        Args:
            username (str): Chess.com username

        Returns:
            bool: True if user exists, False otherwise
        """
        player = self.get_player(username)
        return player is not None
