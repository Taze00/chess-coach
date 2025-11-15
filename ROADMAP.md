# 🗺️ CHESS COACH - DEVELOPMENT ROADMAP

## Vision

**Ein personalisierter Schach-Trainer der echte Fehler analysiert und gezielt trainiert.**

**Kernproblem:** Spieler üben seit Jahren, machen aber dieselben Fehler immer wieder. Generische Taktikaufgaben bringen nichts, weil sie nicht die individuellen Schwächen treffen.

**Unsere Lösung:**
1. ✅ Chess.com Spiele automatisch importieren
2. ✅ Mit Stockfish individuelle Fehler finden  
3. ✅ Fehler laien-freundlich kategorisieren
4. ✅ Lichess-Puzzles geben die GENAU diese Fehler trainieren
5. ✅ Wie ein Coach Züge erklären
6. ✅ Fortschritt sichtbar machen
7. 🔜 (Später) Als adaptiver Bot testen

---

## 🎯 Core Features

### Must-Have Features
- [x] User Authentication (Login/Register)
- [ ] Chess.com Spiele Import
- [ ] Stockfish Fehler-Analyse
- [ ] Fehler-Kategorisierung (Hanging Piece, Fork, Pin, etc.)
- [ ] Lichess Puzzle Integration
- [ ] Training Interface mit Coach-Feedback
- [ ] Fortschritts-Tracking
- [ ] Dashboard mit Stats

### Nice-to-Have Features
- [ ] Spaced Repetition für Fehlertypen
- [ ] Achievements & Badges
- [ ] Weekly Progress Reports
- [ ] Fehler-Heatmap (Eröffnung/Mittelspiel/Endspiel)
- [ ] Pre-Game Warm-up Puzzles

### Future Features
- [ ] Adaptiver Bot zum Spielen
- [ ] Gegner-Analyse Tool (Spionage)
- [ ] Mobile App
- [ ] Abo-Modell / Monetarisierung

---

## 🛠️ Tech Stack

### Backend
- **Framework:** Flask (Python)
- **Database:** SQLite (dev) → PostgreSQL (production)
- **ORM:** SQLAlchemy
- **Auth:** Flask-Login + bcrypt

### Frontend
- **UI Framework:** Bootstrap 5
- **JavaScript:** Vanilla JS (später React optional)
- **Chessboard:** ChessboardJS + chess.js
- **Charts:** Chart.js

### Chess Tools
- **Game Analysis:** Stockfish Engine
- **Board Logic:** python-chess
- **Puzzles:** Lichess Puzzle Database (3M+ kostenlos)
- **Game Import:** Chess.com Public API

### Deployment (später)
- **Hosting:** Railway / Render / Heroku
- **CI/CD:** GitHub Actions
- **Domain:** Custom domain mit SSL

---

## 📋 Development Phases

### **Phase 1: Foundation** ⏱️ 1-2 Wochen
**Ziel:** Basic App mit Login läuft

#### Tasks:
- [ ] Flask App Setup
  - [ ] Projekt-Struktur erstellen
  - [ ] Virtual Environment
  - [ ] requirements.txt
- [ ] Database Setup
  - [ ] SQLAlchemy Models:
    - [ ] User (email, password_hash, chesscom_username)
    - [ ] Game (pgn, result, played_at, analyzed)
    - [ ] Error (game_id, error_type, position, move, explanation)
    - [ ] PuzzleProgress (puzzle_id, solved, attempts)
  - [ ] Migrations Setup
- [ ] User Authentication
  - [ ] Registration Form
  - [ ] Login System
  - [ ] Password Hashing (bcrypt)
  - [ ] Session Management
  - [ ] Logout
- [ ] Basic UI
  - [ ] Landing Page
  - [ ] Login/Register Pages
  - [ ] Dashboard (empty)
  - [ ] Navbar mit Navigation
  - [ ] Footer
- [ ] Settings Page
  - [ ] Profile editing
  - [ ] Chess.com username

**Deliverable:** User kann Account erstellen, einloggen, leeres Dashboard sehen

**Success Criteria:**
- ✅ User Registration funktioniert
- ✅ Login/Logout funktioniert
- ✅ Dashboard ist erreichbar
- ✅ Design ist clean und minimalistisch

---

### **Phase 2: Chess.com Integration** ⏱️ 1 Woche
**Ziel:** Spiele automatisch importieren

#### Tasks:
- [ ] Chess.com API Research
  - [ ] Public API Endpoints verstehen
  - [ ] Rate Limits checken
  - [ ] PGN Format studieren
- [ ] Import Funktion Backend
  - [ ] API Client erstellen
  - [ ] Endpoint: `/pub/player/{username}/games/archives`
  - [ ] PGN parsen mit python-chess
  - [ ] Games in DB speichern
  - [ ] Duplikats-Check (keine doppelten Importe)
- [ ] Import Funktion Frontend
  - [ ] "Spiele importieren" Button
  - [ ] Loading State / Progress Bar
  - [ ] Success/Error Messages
  - [ ] "12 neue Spiele importiert!" Feedback
- [ ] Spiele-Liste UI
  - [ ] Tabelle: Datum, Gegner, Ergebnis
  - [ ] Filter: Datum / Ergebnis / Analysiert
  - [ ] Link zu Chess.com Original
  - [ ] Pagination (bei vielen Spielen)

**Deliverable:** User kann Chess.com Spiele importieren und sehen

**Success Criteria:**
- ✅ Import funktioniert zuverlässig
- ✅ Keine Duplikate
- ✅ PGN wird korrekt gespeichert
- ✅ Liste zeigt alle Spiele an

---

### **Phase 3: Stockfish Analyse** ⏱️ 2 Wochen
**Ziel:** Fehler automatisch finden und kategorisieren

#### Tasks:
- [ ] Stockfish Setup
  - [ ] Lokal installieren (Windows/Mac/Linux)
  - [ ] python-chess Engine Integration
  - [ ] Engine Communication testen
  - [ ] Performance Tuning (Depth, Time)
- [ ] Analyse-Algorithmus
  - [ ] PGN → Board States konvertieren
  - [ ] Jeden Zug evaluieren (Stockfish)
  - [ ] Eval-Drops erkennen (Blunders)
  - [ ] Threshold: -2.0 Pawns = Fehler
  - [ ] Best Move finden
  - [ ] Position (FEN) speichern
- [ ] Fehler-Kategorisierung 🧠
  - [ ] **Hanging Piece:** Material-Verlust durch ungeschützte Figur
  - [ ] **Fork missed:** Gabel übersehen
  - [ ] **Pin missed:** Fesselung nicht erkannt
  - [ ] **Mate missed:** Matt in X übersehen
  - [ ] **Checkmate:** Matt verpasst
  - [ ] **Defensive mistake:** Eigene Figur bedroht
  - [ ] **Endgame mistake:** Endspiel-Fehler
- [ ] Erklärungen generieren
  - [ ] Layman-freundliche Texte
  - [ ] Template-System:
    - "Du hast deinen {piece} ungeschützt gelassen"
    - "Dein Gegner konnte mit {move} Material gewinnen"
  - [ ] Severity Score (1-10)
- [ ] Error Storage
  - [ ] Errors in DB speichern
  - [ ] Link zu Game
  - [ ] FEN Position
  - [ ] Move Played vs Best Move
- [ ] Dashboard Stats
  - [ ] Total Errors anzeigen
  - [ ] Fehlertypen aggregieren
  - [ ] "Hauptschwäche: Hanging Pieces (60%)"
  - [ ] Top 3 Fehlertypen
- [ ] Spiel-Detail-Ansicht
  - [ ] Liste aller Fehler eines Spiels
  - [ ] Chessboard mit Position
  - [ ] Erklärung anzeigen
  - [ ] "Dein Zug" vs "Best Move"

**Deliverable:** User sieht analysierte Fehler mit Kategorien und Erklärungen

**Success Criteria:**
- ✅ Stockfish findet relevante Fehler (keine False Positives)
- ✅ Kategorisierung ist akkurat
- ✅ Erklärungen sind verständlich
- ✅ Dashboard zeigt sinnvolle Stats

---

### **Phase 4: Lichess Puzzle Integration** ⏱️ 1 Woche
**Ziel:** Puzzle-Datenbank verfügbar machen

#### Tasks:
- [ ] Lichess Puzzle DB Download
  - [ ] CSV herunterladen (3M+ Puzzles)
  - [ ] Format verstehen: PuzzleId, FEN, Moves, Rating, Themes
  - [ ] Beispiel-Puzzles testen
- [ ] Puzzle Import
  - [ ] Neue Tabelle: Puzzles (id, fen, moves, rating, themes)
  - [ ] CSV → SQLite Import Script
  - [ ] ODER: Direct CSV Reading (schneller)
  - [ ] Indizes auf Themes erstellen
- [ ] Puzzle-Matching Algorithmus
  ```python
  1. User's Hauptschwäche finden (z.B. "hanging_piece")
  2. Lichess Themes mappen:
     - hanging_piece → "hangingPiece"
     - fork_missed → "fork"
     - pin_missed → "pin"
  3. Puzzles mit Theme filtern
  4. Rating ±200 vom User (später ELO-Tracking)
  5. Sortieren nach Popularität
  6. Top 10 zurückgeben
  ```
- [ ] API Endpoints
  - [ ] `/api/get-next-puzzle` - Nächstes Puzzle
  - [ ] `/api/submit-puzzle` - Lösung einreichen
  - [ ] `/api/puzzle-stats` - User's Puzzle Stats
- [ ] Progress Tracking
  - [ ] Welche Puzzles wurden gezeigt?
  - [ ] Welche gelöst?
  - [ ] Success Rate pro Fehlertyp

**Deliverable:** Backend kann passende Puzzles liefern

**Success Criteria:**
- ✅ Puzzles matchen User's Fehlertypen
- ✅ Keine Wiederholungen (kurz nacheinander)
- ✅ Rating passt zu User-Level
- ✅ API ist schnell (<500ms)

---

### **Phase 5: Training Interface** ⏱️ 2-3 Wochen
**Ziel:** User kann Puzzles lösen mit Coach-Feedback

#### Tasks:
- [ ] Chessboard Integration
  - [ ] ChessboardJS einbinden
  - [ ] chess.js für Move Validation
  - [ ] Interactive Drag & Drop
  - [ ] Responsive für Mobile
- [ ] Puzzle UI
  - [ ] Puzzle laden (API Call)
  - [ ] Theme & Rating anzeigen
  - [ ] Züge erkennen (onDrop event)
  - [ ] Move Validation
  - [ ] Visual Feedback (Richtig/Falsch)
- [ ] Coach-Erklärungen 🎓
  - [ ] **Bei richtigem Zug:**
    ```
    "✅ Richtig! Der Läufer war ungeschützt.
     In deinem Spiel vs. Opponent123 hast du
     genau diese Situation übersehen.
     Siehst du den Fortschritt? 💪"
    ```
  - [ ] **Bei falschem Zug:**
    ```
    "❌ Nicht ganz! Schau nochmal:
     Der Turm auf e5 ist ungeschützt.
     Was passiert wenn du ihn mit deinem
     Springer schlägst?"
    ```
  - [ ] **Hinweis-Funktion:**
    ```
    "💡 Tipp: Eine schwarze Figur ist
     ungeschützt. Welche könnte das sein?
     Schau auf Reihe 5."
    ```
  - [ ] **Lösung zeigen:**
    - Best Move anzeigen
    - Animation auf Board
    - Erklärung warum
- [ ] Progress Tracking
  - [ ] Puzzle als "solved" markieren
  - [ ] Attempts tracken
  - [ ] Success Rate berechnen
  - [ ] Stats anzeigen:
    - "✅ 8 gelöst | ❌ 2 falsch | 📊 80%"
- [ ] Spaced Repetition
  - [ ] Fehlertyp Performance tracken
  - [ ] Oft falsch → häufiger zeigen
  - [ ] Beherrscht → seltener
  - [ ] Algorithmus: Leitner System
- [ ] Navigation
  - [ ] "Nächstes Puzzle" Button
  - [ ] "Lösung zeigen" Button  
  - [ ] "Überspringen" Button
  - [ ] "Zurück zum Dashboard"
- [ ] Verknüpfung zu eigenen Fehlern
  - [ ] "Das hast DU in Spiel XY falsch gemacht!"
  - [ ] Link zum Original-Spiel
  - [ ] Zeige Verbesserung auf

**Deliverable:** User kann Puzzles lösen und sieht personalisiertes Coach-Feedback

**Success Criteria:**
- ✅ Chessboard funktioniert einwandfrei
- ✅ Move Validation ist akkurat
- ✅ Feedback ist motivierend und lehrreich
- ✅ User fühlt Verbindung zu eigenen Fehlern
- ✅ Spaced Repetition funktioniert

---

### **Phase 6: Fortschritt & Analytics** ⏱️ 1 Woche
**Ziel:** User sieht messbare Verbesserung

#### Tasks:
- [ ] Error Stats über Zeit
  - [ ] Wöchentliche Aggregation
  - [ ] Tabelle: ErrorStats (week, error_type, count)
  - [ ] Trend berechnen (diese Woche vs letzte)
- [ ] Visualisierungen
  - [ ] Line Chart: Fehler über Zeit (Chart.js)
  - [ ] Bar Chart: Fehlertypen Breakdown
  - [ ] Progress Bars: Verbesserung pro Typ
- [ ] Trend Indicators
  - [ ] 📉 -20% Hanging Pieces diese Woche!
  - [ ] 📈 +10% Forks übersehen (Achtung!)
  - [ ] ➡️ Stabil bei Pins
- [ ] Achievements System
  - [ ] "🔥 7 Tage Streak"
  - [ ] "🏆 50 Puzzles gelöst"
  - [ ] "⭐ Erste Woche ohne Fehlertyp X"
  - [ ] "🎯 10 Spiele analysiert"
  - [ ] Badges im Dashboard anzeigen
- [ ] Positive Reinforcement
  - [ ] "Du hast 7 Spiele ohne Hanging Piece! 🎉"
  - [ ] "Deine Gabel-Erkennung ist 40% besser!"
  - [ ] Nicht nur Fehler, auch Erfolge zeigen
- [ ] Weekly Report (später per Email)
  - [ ] Zusammenfassung der Woche
  - [ ] Verbesserungen hervorheben
  - [ ] Nächste Ziele vorschlagen

**Deliverable:** User sieht klare Verbesserung und wird motiviert

**Success Criteria:**
- ✅ Charts sind verständlich und motivierend
- ✅ Trends sind akkurat
- ✅ Achievements sind erreichbar
- ✅ User fühlt Fortschritt

---

### **Phase 7: Polish & UX** ⏱️ 1 Woche
**Ziel:** Professionelles Look & Feel

#### Tasks:
- [ ] Responsive Design
  - [ ] Mobile Breakpoints testen
  - [ ] Touch-Gesten für Chessboard
  - [ ] Navbar Burger-Menu
- [ ] Loading States
  - [ ] Spinner bei API Calls
  - [ ] Skeleton Screens
  - [ ] Progress Bars bei Import/Analyse
- [ ] Error Handling
  - [ ] User-freundliche Fehler-Messages
  - [ ] "Etwas ist schiefgelaufen" statt Stack Traces
  - [ ] Retry Buttons
- [ ] Onboarding Tutorial
  - [ ] "Willkommen! So funktioniert's..."
  - [ ] 3-Step Guide:
    1. Spiele importieren
    2. Analyse starten
    3. Training beginnen
  - [ ] First-Time User Experience
- [ ] Tooltips & Help
  - [ ] "?" Icons bei komplexen Features
  - [ ] Hover-Tooltips mit Erklärungen
  - [ ] Help Center Link
- [ ] Performance
  - [ ] DB Queries optimieren
  - [ ] Lazy Loading für Spiele-Liste
  - [ ] Caching für Puzzle-Suche
  - [ ] Image Optimization
- [ ] Browser Testing
  - [ ] Chrome ✅
  - [ ] Firefox ✅
  - [ ] Safari ✅
  - [ ] Edge ✅

**Deliverable:** App fühlt sich "fertig" und professionell an

**Success Criteria:**
- ✅ Keine offensichtlichen Bugs
- ✅ Funktioniert auf Mobile
- ✅ Loading Times <2s
- ✅ Intuitive Navigation

---

### **Phase 8: Bot Feature** ⏱️ 3-4 Wochen *(SPÄTER)*
**Ziel:** Gegen adaptiven Coach spielen

#### Tasks:
- [ ] Game Interface
  - [ ] Zwei-Spieler Chessboard
  - [ ] User Color Auswahl (Weiß/Schwarz)
  - [ ] Move History anzeigen
  - [ ] Captured Pieces anzeigen
- [ ] Stockfish Bot Backend
  - [ ] Bot Endpoint: `/api/bot-move`
  - [ ] Skill Level parametrisieren (1-20)
  - [ ] Response Time (nicht sofort → realistisch)
  - [ ] Opening Book optional
- [ ] Adaptive Logic 🧠
  ```python
  def get_bot_move(position, user_weaknesses):
      # 70% Normal spielen
      if random() < 0.7:
          return stockfish.best_move(position, skill_level)
      
      # 30% Teste User-Schwäche
      weakness = user_weaknesses[0]  # z.B. "hanging_piece"
      
      if weakness == "hanging_piece":
          # Positioniere Figur ungeschützt
          # Warte ob User schlägt
          return create_hanging_piece_trap(position)
      
      if weakness == "fork_missed":
          # Stelle Gabel-Situation her
          return create_fork_opportunity(position)
  ```
- [ ] Trap Creation
  - [ ] hanging_piece: Figur ungeschützt lassen
  - [ ] fork: Gabel-Setup
  - [ ] pin: Fesselung möglich machen
  - [ ] backrank: Schwäche auf Grundreihe
- [ ] Post-Game Analyse
  - [ ] Wie normales Spiel analysieren
  - [ ] Fehler finden
  - [ ] "Du hast wieder Gabel übersehen!"
  - [ ] Link zu passenden Puzzles
  - [ ] In DB speichern wie Chess.com Games
- [ ] Bot Settings UI
  - [ ] Schwierigkeits-Slider (Anfänger → Experte)
  - [ ] "Adaptive Modus" Toggle
  - [ ] Time Control (Blitz, Rapid, etc.)
  - [ ] Hints aktivieren/deaktivieren

**Deliverable:** User kann gegen Bot spielen der seine Schwächen testet

**Success Criteria:**
- ✅ Bot spielt auf passendem Level
- ✅ Adaptive Traps sind effektiv aber fair
- ✅ Post-Game Analyse funktioniert
- ✅ User lernt durch Bot-Spiele

---

### **Phase 9: Deployment & Launch** ⏱️ 1 Woche
**Ziel:** App ist online und nutzbar

#### Tasks:
- [ ] PostgreSQL Migration
  - [ ] SQLite → PostgreSQL
  - [ ] Connection Strings
  - [ ] Migrations testen
- [ ] Environment Variables
  - [ ] .env für Secrets
  - [ ] DATABASE_URL
  - [ ] SECRET_KEY
  - [ ] STOCKFISH_PATH
- [ ] Hosting Setup
  - [ ] Railway / Render / Heroku Account
  - [ ] App deployen
  - [ ] Stockfish auf Server installieren
  - [ ] Domain verbinden
- [ ] SSL Certificate
  - [ ] HTTPS aktivieren
  - [ ] Let's Encrypt
- [ ] Monitoring
  - [ ] Error Tracking (Sentry)
  - [ ] Analytics (Optional)
  - [ ] Uptime Monitoring
- [ ] Backup Strategy
  - [ ] Automated DB Backups
  - [ ] Recovery Plan

**Deliverable:** App läuft stabil auf Production Server

---

### **Phase 10: Monetarisierung** ⏱️ 2 Wochen *(OPTIONAL)*
**Ziel:** Abo-Modell einrichten

#### Tasks:
- [ ] Pricing Strategy
  - [ ] Free Tier:
    - 5 Spiele Import pro Monat
    - 20 Puzzles pro Tag
    - Basis-Analyse
  - [ ] Premium Tier (€7-10/Monat):
    - Unlimited Imports
    - Unlimited Puzzles
    - Bot Zugang
    - Erweiterte Stats
    - Gegner-Analyse Tool
    - Priority Support
- [ ] Payment Integration
  - [ ] Stripe Setup
  - [ ] Subscription Plans
  - [ ] Checkout Flow
  - [ ] Webhooks für Events
- [ ] Billing UI
  - [ ] Pricing Page
  - [ ] Subscription Management
  - [ ] Invoice History
  - [ ] Upgrade/Downgrade
- [ ] Feature Gates
  - [ ] Free vs Premium Checks
  - [ ] Paywall UI
  - [ ] "Upgrade to Premium" CTAs

**Deliverable:** User können bezahlen und Premium Features nutzen

---

## 🎯 Success Metrics

### Technical Metrics
- **Page Load Time:** <2 Sekunden
- **API Response Time:** <500ms
- **Uptime:** >99.5%
- **Bug Rate:** <1% der Sessions
- **Mobile Responsive:** 100% Features funktionieren

### User Metrics
- **Onboarding Completion:** >80%
- **Daily Active Users:** Tracking
- **Puzzle Completion Rate:** >60%
- **Retention (7 Tage):** >40%
- **Retention (30 Tage):** >20%

### Learning Metrics
- **Fehlerreduktion:** -20% nach 4 Wochen
- **Puzzle Success Rate:** Verbesserung über Zeit
- **User Feedback:** >4.0/5.0 Stars

---

## 📊 Timeline Summary

| Phase | Duration | Key Deliverable |
|-------|----------|-----------------|
| 1. Foundation | 1-2 Wochen | Login funktioniert |
| 2. Chess.com | 1 Woche | Spiele importiert |
| 3. Stockfish | 2 Wochen | Fehler analysiert |
| 4. Lichess DB | 1 Woche | Puzzles verfügbar |
| 5. Training UI | 2-3 Wochen | Puzzles mit Coach |
| 6. Analytics | 1 Woche | Fortschritt sichtbar |
| 7. Polish | 1 Woche | Production-ready |
| 8. Bot | 3-4 Wochen | Adaptiver Bot |
| 9. Deploy | 1 Woche | Online |
| 10. Monetize | 2 Wochen | Abo möglich |

**MVP (Minimum Viable Product): ~11 Wochen**
**Full Product (mit Bot): ~15 Wochen**

---

## 🚀 Getting Started

### Quick Setup
```bash
# Clone Repo
git clone https://github.com/Taze00/chess-coach.git
cd chess-coach

# Virtual Environment
python -m venv venv
source venv/bin/activate  # Mac/Linux
venv\Scripts\activate  # Windows

# Install Dependencies
pip install -r requirements.txt

# Run App
python app.py
```

### First Steps
1. ✅ Projekt-Struktur aufsetzen
2. ✅ User Auth implementieren
3. ✅ Dummy Dashboard erstellen
4. ✅ Auf GitHub pushen
5. ✅ Phase 1 abschließen

---

## 📚 Resources

### Documentation
- Flask: https://flask.palletsprojects.com/
- python-chess: https://python-chess.readthedocs.io/
- Stockfish: https://stockfishchess.org/
- Lichess Puzzles: https://database.lichess.org/#puzzles
- Chess.com API: https://www.chess.com/news/view/published-data-api

### Tools
- VSCode: https://code.visualstudio.com/
- Git: https://git-scm.com/
- Postman: https://www.postman.com/ (API Testing)
- DB Browser for SQLite: https://sqlitebrowser.org/

---

## 🎓 Lessons Learned (wird gefüllt während Entwicklung)

*Hier dokumentieren wir was gut lief, was nicht, und was wir beim nächsten Mal anders machen würden.*

---

**Version:** 1.0  
**Erstellt:** November 2024  
**Status:** In Planung  
**Next:** Phase 1 - Foundation
