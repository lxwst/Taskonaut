# Contributing to Arbeitszeit Tracker

Vielen Dank für Ihr Interesse, zu diesem Projekt beizutragen! 

## Entwicklungsumgebung einrichten

### Voraussetzungen
- Python 3.8 oder höher
- Git

### Setup
1. Repository klonen:
```bash
git clone https://github.com/yourusername/arbeitszeit-tracker.git
cd arbeitszeit-tracker
```

2. Entwicklungsumgebung einrichten:
```bash
python dev_setup.py
```

3. Oder manuell:
```bash
# Virtual Environment erstellen
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Dependencies installieren
pip install -r requirements.txt

# Entwicklungsinstallation
pip install -e .
```

## Code-Struktur

```
src/
├── core/           # Kernfunktionalität
│   ├── config_manager.py
│   ├── session_manager.py
│   └── excel_manager.py
├── gui/            # Benutzeroberfläche
│   └── overlay_window.py
├── utils/          # Hilfsfunktionen
│   └── time_utils.py
└── main.py         # Einstiegspunkt
```

## Entwicklungsrichtlinien

### Code-Stil
- Folgen Sie PEP 8
- Verwenden Sie Type Hints wo möglich
- Dokumentieren Sie alle öffentlichen Methoden mit Docstrings
- Maximale Zeilenlänge: 100 Zeichen

### Commit-Nachrichten
- Verwenden Sie aussagekräftige Commit-Nachrichten
- Format: `type(scope): description`
- Beispiele:
  - `feat(gui): add project selection menu`
  - `fix(excel): prevent data loss on sheet creation`
  - `docs(readme): update installation instructions`

### Branch-Struktur
- `main`: Stable release branch
- `develop`: Development branch
- `feature/feature-name`: Feature branches
- `bugfix/bug-description`: Bug fix branches

## Testing

### Lokale Tests
```bash
# Setup testen
python dev_setup.py

# Manuelle Tests
python src/main.py
```

### Automatisierte Tests
CI/CD Pipeline läuft automatisch bei Push/Pull Request.

## Pull Requests

1. Fork das Repository
2. Erstellen Sie einen Feature-Branch von `develop`
3. Implementieren Sie Ihre Änderungen
4. Testen Sie Ihre Änderungen
5. Commiten Sie mit aussagekräftigen Nachrichten
6. Erstellen Sie einen Pull Request gegen `develop`

### Pull Request Checklist
- [ ] Code folgt den Stil-Richtlinien
- [ ] Neue Features sind dokumentiert
- [ ] Tests wurden durchgeführt
- [ ] README.md wurde bei Bedarf aktualisiert

## Feature Requests und Bug Reports

### Bug Reports
Verwenden Sie das Bug Report Template und geben Sie an:
- Python Version
- Betriebssystem
- Schritte zur Reproduktion
- Erwartetes vs. tatsächliches Verhalten
- Relevante Log-Ausgaben

### Feature Requests
Verwenden Sie das Feature Request Template und beschreiben Sie:
- Use Case / Problem
- Vorgeschlagene Lösung
- Alternativen
- Zusätzlicher Kontext

## Code Review Prozess

1. Alle Pull Requests benötigen mindestens eine Review
2. CI/CD Tests müssen bestehen
3. Mindestens ein Maintainer muss approven
4. Squash and Merge in develop branch

## Release Prozess

1. Feature-Complete auf `develop`
2. Erstelle Release-Branch: `release/v1.x.x`
3. Testing und Bug-Fixes
4. Merge in `main` und Tag erstellen
5. Release auf GitHub mit Changelog

## Entwickler-Tools

### Nützliche Scripts
- `dev_setup.py`: Entwicklungsumgebung einrichten
- `build.py`: Windows Executable erstellen

### Debugging
- Logs werden in `debug.log` geschrieben
- Verwenden Sie `logging` Module für Debug-Ausgaben
- Config-Datei für Debug-Modi: `dev_config.json`

## Dokumentation

- Halten Sie README.md aktuell
- Dokumentieren Sie Breaking Changes
- Ergänzen Sie Docstrings für neue Funktionen
- Aktualisieren Sie Changelog bei Releases

## Community

- Seien Sie respektvoll und konstruktiv
- Helfen Sie anderen Entwicklern
- Folgen Sie dem Code of Conduct

## Fragen?

Bei Fragen können Sie:
- Issue erstellen für allgemeine Fragen
- Pull Request mit Draft-Status für Diskussionen
- Maintainer direkt kontaktieren

Vielen Dank für Ihren Beitrag! 🎉
