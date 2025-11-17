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
load_dotenv(override=True)


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

    def _get_mate_in(self, fen: str) -> Optional[int]:
        """
        Check if position has mate in X moves
        Returns: positive = we can mate, negative = we get mated, None = no mate
        """
        self.stockfish.set_fen_position(fen)
        evaluation = self.stockfish.get_evaluation()

        if evaluation['type'] == 'mate':
            return evaluation['value']
        return None

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

    def _analyze_tactical_consequences(self, board: chess.Board, move: chess.Move, player_color: chess.Color) -> Dict:
        """
        Analyze what happens after a move by simulating opponent's best response
        Returns tactical consequences including material loss, threats, etc.

        Args:
            board: Current board position
            move: Move to analyze
            player_color: The color of the player we're analyzing (WHITE or BLACK)
        """
        board_after = board.copy()
        board_after.push(move)

        # Get opponent's best response using Stockfish
        self.stockfish.set_fen_position(board_after.fen())
        opponent_response = self.stockfish.get_best_move()

        consequences = {
            'material_loss': 0,
            'pieces_lost': [],
            'pieces_threatened': [],
            'gives_check': board_after.is_check(),
            'opponent_threats': []
        }

        if not opponent_response:
            return consequences

        try:
            response_move = chess.Move.from_uci(opponent_response)

            # Check what tactical threats the opponent creates!
            opponent_patterns = self._detect_tactical_patterns(board_after, response_move)
            if opponent_patterns:
                consequences['opponent_threats'].extend(opponent_patterns)

            # Is it a capture? What gets captured?
            if board_after.is_capture(response_move):
                captured_piece = board_after.piece_at(response_move.to_square)
                # Make sure it's OUR piece that gets captured
                if captured_piece and captured_piece.color == player_color:
                    piece_name = self._get_piece_name(captured_piece)
                    piece_value = self._get_piece_value(captured_piece)
                    consequences['material_loss'] = piece_value
                    consequences['pieces_lost'].append({
                        'name': piece_name,
                        'value': piece_value,
                        'square': chess.square_name(response_move.to_square)
                    })

            # Check for pieces under attack after opponent's response
            board_after_response = board_after.copy()
            board_after_response.push(response_move)

            for square in chess.SQUARES:
                piece = board_after_response.piece_at(square)
                # Check OUR pieces (player_color) that are threatened
                if piece and piece.color == player_color:
                    if board_after_response.is_attacked_by(not player_color, square):
                        attackers = len(board_after_response.attackers(not player_color, square))
                        defenders = len(board_after_response.attackers(player_color, square))
                        if attackers > defenders:
                            consequences['pieces_threatened'].append({
                                'name': self._get_piece_name(piece),
                                'value': self._get_piece_value(piece),
                                'square': chess.square_name(square)
                            })

        except Exception as e:
            print(f"Error in tactical analysis: {e}")

        return consequences

    def _get_piece_value(self, piece) -> int:
        """Get approximate piece value in centipawns"""
        if not piece:
            return 0
        values = {
            chess.PAWN: 100,
            chess.KNIGHT: 300,
            chess.BISHOP: 300,
            chess.ROOK: 500,
            chess.QUEEN: 900,
            chess.KING: 0
        }
        return values.get(piece.piece_type, 0)

    def _detect_tactical_patterns(self, board: chess.Board, move: chess.Move) -> List[str]:
        """
        Detect ALL tactical patterns
        Returns list of detected patterns in German
        """
        patterns = []
        board_after = board.copy()
        board_after.push(move)

        piece = board.piece_at(move.from_square)
        if not piece:
            return patterns

        moved_piece = board_after.piece_at(move.to_square)
        opponent_color = not piece.color

        # 1. GABEL (Fork)
        fork = self._detect_fork(board_after, move.to_square, piece.color)
        if fork:
            patterns.append("Gabel")

        # 2. FESSELUNG (Pin)
        if moved_piece and moved_piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            pin = self._detect_pin(board_after, move.to_square, piece.color)
            if pin:
                patterns.append("Fesselung")

        # 3. SPIESS (Skewer) - ähnlich Pin aber wertvollere Figur vorne
        if moved_piece and moved_piece.piece_type in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            skewer = self._detect_skewer(board_after, move.to_square, piece.color)
            if skewer:
                patterns.append("Spieß")

        # 4. ABZUGSSCHACH (Discovered Check)
        if self._detect_discovered_check(board, move, piece.color):
            patterns.append("Abzugsschach")

        # 5. DOPPELANGRIFF (Double Attack)
        if self._detect_double_attack(board_after, piece.color):
            patterns.append("Doppelangriff")

        # 6. GRUNDREIHENMATT (Back Rank Mate)
        if self._detect_back_rank_mate_threat(board_after, opponent_color):
            patterns.append("Grundreihenmatt-Drohung")

        # 7. ERSTICKTES MATT (Smothered Mate) mit Springer
        if moved_piece and moved_piece.piece_type == chess.KNIGHT:
            if self._detect_smothered_mate_threat(board_after, opponent_color):
                patterns.append("Ersticktes Matt")

        # 8. ABLENKUNG (Deflection) - erkennen wir später über Material-Gewinn

        # 9. LINIENÖFFNUNG (Line Opening)
        if self._detect_line_opening(board, board_after, move, piece.color):
            patterns.append("Linienöffnung")

        # 10. QUALITÄTSOPFER (Exchange Sacrifice)
        if board.is_capture(move):
            if self._detect_exchange_sacrifice(board, move):
                patterns.append("Qualitätsopfer")

        # STRATEGISCHE MUSTER:

        # 11. ROCHADE (Castling) - sehr wichtig!
        if board.is_castling(move):
            patterns.append("Rochade")

        return patterns

    def _detect_fork(self, board: chess.Board, attacker_square: int, attacker_color: chess.Color) -> bool:
        """Detect if piece on attacker_square creates a fork"""
        attacked_pieces = []
        for square in chess.SQUARES:
            target = board.piece_at(square)
            if target and target.color != attacker_color:
                if board.is_attacked_by(attacker_color, square):
                    attacked_pieces.append(target)

        # Fork = attacking 2+ valuable pieces
        valuable = [p for p in attacked_pieces if p.piece_type in [chess.QUEEN, chess.ROOK, chess.KNIGHT, chess.BISHOP]]
        return len(valuable) >= 2

    def _detect_pin(self, board: chess.Board, attacker_square: int, attacker_color: chess.Color) -> bool:
        """
        Detect if a piece on attacker_square is pinning an opponent piece
        Returns True if a pin is detected
        """
        attacker = board.piece_at(attacker_square)
        if not attacker or attacker.piece_type not in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            return False

        # Get all squares attacked by this piece
        attacks = board.attacks(attacker_square)

        for attacked_square in attacks:
            pinned_piece = board.piece_at(attacked_square)

            # Is there an opponent piece here?
            if not pinned_piece or pinned_piece.color == attacker_color:
                continue

            # Check if there's a more valuable piece behind it (same line)
            # For bishops: diagonals, for rooks: files/ranks, for queens: both
            direction = self._get_direction(attacker_square, attacked_square)
            if not direction:
                continue

            # Look further in the same direction
            next_square = attacked_square + direction
            while chess.square_rank(next_square) >= 0 and chess.square_rank(next_square) <= 7:
                if next_square < 0 or next_square > 63:
                    break

                behind_piece = board.piece_at(next_square)
                if behind_piece:
                    # Found a piece behind - is it valuable and same color as pinned piece?
                    if behind_piece.color == pinned_piece.color:
                        # Pin if behind piece is King or more valuable
                        if behind_piece.piece_type == chess.KING:
                            return True  # Absolute pin
                        elif self._get_piece_value(behind_piece) > self._get_piece_value(pinned_piece):
                            return True  # Relative pin
                    break

                next_square += direction

                # Safety: prevent infinite loop
                if abs(next_square - attacked_square) > 7:
                    break

        return False

    def _detect_skewer(self, board: chess.Board, attacker_square: int, attacker_color: chess.Color) -> bool:
        """
        Detect SKEWER - like pin but valuable piece in front
        Returns True if skewer detected
        """
        attacker = board.piece_at(attacker_square)
        if not attacker or attacker.piece_type not in [chess.BISHOP, chess.ROOK, chess.QUEEN]:
            return False

        attacks = board.attacks(attacker_square)

        for attacked_square in attacks:
            front_piece = board.piece_at(attacked_square)

            if not front_piece or front_piece.color == attacker_color:
                continue

            direction = self._get_direction(attacker_square, attacked_square)
            if not direction:
                continue

            # Look behind for less valuable piece
            next_square = attacked_square + direction
            while 0 <= next_square <= 63:
                if chess.square_rank(next_square) < 0 or chess.square_rank(next_square) > 7:
                    break

                behind_piece = board.piece_at(next_square)
                if behind_piece:
                    if behind_piece.color == front_piece.color:
                        # Skewer if FRONT piece is more valuable
                        if self._get_piece_value(front_piece) > self._get_piece_value(behind_piece):
                            return True
                    break

                next_square += direction
                if abs(next_square - attacked_square) > 7:
                    break

        return False

    def _detect_discovered_check(self, board_before: chess.Board, move: chess.Move, mover_color: chess.Color) -> bool:
        """Detect if moving piece reveals check"""
        board_after = board_before.copy()
        board_after.push(move)

        # Is it check after the move?
        if not board_after.is_check():
            return False

        # Was the moved piece NOT giving check directly?
        moved_piece = board_after.piece_at(move.to_square)
        if not moved_piece:
            return False

        # If moved piece doesn't attack king, it's discovered check
        king_square = board_after.king(not mover_color)
        if king_square and not board_after.is_attacked_by(mover_color, king_square):
            return False

        # Check if the moving piece itself attacks the king
        if moved_piece.piece_type == chess.KNIGHT:
            knight_attacks = board_after.attacks(move.to_square)
            if king_square in knight_attacks:
                return False  # Direct check, not discovered

        # It's discovered check if king is in check but not from moved piece directly
        return True

    def _detect_double_attack(self, board: chess.Board, attacker_color: chess.Color) -> bool:
        """
        Detect if 2+ pieces attack the same square (useful for sacrifices)
        """
        opponent_color = not attacker_color

        # Find valuable opponent pieces/squares
        for square in chess.SQUARES:
            target = board.piece_at(square)
            if target and target.color == opponent_color and target.piece_type in [chess.QUEEN, chess.ROOK]:
                attackers = list(board.attackers(attacker_color, square))
                if len(attackers) >= 2:
                    return True

        return False

    def _detect_smothered_mate_threat(self, board: chess.Board, target_color: chess.Color) -> bool:
        """Detect smothered mate pattern (King trapped, Knight gives mate)"""
        king_square = board.king(target_color)
        if king_square is None:
            return False

        # Is king surrounded by own pieces?
        escape_squares = list(board.attacks(king_square))
        trapped = True

        for escape_sq in escape_squares:
            piece_on_escape = board.piece_at(escape_sq)
            if piece_on_escape is None or piece_on_escape.color != target_color:
                trapped = False
                break

        if not trapped:
            return False

        # Is there a knight giving check?
        if board.is_check():
            for square in chess.SQUARES:
                attacker = board.piece_at(square)
                if attacker and attacker.color != target_color and attacker.piece_type == chess.KNIGHT:
                    if board.is_attacked_by(not target_color, king_square):
                        return True

        return False

    def _detect_line_opening(self, board_before: chess.Board, board_after: chess.Board,
                            move: chess.Move, mover_color: chess.Color) -> bool:
        """Detect if move opens a line for rook/bishop/queen"""
        # Did we move away a piece?
        if board_before.is_capture(move):
            return False  # Captures don't count as line opening

        # Check if we opened a file or diagonal
        from_square = move.from_square
        from_file = chess.square_file(from_square)
        from_rank = chess.square_rank(from_square)

        # Look for our rooks/queens on same file/rank
        for square in chess.SQUARES:
            piece = board_after.piece_at(square)
            if not piece or piece.color != mover_color:
                continue

            if piece.piece_type not in [chess.ROOK, chess.QUEEN, chess.BISHOP]:
                continue

            sq_file = chess.square_file(square)
            sq_rank = chess.square_rank(square)

            # Same file/rank/diagonal?
            if sq_file == from_file or sq_rank == from_rank:
                # Check if there's now an attack path
                if len(list(board_after.attacks(square))) > len(list(board_before.attacks(square))):
                    return True

        return False

    def _should_castle(self, board: chess.Board, player_color: chess.Color) -> bool:
        """Check if player should castle (opening phase, king not safe)"""
        # Can player still castle?
        if player_color == chess.WHITE:
            can_castle = board.has_kingside_castling_rights(chess.WHITE) or \
                        board.has_queenside_castling_rights(chess.WHITE)
        else:
            can_castle = board.has_kingside_castling_rights(chess.BLACK) or \
                        board.has_queenside_castling_rights(chess.BLACK)

        if not can_castle:
            return False

        # Is it still opening/early middlegame? (move < 15)
        if board.fullmove_number > 15:
            return False

        # Is king still in center?
        king_square = board.king(player_color)
        if king_square is None:
            return False

        king_file = chess.square_file(king_square)

        # King on e-file = still in center
        if king_file == 4:  # e-file
            return True

        return False

    def _detect_exchange_sacrifice(self, board: chess.Board, move: chess.Move) -> bool:
        """Detect exchange sacrifice (Rook for minor piece)"""
        if not board.is_capture(move):
            return False

        moved_piece = board.piece_at(move.from_square)
        captured_piece = board.piece_at(move.to_square)

        if not moved_piece or not captured_piece:
            return False

        # Rook takes Bishop/Knight?
        if moved_piece.piece_type == chess.ROOK and \
           captured_piece.piece_type in [chess.BISHOP, chess.KNIGHT]:
            return True

        return False

    def _get_direction(self, from_sq: int, to_sq: int) -> Optional[int]:
        """Get direction of movement between two squares"""
        file_diff = chess.square_file(to_sq) - chess.square_file(from_sq)
        rank_diff = chess.square_rank(to_sq) - chess.square_rank(from_sq)

        if file_diff == 0 and rank_diff != 0:
            return 8 if rank_diff > 0 else -8  # Vertical
        elif rank_diff == 0 and file_diff != 0:
            return 1 if file_diff > 0 else -1  # Horizontal
        elif abs(file_diff) == abs(rank_diff):
            # Diagonal
            return (8 if rank_diff > 0 else -8) + (1 if file_diff > 0 else -1)

        return None

    def _detect_back_rank_mate_threat(self, board: chess.Board, target_color: chess.Color) -> bool:
        """Check if there's a back rank mate threat against target_color"""
        # Find the king
        king_square = board.king(target_color)
        if king_square is None:
            return False

        king_rank = chess.square_rank(king_square)

        # Is king on back rank?
        if (target_color == chess.WHITE and king_rank != 0) or \
           (target_color == chess.BLACK and king_rank != 7):
            return False

        # Is king trapped by its own pawns?
        escape_squares = list(board.attacks(king_square))
        can_escape = False

        for escape_sq in escape_squares:
            piece_on_escape = board.piece_at(escape_sq)
            # Can king move there?
            if piece_on_escape is None or piece_on_escape.color != target_color:
                if not board.is_attacked_by(not target_color, escape_sq):
                    can_escape = True
                    break

        if can_escape:
            return False

        # Is there a rook/queen attacking the back rank?
        for square in chess.SQUARES:
            attacker = board.piece_at(square)
            if attacker and attacker.color != target_color:
                if attacker.piece_type in [chess.ROOK, chess.QUEEN]:
                    if board.is_attacked_by(not target_color, king_square):
                        return True

        return False

    def _generate_description(
        self,
        move_number: int,
        player_move: str,
        best_move: str,
        centipawn_loss: int,
        error_type: str,
        fen_before: str = None
    ) -> str:
        """Generate detailed tactical explanation with concrete analysis"""
        loss_in_pawns = centipawn_loss / 100

        if not fen_before:
            return f"Dieser Zug verschlechtert deine Position um {loss_in_pawns:.1f} Bauern."

        board = chess.Board(fen_before)

        try:
            player_move_obj = chess.Move.from_uci(player_move)
            best_move_obj = chess.Move.from_uci(best_move)

            # Determine player color
            player_color = board.turn

            # Convert UCI to readable notation
            player_move_readable = self._uci_to_readable(board, player_move)
            best_move_readable = self._uci_to_readable(board, best_move)

            piece_moved = board.piece_at(player_move_obj.from_square)
            piece_name = self._get_piece_name(piece_moved)

            # Analyze what happens after YOUR move
            your_consequences = self._analyze_tactical_consequences(board, player_move_obj, player_color)

            # Analyze what happens after BEST move
            best_consequences = self._analyze_tactical_consequences(board, best_move_obj, player_color)

            # Detect tactical patterns in best move
            best_patterns = self._detect_tactical_patterns(board, best_move_obj)

            # Check for missed mate
            mate_before = self._get_mate_in(fen_before)
            missed_mate = None
            if mate_before and mate_before > 0 and mate_before <= 3:
                # You had mate in X!
                missed_mate = mate_before

            # Check for strategic issues
            should_castle = self._should_castle(board, player_color)
            missed_castle = should_castle and not board.is_castling(player_move_obj)

            # Build explanation based on concrete analysis
            explanation_parts = []

            # CRITICAL: Did you miss mate?
            if missed_mate:
                explanation_parts.append(
                    f"<strong>KRITISCH!</strong> Du hattest Matt in {missed_mate} {'Zug' if missed_mate == 1 else 'Zügen'}! "
                    f"Der Zug <strong>{player_move_readable}</strong> lässt diese Chance aus."
                )
            # Important: Should you have castled?
            elif missed_castle and centipawn_loss >= 50:
                if "Rochade" in best_patterns:
                    explanation_parts.append(
                        f"Dein König steht unsicher! Der Zug <strong>{player_move_readable}</strong> lässt ihn im Zentrum."
                    )

            # What's wrong with your move?
            if your_consequences['material_loss'] > 0:
                lost_pieces = your_consequences['pieces_lost']
                if lost_pieces:
                    lost = lost_pieces[0]
                    # Check what tactical pattern causes the loss
                    if 'Gabel' in your_consequences['opponent_threats']:
                        explanation_parts.append(
                            f"Nach deinem Zug <strong>{player_move_readable}</strong> kann der Gegner eine Gabel machen und deinen {lost['name']} gewinnen."
                        )
                    elif 'Fesselung' in your_consequences['opponent_threats']:
                        explanation_parts.append(
                            f"Nach <strong>{player_move_readable}</strong> kann der Gegner deinen {lost['name']} fesseln und ihn dann gewinnen."
                        )
                    elif 'Grundreihenmatt-Drohung' in your_consequences['opponent_threats']:
                        explanation_parts.append(
                            f"Nach <strong>{player_move_readable}</strong> droht Grundreihenmatt! Du verlierst deinen {lost['name']} oder wirst matt gesetzt."
                        )
                    else:
                        explanation_parts.append(
                            f"Nach deinem Zug <strong>{player_move_readable}</strong> verlierst du deinen {lost['name']} auf {lost['square']}. "
                            f"Der Gegner kann ihn einfach schlagen."
                        )
            elif your_consequences['opponent_threats']:
                # Tactical threat but no immediate capture
                threat = your_consequences['opponent_threats'][0]
                threat_messages = {
                    'Gabel': f"Nach <strong>{player_move_readable}</strong> kann der Gegner eine Gabel machen und Material gewinnen.",
                    'Fesselung': f"Nach <strong>{player_move_readable}</strong> kann der Gegner eine wichtige Figur fesseln.",
                    'Spieß': f"Nach <strong>{player_move_readable}</strong> kann der Gegner einen Spieß machen.",
                    'Grundreihenmatt-Drohung': f"Nach <strong>{player_move_readable}</strong> droht der Gegner Grundreihenmatt!",
                    'Ersticktes Matt': f"Nach <strong>{player_move_readable}</strong> droht ersticktes Matt!",
                    'Abzugsschach': f"Nach <strong>{player_move_readable}</strong> kann der Gegner Abzugsschach geben.",
                    'Doppelangriff': f"Nach <strong>{player_move_readable}</strong> kann der Gegner einen Doppelangriff starten."
                }
                explanation_parts.append(threat_messages.get(threat,
                    f"Nach <strong>{player_move_readable}</strong> hat der Gegner eine starke taktische Drohung."))
            elif your_consequences['pieces_threatened']:
                threatened = your_consequences['pieces_threatened'][0]
                explanation_parts.append(
                    f"Nach <strong>{player_move_readable}</strong> steht dein {threatened['name']} auf {threatened['square']} ungedeckt und wird angegriffen."
                )
            else:
                # No immediate material loss - it's positional
                explanation_parts.append(
                    f"Der Zug <strong>{player_move_readable}</strong> schwächt deine Stellung erheblich."
                )

            # Why is the best move better?
            best_reasons = []

            if best_patterns:
                # Translate tactical patterns to German explanations
                pattern_translations = {
                    "Gabel": "macht eine Gabel",
                    "Fesselung": "fesselt eine gegnerische Figur",
                    "Spieß": "macht einen Spieß",
                    "Grundreihenmatt-Drohung": "droht Grundreihenmatt",
                    "Ersticktes Matt": "droht ersticktes Matt",
                    "Abzugsschach": "gibt Abzugsschach",
                    "Doppelangriff": "macht einen Doppelangriff",
                    "Linienöffnung": "öffnet eine wichtige Linie",
                    "Qualitätsopfer": "opfert die Qualität für Angriff",
                    "Rochade": "bringt den König in Sicherheit"
                }
                for pattern in best_patterns:
                    translation = pattern_translations.get(pattern)
                    if translation:
                        best_reasons.append(translation)

            if board.is_capture(best_move_obj):
                captured = board.piece_at(best_move_obj.to_square)
                if captured:
                    best_reasons.append(f"gewinnt einen {self._get_piece_name(captured)}")

            board_after_best = board.copy()
            board_after_best.push(best_move_obj)
            if board_after_best.is_check():
                best_reasons.append("gibt Schach")

            if not best_reasons:
                best_reasons.append("hält deine Position stabil")

            explanation_parts.append(
                f"Besser wäre <strong>{best_move_readable}</strong> gewesen, das {' und '.join(best_reasons)}."
            )

            # Add severity
            if centipawn_loss >= 300:
                explanation_parts.append(f"Das ist ein grober Fehler (Verlust: {loss_in_pawns:.1f} Bauern).")
            else:
                explanation_parts.append(f"Verlust: {loss_in_pawns:.1f} Bauern.")

            return " ".join(explanation_parts)

        except Exception as e:
            print(f"Error generating description: {e}")
            return f"Fehler in Zug {move_number}. Verlust: {loss_in_pawns:.1f} Bauern."

    def _get_piece_name(self, piece):
        """Get German piece name"""
        if not piece:
            return "Figur"
        names = {
            chess.PAWN: "Bauer",
            chess.KNIGHT: "Springer",
            chess.BISHOP: "Läufer",
            chess.ROOK: "Turm",
            chess.QUEEN: "Dame",
            chess.KING: "König"
        }
        return names.get(piece.piece_type, "Figur")

    def _uci_to_readable(self, board: chess.Board, uci_move: str) -> str:
        """Convert UCI move to readable chess notation (e.g., e4, Sf3, O-O)"""
        if not uci_move or len(uci_move) < 4:
            return uci_move

        try:
            move = chess.Move.from_uci(uci_move)

            # Check for castling
            if board.is_castling(move):
                # Kingside (short) castling
                if move.to_square > move.from_square:
                    return "O-O"
                # Queenside (long) castling
                else:
                    return "O-O-O"

            piece = board.piece_at(move.from_square)
            if not piece:
                return uci_move

            # Get piece symbol (empty for pawns)
            piece_symbols = {
                chess.KNIGHT: 'S',  # Springer
                chess.BISHOP: 'L',  # Läufer
                chess.ROOK: 'T',    # Turm
                chess.QUEEN: 'D',   # Dame
                chess.KING: 'K'     # König
            }

            piece_symbol = piece_symbols.get(piece.piece_type, '')

            # Get target square
            to_square = chess.square_name(move.to_square)

            # Check if it's a capture
            is_capture = board.is_capture(move)
            capture_symbol = 'x' if is_capture else ''

            # For pawn moves, include file if it's a capture
            if piece.piece_type == chess.PAWN:
                if is_capture:
                    from_file = chess.square_name(move.from_square)[0]
                    return f"{from_file}{capture_symbol}{to_square}"
                else:
                    return to_square

            # For other pieces: Just piece symbol + capture + square (no piece name)
            result = f"{piece_symbol}{capture_symbol}{to_square}"
            return result

        except Exception as e:
            print(f"Error converting UCI to readable: {e}")
            return uci_move

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
