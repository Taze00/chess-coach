"""
Stockfish Chess Game Analyzer
Analyzes chess games to find errors (blunders, mistakes, inaccuracies)
"""

import os
import chess
import chess.pgn
from stockfish import Stockfish
from io import StringIO
from typing import List, Dict, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class StockfishAnalyzer:
    """Analyzes chess games using Stockfish engine"""

    # Error thresholds (centipawns)
    BLUNDER_THRESHOLD = 300   # >= 3.00 pawns
    MISTAKE_THRESHOLD = 100   # >= 1.00 pawns
    INACCURACY_THRESHOLD = 50 # >= 0.50 pawns

    def __init__(self, stockfish_path: str = None, depth: int = 15):
        """
        Initialize Stockfish analyzer

        Args:
            stockfish_path: Path to Stockfish executable
            depth: Analysis depth (higher = more accurate but slower)
        """
        if not stockfish_path:
            stockfish_path = os.getenv('STOCKFISH_PATH', 'engines/stockfish/stockfish-windows-x86-64-avx2.exe')

        # Convert to absolute path
        if not os.path.isabs(stockfish_path):
            stockfish_path = os.path.abspath(stockfish_path)

        if not os.path.exists(stockfish_path):
            raise FileNotFoundError(f"Stockfish not found at: {stockfish_path}")

        self.stockfish = Stockfish(
            path=stockfish_path,
            depth=depth,
            parameters={
                "Threads": 2,
                "Hash": 256,
            }
        )
        self.depth = depth

    def analyze_game(self, pgn_string: str, player_color: str) -> List[Dict]:
        """
        Analyze a chess game and find errors

        Args:
            pgn_string: PGN string of the game
            player_color: 'white' or 'black' - which side to analyze

        Returns:
            List of errors found, each containing:
            {
                'move_number': int,
                'fen': str,
                'player_move': str,
                'best_move': str,
                'evaluation_before': float,
                'evaluation_after': float,
                'centipawn_loss': int,
                'error_type': 'blunder' | 'mistake' | 'inaccuracy',
                'description': str
            }
        """
        errors = []

        # Parse PGN
        pgn = StringIO(pgn_string)
        game = chess.pgn.read_game(pgn)

        if not game:
            return errors

        board = game.board()
        prev_eval = 0

        for move_number, move in enumerate(game.mainline_moves(), start=1):
            # Determine if this is the player's move
            is_white_move = board.turn == chess.WHITE
            is_player_move = (player_color == 'white' and is_white_move) or \
                           (player_color == 'black' and not is_white_move)

            if not is_player_move:
                board.push(move)
                continue

            # Get position before move
            fen_before = board.fen()

            # Get best move and evaluation
            self.stockfish.set_fen_position(fen_before)
            best_move = self.stockfish.get_best_move()
            eval_before = self._get_evaluation()

            # Make the actual move
            board.push(move)
            fen_after = board.fen()

            # Get evaluation after move
            self.stockfish.set_fen_position(fen_after)
            eval_after = self._get_evaluation()

            # Calculate centipawn loss
            # Negate if black (Stockfish evaluates from white's perspective)
            if player_color == 'black':
                eval_before = -eval_before
                eval_after = -eval_after

            centipawn_loss = int(eval_before - eval_after)

            # Check if this is an error
            if centipawn_loss >= self.INACCURACY_THRESHOLD:
                error_type = self._classify_error(centipawn_loss)

                error = {
                    'move_number': move_number,
                    'fen': fen_before,
                    'player_move': move.uci(),
                    'best_move': best_move,
                    'evaluation_before': round(eval_before / 100, 2),
                    'evaluation_after': round(eval_after / 100, 2),
                    'centipawn_loss': centipawn_loss,
                    'error_type': error_type,
                    'description': self._generate_description(
                        move_number,
                        move.uci(),
                        best_move,
                        centipawn_loss,
                        error_type,
                        fen_before
                    )
                }
                errors.append(error)

        return errors

    def _get_evaluation(self) -> int:
        """
        Get position evaluation in centipawns
        Returns mate score as very large number
        """
        evaluation = self.stockfish.get_evaluation()

        if evaluation['type'] == 'cp':
            return evaluation['value']
        elif evaluation['type'] == 'mate':
            # Mate in X moves
            mate_in = evaluation['value']
            if mate_in > 0:
                return 10000 - mate_in * 100  # Winning mate
            else:
                return -10000 + mate_in * 100  # Losing mate

        return 0

    def _classify_error(self, centipawn_loss: int) -> str:
        """Classify error based on centipawn loss"""
        if centipawn_loss >= self.BLUNDER_THRESHOLD:
            return 'blunder'
        elif centipawn_loss >= self.MISTAKE_THRESHOLD:
            return 'mistake'
        else:
            return 'inaccuracy'

    def _get_detailed_analysis(self, fen: str) -> Dict:
        """Get detailed analysis including top moves"""
        self.stockfish.set_fen_position(fen)

        # Get top 3 moves
        top_moves = self.stockfish.get_top_moves(3) if hasattr(self.stockfish, 'get_top_moves') else []

        return {
            'best_move': self.stockfish.get_best_move(),
            'evaluation': self._get_evaluation(),
            'top_moves': top_moves
        }

    def _generate_description(
        self,
        move_number: int,
        player_move: str,
        best_move: str,
        centipawn_loss: int,
        error_type: str,
        fen_before: str = None
    ) -> str:
        """Generate detailed human-readable error description with tactical context"""
        error_names = {
            'blunder': 'Grober Fehler',
            'mistake': 'Fehler',
            'inaccuracy': 'Ungenauigkeit'
        }

        # Convert UCI moves to readable format (simplified)
        player_move_readable = self._uci_to_readable(player_move)
        best_move_readable = self._uci_to_readable(best_move)

        loss_in_pawns = centipawn_loss / 100

        # Generate context-aware description
        if error_type == 'blunder':
            if loss_in_pawns > 5:
                context = "Dies könnte Material kosten oder zu einer verlorenen Stellung führen."
            else:
                context = "Dies verschlechtert deine Position deutlich."
        elif error_type == 'mistake':
            context = "Dieser Zug gibt einen Teil deines Vorteils ab."
        else:
            context = "Eine leichte Ungenauigkeit."

        return (
            f"{error_names[error_type]} in Zug {move_number}: "
            f"Du spieltest {player_move_readable}, aber {best_move_readable} wäre besser gewesen. "
            f"{context} Verlust: {loss_in_pawns:.2f} Bauern."
        )

    def _uci_to_readable(self, uci_move: str) -> str:
        """Convert UCI move to more readable format"""
        if not uci_move or len(uci_move) < 4:
            return uci_move

        # Extract squares
        from_sq = uci_move[0:2]
        to_sq = uci_move[2:4]

        # For now, just return UCI notation (we'll enhance this later)
        return f"{from_sq}-{to_sq}"

    def categorize_errors(self, errors: List[Dict]) -> Dict[str, List[Dict]]:
        """
        Categorize errors by opening/middlegame/endgame

        Args:
            errors: List of errors from analyze_game()

        Returns:
            Dictionary with keys 'opening', 'middlegame', 'endgame'
        """
        categorized = {
            'opening': [],
            'middlegame': [],
            'endgame': []
        }

        for error in errors:
            move_num = error['move_number']

            if move_num <= 15:
                categorized['opening'].append(error)
            elif move_num <= 40:
                categorized['middlegame'].append(error)
            else:
                categorized['endgame'].append(error)

        return categorized

    def get_error_statistics(self, errors: List[Dict]) -> Dict:
        """
        Get statistics about errors

        Returns:
            {
                'total': int,
                'blunders': int,
                'mistakes': int,
                'inaccuracies': int,
                'avg_centipawn_loss': float
            }
        """
        if not errors:
            return {
                'total': 0,
                'blunders': 0,
                'mistakes': 0,
                'inaccuracies': 0,
                'avg_centipawn_loss': 0
            }

        stats = {
            'total': len(errors),
            'blunders': sum(1 for e in errors if e['error_type'] == 'blunder'),
            'mistakes': sum(1 for e in errors if e['error_type'] == 'mistake'),
            'inaccuracies': sum(1 for e in errors if e['error_type'] == 'inaccuracy'),
            'avg_centipawn_loss': round(
                sum(e['centipawn_loss'] for e in errors) / len(errors),
                2
            )
        }

        return stats


def test_analyzer():
    """Test the analyzer with a simple game"""
    test_pgn = """
[Event "Test Game"]
[Site "Chess.com"]
[Date "2024.01.01"]
[White "Player1"]
[Black "Player2"]
[Result "1-0"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 7. Bb3 d6
8. c3 O-O 9. h3 Na5 10. Bc2 c5 11. d4 Qc7 1-0
"""

    analyzer = StockfishAnalyzer()
    errors = analyzer.analyze_game(test_pgn, 'white')

    print(f"Found {len(errors)} errors:")
    for error in errors:
        print(f"  - {error['description']}")

    stats = analyzer.get_error_statistics(errors)
    print(f"\nStatistics: {stats}")


if __name__ == '__main__':
    test_analyzer()
