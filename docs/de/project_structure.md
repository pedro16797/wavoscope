# Projektstruktur

Dieses Dokument beschreibt die Verzeichnisstruktur und den Zweck der einzelnen Komponenten im Wavoscope-Repository.

## Verzeichnisübersicht

-   **`audio/`**: Enthält die Kern-Audio-Engine.
    -   `audio_backend.py`: Haupt-Wiedergabe-Engine, verwaltet Datei-E/A, Geschwindigkeit und Echtzeit-Streaming.
    -   `chord_analyzer.py`: Chroma-basierte Akkorderkennung für Harmonie-Markierungen.
    -   `ringbuffer.py`: Sperrfreie Ringpuffer-Implementierung für Audiodaten.
    -   `spectrum_analyzer.py`: Logik für FFT-Berechnungen und Spektraldaten.
    -   `synth.py`: Einfache Synthese für Metronom-Klicks.
    -   `waveform_cache.py`: Verwaltet die Generierung und das Caching von Wellenformdaten für eine effiziente Darstellung.
-   **`backend/`**: Modernes Web-Backend basierend auf FastAPI.
    -   `main.py`: Einstiegspunkt für den FastAPI-Server, stellt API-Endpunkte und Frontend-Assets bereit.
    -   `state.py`: Gemeinsam genutzter globaler Zustand (aktive `Project`-Instanz).
    -   `routers/`: Modularisierte FastAPI-Router für verschiedene API-Bereiche (Audio, Wiedergabe, Projekt usw.).
-   **`cli/`**: Enthält Kommandozeilen-Utilities.
    -   `flag_cli.py`: Utilities zur Verwaltung von Markierungen über das Terminal.
-   **`config/`**: Konfigurationsdateien und Standardeinstellungen für die Anwendung.
-   **`docs/`**: Projektdokumentation, einschließlich Roadmaps und Strukturleitfäden.
-   **`frontend/`**: Die React-basierte grafische Benutzeroberfläche.
    -   `src/components/`: React-Komponenten (Wellenform, Spektrum, Timeline, Wiedergabeleiste).
    -   `src/store/`: Frontend-Zustandsmanagement (Zustand).
    -   `dist/`: Kompilierte Produktions-Assets.
-   **`resources/`**: Statische Assets wie Icons (SVG), Themes (JSON), Übersetzungen (JSON) und Anwendungsressourcen.
-   **`scripts/`**: Automatisierungsskripte und Utilities (z. B. Screenshot-Generierung).
-   **`session/`**: Verwaltet die Projektpersistenz und den High-Level-Zustand.
    -   `project.py`: Die `Project`-Klasse, die Audio, Metadaten (Markierungen) und Cache verknüpft.
-   **`utils/`**: Allgemeine Hilfsfunktionen und gemeinsam genutzte Utilities.

## Dateien im Hauptverzeichnis

-   **`run.sh` / `run.bat`**: Skripte zum Einrichten der Umgebung und Starten der Anwendung.
-   **`build.sh` / `build.bat`**: Skripte zum Bauen des Frontends und Paketieren der Anwendung.
-   **`main.py`**: Der Einstiegspunkt der Anwendung. Startet jetzt FastAPI + pywebview.
-   **`AGENTS.md`**: Leitfaden und Roadmap für KI-Agenten, die am Projekt arbeiten.
-   **`Readme.md`**: Projektübersicht und Installationsanweisungen.
-   **`LICENSE`**: Die MIT-Lizenzbedingungen des Projekts.
-   **`SECURITY.md`**: Richtlinien für die Meldung von Sicherheitslücken.
-   **`requirements.txt`**: Python-Abhängigkeiten.
