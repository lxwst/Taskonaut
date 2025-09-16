# Changelog

Alle wichtigen Änderungen an diesem Projekt werden in dieser Datei dokumentiert.

Das Format basiert auf [Keep a Changelog](https://keepachangelog.com/de/1.0.0/),
und dieses Projekt folgt [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Modulare Code-Architektur mit separaten Modulen für core, gui und utils
- Professionelle Paket-Struktur mit setup.py
- Umfassende Dokumentation und README
- MIT Lizenz für Open Source Distribution
- GitHub Actions CI/CD Pipeline
- Windows Executable Build-Script
- Entwickler-Setup-Script
- Contributing Guidelines
- Changelog Dokumentation

### Changed
- Code-Struktur von monolithischer Datei zu modularer Architektur
- Verbesserte Dokumentation mit detaillierten Installationsanweisungen
- Professionelle Python Package-Struktur

## [1.0.0] - 2024-01-XX

### Added
- Desktop Overlay für Arbeitszeiterfassung
- Session-Management mit Projekt-Tracking
- Excel-Integration für Datenexport
- Konfigurierbares Overlay (Position, Transparenz, Größe)
- Context-Menu mit allen wichtigen Funktionen
- Automatische Zeitberechnung und Formatierung
- Projekt-Auswahl über Dropdown-Menu
- Session-Info Dialog mit detaillierten Informationen
- Konfiguration über JSON-Datei
- Arbeitszeiten-Tracking mit Start/Stop/Pause Funktionalität

### Features
- **Overlay Interface**: Minimales, transparentes Overlay am Desktop
- **Zeiterfassung**: Automatisches Tracking von Arbeitszeiten
- **Projekt-Management**: Wechsel zwischen verschiedenen Projekten
- **Excel Export**: Automatischer Export in strukturierte Excel-Tabelle
- **Konfigurierbarkeit**: Anpassbare Overlay-Einstellungen
- **Session-Persistenz**: Automatisches Speichern und Wiederherstellen
- **Context-Menu**: Rechtsklick-Menü für alle Funktionen
- **Benutzerfreundlich**: Intuitive Bedienung ohne komplexe UI

### Technical Details
- Python 3.8+ Kompatibilität
- Tkinter GUI Framework
- Pandas/OpenPyXL für Excel-Integration
- JSON-basierte Konfiguration
- Modulare Architektur für Wartbarkeit

## [0.1.0] - Initial Development

### Added
- Grundlegende Overlay-Funktionalität
- Einfache Zeiterfassung
- Basis Excel-Export

---

## Versioning Schema

- **MAJOR**: Inkompatible API-Änderungen
- **MINOR**: Neue Funktionalität (rückwärtskompatibel)
- **PATCH**: Bug-Fixes (rückwärtskompatibel)

## Kategorien

- `Added`: Neue Features
- `Changed`: Änderungen an bestehender Funktionalität
- `Deprecated`: Features die bald entfernt werden
- `Removed`: Entfernte Features
- `Fixed`: Bug-Fixes
- `Security`: Sicherheitsrelevante Änderungen
