# ♟️ Chess Coach - Dein personalisierter Schach-Trainer

Ein Web-Tool das deine Chess.com Spiele analysiert, deine häufigsten Fehler findet, und dir Taktikaufgaben gibt die GENAU diese Fehler trainieren.

**🎯 Ziel:** Messbare ELO-Verbesserung durch personalisiertes, fehler-fokussiertes Training.

---

## 💡 Das Problem

- Du übst seit Jahren Schach
- Du machst tausende Taktikaufgaben
- Du analysierst deine Spiele auf Chess.com
- **Aber:** Du machst dieselben Fehler immer wieder

**Warum?** Weil generische Taktikaufgaben nicht DEINE Schwächen treffen.

---

## ✨ Die Lösung

Chess Coach macht 3 Dinge anders:

### 1. 🔍 Analyse DEINER Spiele
- Importiert automatisch von Chess.com
- Analysiert mit Stockfish
- Findet deine häufigsten Fehler
- "Du lässt in 60% der Spiele Figuren ungeschützt!"

### 2. 🎯 Training deiner Schwächen
- Filtert Lichess-Puzzles nach DEINEN Fehlertypen
- Keine generischen Aufgaben
- Nur Puzzles die dein Problem lösen
- Spaced Repetition: Schwächen häufiger üben

### 3. 🎓 Coach-Feedback
- Erklärt jeden Zug laien-freundlich
- "Das hast DU in Spiel #42 falsch gemacht!"
- Zeigt Fortschritt: "7 Spiele ohne diesen Fehler! 🎉"
- Motiviert durch positive Verstärkung

---

## 🚀 Features

### ✅ Geplant für MVP
- [x] User Authentication
- [ ] Chess.com Spiele Import
- [ ] Stockfish Fehler-Analyse
- [ ] Fehler-Kategorisierung (Hanging Piece, Fork, Pin, etc.)
- [ ] Lichess Puzzle Integration (3M+ Puzzles)
- [ ] Training Interface mit interaktivem Schachbrett
- [ ] Coach-Feedback System
- [ ] Fortschritts-Tracking & Charts
- [ ] Dashboard mit Stats

### 🔜 Kommende Features
- [ ] Adaptiver Bot der deine Schwächen testet
- [ ] Weekly Progress Reports
- [ ] Achievements & Badges
- [ ] Gegner-Analyse Tool (Spionage)

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- Flask
- SQLAlchemy
- Stockfish Engine
- python-chess

**Frontend:**
- Bootstrap 5
- Vanilla JavaScript
- ChessboardJS
- Chart.js

**Datenquellen:**
- Chess.com Public API
- Lichess Puzzle Database
- Stockfish Analysis

---

## 📦 Installation

### Voraussetzungen
- Python 3.12+
- Git
- [Stockfish](https://stockfishchess.org/download/) (Chess Engine)

### Setup

```bash
# Repository klonen
git clone https://github.com/Taze00/chess-coach.git
cd chess-coach

# Virtual Environment erstellen
python -m venv venv

# Aktivieren
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate     # Windows

# Dependencies installieren
pip install -r requirements.txt

# Environment Variables setzen
cp .env.example .env
# Editiere .env und setze:
# - SECRET_KEY
# - DATABASE_URL
# - STOCKFISH_PATH

# Datenbank initialisieren
python
>>> from app import db
>>> db.create_all()
>>> exit()

# App starten
python app.py
```

Öffne Browser: http://localhost:5000

---

## 🎮 Usage

### 1. Account erstellen
- Registriere dich mit Email und Passwort
- Verknüpfe deinen Chess.com Username

### 2. Spiele importieren
- Klicke "Spiele importieren" im Dashboard
- Warte 5-10 Sekunden
- Deine letzten Spiele werden geladen

### 3. Analyse starten
- Klicke "Spiele analysieren"
- Stockfish findet deine Fehler
- Dashboard zeigt deine Hauptschwächen

### 4. Training beginnen
- Klicke "Training starten"
- Löse Puzzles die DEINE Fehler trainieren
- Erhalte Coach-Feedback
- Tracke deinen Fortschritt

---

## 📊 Wie funktioniert die Analyse?

```python
1. Import von Chess.com
   ↓
2. Stockfish analysiert jeden Zug
   ↓
3. Eval-Drops > 2.0 Pawns = Blunder
   ↓
4. Fehler kategorisieren:
   - Hanging Piece (Figur ungeschützt)
   - Fork missed (Gabel übersehen)
   - Pin missed (Fesselung übersehen)
   - Mate missed (Matt übersehen)
   - etc.
   ↓
5. Hauptschwäche finden: z.B. "Hanging Pieces 60%"
   ↓
6. Lichess Puzzles filtern nach Theme: "hangingPiece"
   ↓
7. User löst Puzzles → Fortschritt tracken
   ↓
8. Neue Spiele analysieren → Verbesserung sichtbar!
```

---

## 📁 Projekt-Struktur

```
chess-coach/
├── app.py                 # Main Flask App
├── models.py              # Database Models
├── auth.py                # Authentication
├── chess_api.py           # Chess.com Integration
├── stockfish_analyzer.py  # Stockfish Analysis
├── puzzle_matcher.py      # Lichess Puzzle Matching
│
├── templates/
│   ├── base.html         # Base Layout
│   ├── index.html        # Landing Page
│   ├── dashboard.html    # Main Dashboard
│   ├── games.html        # Games List
│   ├── training.html     # Puzzle Interface
│   └── progress.html     # Stats & Charts
│
├── static/
│   ├── css/
│   ├── js/
│   └── images/
│
├── docs/
│   ├── ROADMAP.md        # Development Plan
│   ├── ARCHITECTURE.md   # Tech Details
│   ├── CONTEXT.md        # Context for new sessions
│   └── TODO.md           # Next Steps
│
├── requirements.txt
├── .env
└── .gitignore
```

---

## 🗺️ Roadmap

### Phase 1: Foundation ✅ (Completed)
- User Authentication
- Basic UI
- Database Setup

### Phase 2: Chess.com Integration 🚧 (In Progress)
- Spiele Import
- PGN Parsing
- Games Liste

### Phase 3: Stockfish Analysis 📋 (Planned)
- Error Detection
- Categorization
- Dashboard Stats

### Phase 4: Puzzle Training 📋 (Planned)
- Lichess Integration
- Training Interface
- Coach Feedback

### Phase 5: Analytics 📋 (Planned)
- Progress Tracking
- Charts & Graphs
- Achievements

### Phase 6: Bot 🔮 (Future)
- Adaptive Bot
- Weakness Testing
- Post-Game Analysis

Siehe [ROADMAP.md](docs/ROADMAP.md) für Details.

---

## 🤝 Contributing

Contributions sind willkommen! Bitte:

1. Fork das Repo
2. Erstelle einen Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit deine Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push zum Branch (`git push origin feature/AmazingFeature`)
5. Öffne einen Pull Request

---

## 📝 Dokumentation

- **[ROADMAP.md](docs/ROADMAP.md)** - Kompletter Entwicklungsplan
- **[CONTEXT.md](docs/CONTEXT.md)** - Projekt-Kontext für neue Sessions
- **[TODO.md](docs/TODO.md)** - Nächste Steps
- **[ARCHITECTURE.md](docs/ARCHITECTURE.md)** - Technische Details

---

## 📄 License

Dieses Projekt ist aktuell **privat** und nicht für kommerzielle Nutzung ohne Erlaubnis.

Eine Open-Source Lizenz wird möglicherweise später hinzugefügt.

---

## 👤 Autor

**Alex**
- Chess.com: [FirstRulesChess](https://www.chess.com/member/FirstRulesChess) (falls öffentlich)
- GitHub: [@Taze00](https://github.com/Taze00)

---

## 🙏 Credits

- [Stockfish](https://stockfishchess.org/) - Beste Open-Source Chess Engine
- [Lichess](https://lichess.org/) - Puzzle Database
- [Chess.com](https://www.chess.com/) - Game Data via Public API
- [python-chess](https://python-chess.readthedocs.io/) - Chess Logic
- [ChessboardJS](https://chessboardjs.com/) - Interactive Chessboard

---

## 📊 Stats

![Phase](https://img.shields.io/badge/Phase-1%20Complete-green)
![Status](https://img.shields.io/badge/Status-In%20Development-yellow)
![Python](https://img.shields.io/badge/Python-3.12+-blue)
![License](https://img.shields.io/badge/License-Private-red)

---

## 💬 Support

Fragen oder Feedback? Öffne ein [Issue](https://github.com/Taze00/chess-coach/issues)!

---

**Happy Chess Improving! ♟️**
