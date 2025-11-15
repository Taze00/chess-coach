# ✅ CHESS COACH - TODO LIST

## 🎯 Current Focus: Phase 1 - Foundation

**Goal:** Basic App mit Login läuft lokal

---

## 📋 Immediate Tasks (This Week)

### Setup
- [ ] Git Repository initialisieren
  ```bash
  git init
  git add .
  git commit -m "Initial commit - Project setup"
  git branch -M main
  git remote add origin https://github.com/Taze00/chess-coach.git
  git push -u origin main
  ```

- [ ] Projekt-Struktur erstellen
  ```
  chess-coach/
  ├── app.py
  ├── models.py
  ├── auth.py
  ├── requirements.txt
  ├── .env
  ├── .gitignore
  ├── templates/
  │   ├── base.html
  │   ├── index.html
  │   ├── login.html
  │   ├── register.html
  │   └── dashboard.html
  └── static/
      └── css/
          └── style.css
  ```

- [ ] Virtual Environment
  ```bash
  python -m venv venv
  source venv/bin/activate  # Mac/Linux
  venv\Scripts\activate  # Windows
  ```

- [ ] Dependencies installieren
  ```bash
  pip install Flask
  pip install Flask-SQLAlchemy
  pip install Flask-Login
  pip install Flask-Bcrypt
  pip install python-chess
  pip install requests
  pip install python-dotenv
  
  # Save to requirements.txt
  pip freeze > requirements.txt
  ```

### Database Models
- [ ] `models.py` erstellen
  - [ ] User Model
    - id, email, password_hash, chesscom_username, created_at
  - [ ] Game Model
    - id, user_id, pgn, result, played_at, analyzed, chesscom_url
  - [ ] Error Model
    - id, game_id, user_id, error_type, position, move_played, best_move, explanation, severity
  - [ ] PuzzleProgress Model
    - id, user_id, puzzle_id, error_type, attempts, solved, last_attempt

### Authentication
- [ ] `auth.py` Blueprint erstellen
- [ ] Registration Route
  - [ ] Form: Email, Password, Chess.com Username
  - [ ] Validation
  - [ ] Password Hashing (bcrypt)
  - [ ] User anlegen in DB
  - [ ] Redirect to Login
- [ ] Login Route
  - [ ] Form: Email, Password
  - [ ] Validation
  - [ ] Session erstellen (Flask-Login)
  - [ ] Redirect to Dashboard
- [ ] Logout Route
  - [ ] Session beenden
  - [ ] Redirect to Landing Page
- [ ] Password vergessen (optional später)

### Templates
- [ ] `base.html` - Base Layout
  - [ ] Bootstrap 5 CDN
  - [ ] Navbar (Logo, Navigation, User Menu)
  - [ ] Flash Messages
  - [ ] Footer
  - [ ] Block content

- [ ] `index.html` - Landing Page
  - [ ] Hero Section
  - [ ] Features (3 Cards: Analyse, Training, Wachsen)
  - [ ] CTAs (Registrieren, Login)

- [ ] `register.html`
  - [ ] Form: Email, Password, Password Confirm, Chess.com Username
  - [ ] Submit Button
  - [ ] Link zu Login

- [ ] `login.html`
  - [ ] Form: Email, Password
  - [ ] "Remember Me" Checkbox
  - [ ] Submit Button
  - [ ] Link zu Register

- [ ] `dashboard.html`
  - [ ] Welcome Message
  - [ ] Stats Cards (dummy data):
    - Spiele: 0
    - Fehler: 0
    - Gelöst: 0
  - [ ] Quick Actions:
    - "Spiele importieren" (disabled)
    - "Training starten" (disabled)

### Routes
- [ ] `app.py` - Main App
  - [ ] App Config (SECRET_KEY, DATABASE_URI)
  - [ ] Database init
  - [ ] Login Manager Setup
  - [ ] Auth Blueprint registrieren
  - [ ] `/` - Landing Page (public)
  - [ ] `/dashboard` - Dashboard (login_required)
  - [ ] `/games` - Games List (placeholder)
  - [ ] `/training` - Training (placeholder)
  - [ ] `/progress` - Progress (placeholder)

### Styling
- [ ] `static/css/style.css`
  - [ ] Custom Colors
  - [ ] Card Styles
  - [ ] Button Hover Effects
  - [ ] Responsive Breakpoints

### Testing
- [ ] Test Registration
  - [ ] Create User
  - [ ] Check DB
  - [ ] Try Login
- [ ] Test Login
  - [ ] Correct Credentials → Dashboard
  - [ ] Wrong Credentials → Error Message
- [ ] Test Logout
  - [ ] Session ended
  - [ ] Redirect to Landing

---

## 🎯 Next Phase (Phase 2)

### Chess.com Integration
- [ ] Chess.com API Research
- [ ] API Client erstellen (`chess_api.py`)
- [ ] Import Button im Dashboard
- [ ] Games in DB speichern
- [ ] Games Liste anzeigen

---

## 🔜 Future Tasks

### Phase 3: Stockfish
- [ ] Stockfish installieren
- [ ] `stockfish_analyzer.py` erstellen
- [ ] Analyse-Algorithmus
- [ ] Fehler-Kategorisierung
- [ ] Dashboard Stats updaten

### Phase 4: Lichess Puzzles
- [ ] Lichess DB Download
- [ ] Puzzle Import
- [ ] Matching Algorithmus
- [ ] API Endpoints

### Phase 5: Training UI
- [ ] ChessboardJS Integration
- [ ] Puzzle Interface
- [ ] Coach-Feedback
- [ ] Progress Tracking

### Phase 6: Analytics
- [ ] Charts mit Chart.js
- [ ] Error Stats über Zeit
- [ ] Achievements System

### Phase 7: Polish
- [ ] Mobile Responsive
- [ ] Loading States
- [ ] Error Handling
- [ ] Onboarding Tutorial

### Phase 8: Bot (später)
- [ ] Bot Interface
- [ ] Adaptive Logic
- [ ] Post-Game Analysis

---

## 📝 Notes & Ideas

### Wichtige Entscheidungen
- SQLite für Dev, PostgreSQL für Prod
- Bootstrap 5 für UI
- Vanilla JS (kein React für MVP)
- Lichess Puzzles (kostenlos!)

### Offene Fragen
- [ ] Wie viele Spiele pro Import? (Letzte 10? 20? Konfigurierbar?)
- [ ] Stockfish Depth/Time? (Balance: Genauigkeit vs Speed)
- [ ] Puzzle Rating Bereich? (User ELO ±200?)

### Ideen für später
- Email Notifications für Weekly Reports
- Social Features (Freunde, Vergleiche)
- Mobile App (React Native?)
- Integration mit Lichess (zusätzlich zu Chess.com)

---

## 🐛 Known Issues

*Wird gefüllt wenn wir auf Probleme stoßen*

---

## ✅ Completed Tasks

*Wird gefüllt wenn Tasks erledigt sind*

### Planning Phase
- [x] Projekt-Idee definiert
- [x] Features festgelegt
- [x] Tech Stack ausgewählt
- [x] ROADMAP.md erstellt
- [x] CONTEXT.md erstellt
- [x] TODO.md erstellt (this file)

---

**Last Updated:** November 2024  
**Current Phase:** Phase 1 - Foundation  
**Next Milestone:** Working Login System
