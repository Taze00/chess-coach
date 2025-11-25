"""
Script to extract tactical patterns from error explanations and update the database.
"""
from app import app, db
from models import Error
import re

# VOLLSTÄNDIGE Liste aller Lichess Puzzle Themes (70+) mit deutschen und englischen Begriffen
TACTICAL_PATTERNS = {
    # === MOTIFS (Basic Tactics) ===
    'fork': ['gabel', 'gabelt', 'fork', 'zwei figuren gleichzeitig'],
    'pin': ['fesselung', 'fesselt', 'gefesselt', 'pin', 'fixiert'],
    'skewer': ['spieß', 'spiess', 'spießt', 'skewer'],
    'discoveredAttack': ['abzugsangriff', 'abzug', 'discovered attack', 'entdeckter angriff'],
    'doubleCheck': ['doppelschach', 'double check'],
    'hangingPiece': ['hängende figur', 'hängend', 'ungedeckt', 'hanging', 'unverteidigt'],
    'trappedPiece': ['gefangene figur', 'eingesperrt', 'trapped', 'gefangen', 'keine fluchtfelder'],
    'exposedKing': ['exponierter könig', 'ungeschützter könig', 'exposed king', 'verwundbarer könig'],
    'attackingF2F7': ['angriff auf f2', 'angriff auf f7', 'f2', 'f7', 'attacking f2', 'attacking f7'],
    'kingsideAttack': ['königsflügel', 'kingside attack', 'angriff königsflügel'],
    'queensideAttack': ['damenflügel', 'queenside attack', 'angriff damenflügel'],
    'advancedPawn': ['vorgerückter bauer', 'advanced pawn', 'freibauer', 'weit vorgerückt'],
    'sacrifice': ['opfer', 'sacrifice', 'geopfert', 'material opfern'],

    # === ADVANCED TACTICS ===
    'attraction': ['hinlenkung', 'attraction', 'anlocken', 'lenken'],
    'deflection': ['ablenkung', 'deflection', 'ablenken'],
    'clearance': ['räumung', 'clearance', 'räumen', 'platz machen'],
    'interference': ['störung', 'interference', 'blockade', 'zwischensetzen'],
    'intermezzo': ['zwischenzug', 'intermezzo', 'intermediate', 'dazwischenzug'],
    'quietMove': ['ruhiger zug', 'quiet move', 'ruhig', 'stiller zug'],
    'xRayAttack': ['röntgenangriff', 'x-ray', 'durchschlag', 'x-ray attack'],
    'zugzwang': ['zugzwang'],
    'defensiveMove': ['verteidigung', 'defensive', 'verteidigen', 'defensive move', 'präzise verteidigung'],
    'captureDefender': ['verteidiger schlagen', 'capture defender', 'verteidigung entfernen'],

    # === CHECKMATE PATTERNS ===
    'mate': ['matt', 'schachmatt', 'mate', 'checkmate'],
    'mateIn1': ['matt in 1', 'matt in einem', 'mate in 1', 'matt in einem zug'],
    'mateIn2': ['matt in 2', 'matt in zwei', 'mate in 2', 'matt in zwei zügen'],
    'mateIn3': ['matt in 3', 'matt in drei', 'mate in 3'],
    'mateIn4': ['matt in 4', 'matt in vier', 'mate in 4'],
    'mateIn5': ['matt in 5', 'matt in fünf', 'mate in 5'],
    'backRankMate': ['grundreihenmatt', 'back rank', 'grundreihe', 'back rank mate'],
    'smotheredMate': ['ersticktes matt', 'smothered mate', 'erstickt'],
    'anastasiaMate': ['anastasias matt', 'anastasia', "anastasia's mate"],
    'arabianMate': ['arabisches matt', 'arabian', 'arabian mate'],
    'doubleBishopMate': ['läuferpaar matt', 'double bishop', 'bodens matt', "boden's mate"],
    'dovetailMate': ['schwalbenschwanz', 'dovetail', 'dovetail mate', 'dame neben könig'],
    'hookMate': ['haken matt', 'hook mate', 'turm springer bauer'],
    'balestraMate': ['balestra matt', 'balestra mate', 'läufer dame matt'],
    'killboxMate': ['kill box', 'killbox mate', 'turm dame 3x3'],
    'triangleMate': ['dreieck matt', 'triangle mate', 'dame turm dreieck'],
    'vukovicMate': ['vukovic matt', 'vukovic mate', 'turm springer'],

    # === SPECIAL MOVES ===
    'castling': ['rochade', 'castling', 'rochieren'],
    'enPassant': ['en passant', 'e.p.', 'schlagen im vorbeigehen'],
    'promotion': ['umwandlung', 'bauernumwandlung', 'promotion'],
    'underPromotion': ['unterverwandlung', 'underpromotion', 'umwandlung springer', 'umwandlung turm'],

    # === GAME PHASE ===
    'opening': ['eröffnung', 'opening'],
    'middlegame': ['mittelspiel', 'middlegame', 'mittelspielphase'],
    'endgame': ['endspiel', 'endgame', 'endspielphase'],
    'rookEndgame': ['turmendspiel', 'rook endgame'],
    'bishopEndgame': ['läuferendspiel', 'bishop endgame'],
    'pawnEndgame': ['bauernendspiel', 'pawn endgame'],
    'knightEndgame': ['springerendspiel', 'knight endgame'],
    'queenEndgame': ['damenendspiel', 'queen endgame'],
    'queenRookEndgame': ['damen-turm-endspiel', 'queen and rook', 'queen rook endgame'],

    # === GOALS ===
    'equality': ['gleichstand', 'equality', 'ausgeglichen', 'remis'],
    'advantage': ['vorteil', 'advantage', 'besser', 'überlegenheit'],
    'crushing': ['vernichtend', 'crushing', 'zerstörend', 'überwältigend'],

    # === PUZZLE LENGTH ===
    'oneMove': ['one move', 'ein zug', 'one-move'],
    'short': ['kurz', 'short', 'zwei züge'],
    'long': ['lang', 'long', 'drei züge'],
    'veryLong': ['sehr lang', 'very long', 'vier züge', 'vier oder mehr'],

    # === ORIGIN ===
    'master': ['meister', 'master', 'titel'],
    'masterVsMaster': ['meister gegen meister', 'master vs master'],
    'superGM': ['super gm', 'supergm', 'weltklasse'],
    'playerGames': ['spieler spiele', 'player games']
}

# Pattern Priorität: Höhere Zahl = spezifischer und wichtiger
PATTERN_PRIORITY = {
    # === HIGH PRIORITY: Spezifische taktische Motive ===
    'mate': 10,
    'mateIn1': 10,
    'mateIn2': 10,
    'mateIn3': 10,
    'mateIn4': 10,
    'mateIn5': 10,
    'fork': 9,
    'pin': 9,
    'skewer': 9,
    'discoveredAttack': 9,
    'doubleCheck': 9,
    'hangingPiece': 9,
    'trappedPiece': 9,
    'exposedKing': 9,

    # === MEDIUM PRIORITY: Fortgeschrittene Taktiken ===
    'backRankMate': 8,
    'smotheredMate': 8,
    'anastasiaMate': 8,
    'arabianMate': 8,
    'doubleBishopMate': 8,
    'dovetailMate': 8,
    'hookMate': 8,
    'balestraMate': 8,
    'killboxMate': 8,
    'triangleMate': 8,
    'vukovicMate': 8,
    'attraction': 7,
    'deflection': 7,
    'clearance': 7,
    'interference': 7,
    'intermezzo': 7,
    'xRayAttack': 7,
    'zugzwang': 7,
    'captureDefender': 7,
    'sacrifice': 7,

    # === MEDIUM-LOW PRIORITY: Spezielle Features ===
    'attackingF2F7': 6,
    'kingsideAttack': 6,
    'queensideAttack': 6,
    'advancedPawn': 6,
    'castling': 6,
    'enPassant': 6,
    'promotion': 6,
    'underPromotion': 6,
    'quietMove': 5,
    'defensiveMove': 5,

    # === LOW PRIORITY: Sehr generische Kategorien (nur als Fallback) ===
    'crushing': 3,
    'opening': 2,
    'middlegame': 2,
    'endgame': 2,
    'rookEndgame': 2,
    'bishopEndgame': 2,
    'pawnEndgame': 2,
    'knightEndgame': 2,
    'queenEndgame': 2,
    'queenRookEndgame': 2,
    'advantage': 1,  # Niedrigste Priorität - nur wenn nichts Spezifischeres gefunden
    'equality': 1,
    'oneMove': 1,
    'short': 1,
    'long': 1,
    'veryLong': 1,
    'master': 1,
    'masterVsMaster': 1,
    'superGM': 1,
    'playerGames': 1
}

def extract_pattern_from_explanation(explanation):
    """
    Extract tactical pattern from German explanation text.
    Returns the MOST SPECIFIC matching pattern (highest priority).
    """
    if not explanation:
        return None

    explanation_lower = explanation.lower()

    # Find ALL matching patterns
    matching_patterns = []

    for pattern_name, keywords in TACTICAL_PATTERNS.items():
        for keyword in keywords:
            if keyword.lower() in explanation_lower:
                priority = PATTERN_PRIORITY.get(pattern_name, 5)
                matching_patterns.append((pattern_name, priority))
                break  # Only count each pattern once

    # Return pattern with HIGHEST priority (most specific)
    if matching_patterns:
        # Sort by priority (descending), then alphabetically for consistency
        matching_patterns.sort(key=lambda x: (-x[1], x[0]))
        return matching_patterns[0][0]

    return None

def extract_all_patterns_from_explanation(explanation):
    """
    Extract ALL tactical patterns from German explanation text.
    Returns a list of patterns sorted by priority (most specific first).
    """
    if not explanation:
        return []

    explanation_lower = explanation.lower()

    # Find ALL matching patterns
    matching_patterns = []

    for pattern_name, keywords in TACTICAL_PATTERNS.items():
        for keyword in keywords:
            if keyword.lower() in explanation_lower:
                priority = PATTERN_PRIORITY.get(pattern_name, 5)
                matching_patterns.append((pattern_name, priority))
                break  # Only count each pattern once

    # Sort by priority (descending), then alphabetically for consistency
    matching_patterns.sort(key=lambda x: (-x[1], x[0]))

    # Return only pattern names (not priorities)
    return [pattern[0] for pattern in matching_patterns]

def update_tactical_patterns():
    """Update tactical_pattern AND tactical_patterns fields for all errors based on their explanations."""
    with app.app_context():
        print("Updating tactical patterns for all errors...")
        import json

        # Get all errors
        errors = Error.query.all()
        total = len(errors)
        updated = 0
        not_found = 0
        multi_pattern_count = 0

        print(f"Found {total} errors to process")

        for i, error in enumerate(errors, 1):
            if i % 50 == 0:
                print(f"Processing {i}/{total}...")

            # Extract ALL patterns from explanation
            patterns = extract_all_patterns_from_explanation(error.explanation)

            if patterns:
                # Set primary pattern (highest priority)
                error.tactical_pattern = patterns[0]

                # Set all patterns as JSON array
                error.tactical_patterns = json.dumps(patterns)

                updated += 1

                # Count errors with multiple patterns
                if len(patterns) > 1:
                    multi_pattern_count += 1
            else:
                not_found += 1
                # Print first 10 unmatched explanations for debugging
                if not_found <= 10:
                    print(f"  No pattern found for: {error.explanation[:100] if error.explanation else 'No explanation'}")

        # Commit changes
        db.session.commit()

        print(f"\n=== Results ===")
        print(f"Total errors: {total}")
        print(f"Patterns found: {updated}")
        print(f"Errors with multiple patterns: {multi_pattern_count}")
        print(f"No pattern found: {not_found}")

        # Show distribution of PRIMARY patterns
        from sqlalchemy import func
        pattern_counts = db.session.query(
            Error.tactical_pattern,
            func.count(Error.id)
        ).group_by(Error.tactical_pattern).order_by(func.count(Error.id).desc()).all()

        print("\n=== Primary Pattern Distribution ===")
        for pattern, count in pattern_counts:
            pattern_name = pattern if pattern else "Unknown"
            print(f"  {pattern_name}: {count}")

        # Show some examples of multi-pattern errors
        print("\n=== Example Multi-Pattern Errors (first 5) ===")
        multi_errors = [e for e in errors if e.tactical_patterns and len(json.loads(e.tactical_patterns)) > 1][:5]
        for error in multi_errors:
            patterns_list = json.loads(error.tactical_patterns)
            print(f"  Error #{error.id}: {patterns_list}")
            print(f"    Explanation: {error.explanation[:80]}...")
            print()

if __name__ == '__main__':
    update_tactical_patterns()
