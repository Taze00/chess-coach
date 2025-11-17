# ♟️ Chess Coach - Dein personalisierter Schach-Trainer

Ein Web-Tool das deine Chess.com Spiele analysiert, deine häufigsten Fehler findet, und dir Taktikaufgaben gibt die GENAU diese Fehler trainieren.

**🎯 Ziel:** Messbare ELO-Verbesserung durch personalisiertes, fehler-fokussiertes Training.

---

## 🚀 Quick Start

### 1. Virtual Environment aktivieren

**Windows:**
```bash
venv\Scripts\activate
```

**Mac/Linux:**
```bash
source venv/bin/activate
```

### 2. Flask App starten

```bash
python app.py
```

### 3. Browser öffnen

Öffne: http://localhost:5000

---

## ✅ Phase 1 - ABGESCHLOSSEN!

**Was funktioniert:**
- ✅ Projekt-Struktur erstellt
- ✅ Virtual Environment eingerichtet
- ✅ Dependencies installiert
- ✅ Database Models (User, Game, Error, PuzzleProgress, ErrorStats)
- ✅ Authentication System (Register, Login, Logout)
- ✅ Flask App mit Routes
- ✅ Templates (Landing Page, Login, Register, Dashboard)
- ✅ CSS Styling mit Bootstrap 5
- ✅ Responsive Design

**Funktionale Features:**
- User Registration mit Email, Passwort, Chess.com Username
- Login/Logout System mit Flask-Login
- Password Hashing mit bcrypt
- Dashboard mit Dummy Stats
- Placeholder Pages für Games, Training, Progress

---

## 📂 Projekt-Struktur

```
chess-coach/
├── app.py                 # Main Flask App ✅
├── models.py              # Database Models ✅
├── auth.py                # Authentication Blueprint ✅
├── requirements.txt       # Dependencies ✅
├── .env                   # Environment Variables ✅
├── .gitignore            # Git Ignore ✅
│
├── templates/            # HTML Templates ✅
│   ├── base.html         # Base Layout
│   ├── index.html        # Landing Page
│   ├── login.html        # Login Page
│   ├── register.html     # Register Page
│   ├── dashboard.html    # Dashboard
│   ├── games.html        # Games List (Placeholder)
│   ├── training.html     # Training (Placeholder)
│   └── progress.html     # Progress (Placeholder)
│
├── static/               # Static Files ✅
│   └── css/
│       └── style.css     # Custom CSS
│
├── docs/                 # Documentation
│   ├── CONTEXT.md        # Project Context
│   ├── ROADMAP.md        # Development Plan
│   ├── TODO.md           # Next Steps
│   └── README.md         # Docs Overview
│
└── venv/                 # Virtual Environment ✅
```

---

## 🔜 Nächste Schritte - Phase 2

**Chess.com Integration:**
1. Chess.com API Client erstellen (`chess_api.py`)
2. Import Button im Dashboard
3. Spiele in DB speichern
4. Games Liste anzeigen

Siehe [docs/TODO.md](docs/TODO.md) für Details.

---

## 🛠️ Tech Stack

**Backend:**
- Python 3.12+
- Flask 3.0.0
- SQLAlchemy (ORM)
- Flask-Login (Authentication)
- Flask-Bcrypt (Password Hashing)

**Frontend:**
- Bootstrap 5
- Vanilla JavaScript
- Custom CSS

**Database:**
- SQLite (Development)
- PostgreSQL (Production - später)

---

## 📊 Database Schema

**Users:**
- id, email, password_hash, chesscom_username, created_at

**Games:**
- id, user_id, pgn, result, played_at, analyzed, chesscom_url

**Errors:**
- id, game_id, user_id, error_type, position, move_played, best_move, explanation, severity

**PuzzleProgress:**
- id, user_id, puzzle_id, error_type, attempts, solved, last_attempt

**ErrorStats:**
- id, user_id, error_type, week, count

---

## 🧪 Testing Phase 1

### Manuelle Tests:

1. **Landing Page:**
   - [ ] http://localhost:5000 öffnen
   - [ ] Features sichtbar
   - [ ] Links zu Login/Register funktionieren

2. **Registration:**
   - [ ] Email, Passwort, Chess.com Username eingeben
   - [ ] Account wird erstellt
   - [ ] Redirect zu Login
   - [ ] User in DB gespeichert

3. **Login:**
   - [ ] Mit erstelltem Account einloggen
   - [ ] Redirect zu Dashboard
   - [ ] Welcome Message mit Username

4. **Dashboard:**
   - [ ] Stats Cards angezeigt (0, 0, 0)
   - [ ] Quick Actions Buttons (disabled)
   - [ ] Navigation funktioniert

5. **Logout:**
   - [ ] Logout Button funktioniert
   - [ ] Redirect zu Landing Page
   - [ ] Session beendet

---

## 📝 Entwickler-Notizen

### Environment Variables (.env)

```bash
SECRET_KEY=dev-secret-key-change-in-production-12345
FLASK_ENV=development
FLASK_DEBUG=True
DATABASE_URL=sqlite:///chess_coach.db
```

### Virtual Environment Commands

**Aktivieren:**
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**Deaktivieren:**
```bash
deactivate
```

**Dependencies updaten:**
```bash
pip freeze > requirements.txt
```

### Flask Commands

**App starten:**
```bash
python app.py
```

**Database Shell:**
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
```

---

## 🐛 Known Issues

*Keine bekannten Issues in Phase 1*

---

## 📚 Dokumentation

- **[ROADMAP.md](docs/ROADMAP.md)** - Kompletter Entwicklungsplan (alle Phasen)
- **[CONTEXT.md](docs/CONTEXT.md)** - Projekt-Kontext für neue Sessions
- **[TODO.md](docs/TODO.md)** - Nächste Tasks und Checklisten

---

## 🎉 Success!

Phase 1 ist erfolgreich abgeschlossen! Die Foundation steht:
- ✅ App läuft lokal
- ✅ User kann sich registrieren und einloggen
- ✅ Database ist konfiguriert
- ✅ UI ist clean und responsive

**Nächster Schritt:** Phase 2 - Chess.com Integration

---

**Happy Chess Improving! ♟️**
