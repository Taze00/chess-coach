# 🚀 Setup & Testing Guide

## Phase 1 - Foundation Setup

### 1. Virtual Environment aktivieren

**Windows (du nutzt Windows):**
```bash
venv\Scripts\activate
```

Du solltest `(venv)` vor deinem Prompt sehen.

### 2. Flask App starten

```bash
python app.py
```

Output sollte sein:
```
 * Running on http://127.0.0.1:5000
 * Debug mode: on
```

### 3. Browser öffnen

Öffne: **http://localhost:5000**

---

## ✅ Test Checkliste

### Test 1: Landing Page
- [ ] Öffne http://localhost:5000
- [ ] Siehst du die Hero Section mit "Chess Coach"?
- [ ] Sind 3 Feature Cards sichtbar (Analyse, Training, Wachsen)?
- [ ] Funktionieren die Buttons "Jetzt starten" und "Login"?

### Test 2: Registration
- [ ] Klicke auf "Jetzt starten" oder "Registrieren"
- [ ] Fülle das Formular aus:
  - Email: test@example.com
  - Chess.com Username: FirstRulesChess (oder dein Username)
  - Passwort: test123
  - Passwort bestätigen: test123
- [ ] Klicke "Registrieren"
- [ ] Siehst du die Success Message "Account erfolgreich erstellt"?
- [ ] Wirst du zum Login weitergeleitet?

### Test 3: Login
- [ ] Gib Email und Passwort ein
- [ ] Klicke "Einloggen"
- [ ] Siehst du "Willkommen zurück, FirstRulesChess!"?
- [ ] Wirst du zum Dashboard weitergeleitet?

### Test 4: Dashboard
- [ ] Siehst du "Willkommen zurück, [Username]!"?
- [ ] Sind 3 Stats Cards sichtbar (alle mit 0)?
- [ ] Sind die Buttons "Spiele importieren" und "Training starten" disabled mit Badge "Bald verfügbar"?
- [ ] Funktioniert die Navigation in der Navbar?

### Test 5: Navigation
- [ ] Klicke auf "Spiele" in der Navbar
- [ ] Siehst du die Placeholder Page "Feature in Entwicklung"?
- [ ] Klicke auf "Training"
- [ ] Siehst du die Placeholder Page?
- [ ] Klicke auf "Fortschritt"
- [ ] Siehst du die Placeholder Page?

### Test 6: Logout
- [ ] Klicke auf "Logout" in der Navbar
- [ ] Siehst du "Erfolgreich ausgeloggt"?
- [ ] Wirst du zur Landing Page weitergeleitet?
- [ ] Versuch http://localhost:5000/dashboard zu öffnen
- [ ] Wirst du zum Login weitergeleitet mit Message "Bitte einloggen"?

---

## 🗄️ Database prüfen

Nach Registration kannst du die Database prüfen:

```bash
python
>>> from app import app, db
>>> from models import User
>>> with app.app_context():
...     users = User.query.all()
...     for user in users:
...         print(f"Email: {user.email}, Username: {user.chesscom_username}")
>>> exit()
```

Du solltest deinen erstellten User sehen!

---

## 🐛 Troubleshooting

### App startet nicht
- Stelle sicher dass venv aktiviert ist: `venv\Scripts\activate`
- Prüfe ob alle Dependencies installiert sind: `pip list`

### "Module not found" Error
```bash
pip install -r requirements.txt
```

### Database Error
```bash
python
>>> from app import app, db
>>> with app.app_context():
...     db.create_all()
>>> exit()
```

### Port 5000 bereits belegt
Ändere in [app.py](app.py#L85):
```python
app.run(debug=True, host='0.0.0.0', port=5001)
```

---

## ✅ Phase 1 abgeschlossen wenn:

- [x] ✅ App startet ohne Fehler
- [x] ✅ Registration funktioniert
- [x] ✅ Login funktioniert
- [x] ✅ Dashboard ist erreichbar
- [x] ✅ Logout funktioniert
- [x] ✅ Navigation funktioniert
- [x] ✅ Design sieht clean aus

---

## 🔜 Nächste Schritte

Wenn alle Tests erfolgreich sind, ist Phase 1 abgeschlossen!

**Phase 2 startet mit:**
- Chess.com API Integration
- Spiele Import Funktion
- Games Liste

Siehe [docs/TODO.md](docs/TODO.md) für Details.

---

**Happy Testing! 🎉**
