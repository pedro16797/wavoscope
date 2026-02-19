# Structure du Projet

Ce document décrit la structure des répertoires et le rôle de chaque composant dans le dépôt Wavoscope.

## Description des Répertoires

-   **`audio/`** : Contient le moteur audio central.
    -   `audio_backend.py` : Moteur de lecture principal, gérant les E/S fichiers, la vitesse et le streaming temps réel.
    -   `chord_analyzer.py` : Détection d'accords basée sur le chroma pour les marqueurs d'harmonie.
    -   `ringbuffer.py` : Implémentation d'un tampon circulaire sans verrou pour les données audio.
    -   `spectrum_analyzer.py` : Logique de calcul FFT et données spectrales.
    -   `synth.py` : Synthèse simple pour les clics du métronome.
    -   `waveform_cache.py` : Gère la génération et la mise en cache des données de forme d'onde pour un affichage efficace.
-   **`backend/`** : Backend web moderne basé sur FastAPI.
    -   `main.py` : Point d'entrée du serveur FastAPI, servant les endpoints API et les actifs frontend.
    -   `state.py` : État global partagé (instance active du `Project`).
    -   `routers/` : Routes FastAPI modularisées pour les différents domaines API (audio, lecture, projet, etc.).
-   **`cli/`** : Contient des utilitaires en ligne de commande.
    -   `flag_cli.py` : Utilitaires pour gérer les marqueurs via le terminal.
-   **`config/`** : Fichiers de configuration et paramètres par défaut de l'application.
-   **`docs/`** : Documentation du projet, y compris les feuilles de route et guides de structure.
-   **`frontend/`** : Interface utilisateur basée sur React.
    -   `src/components/` : Composants React (Forme d'onde, Spectre, Timeline, Barre de lecture).
    -   `src/store/` : Gestion d'état frontend (Zustand).
    -   `dist/` : Actifs de production compilés.
-   **`resources/`** : Actifs statiques comme les icônes (SVG), thèmes (JSON), traductions (JSON) et ressources applicatives.
-   **`scripts/`** : Scripts d'automatisation et utilitaires (ex: génération de captures d'écran).
-   **`session/`** : Gère la persistance du projet et l'état de haut niveau.
    -   `project.py` : Classe `Project` liant l'audio, les métadonnées (marqueurs) et le cache.
-   **`utils/`** : Fonctions d'aide générales et utilitaires partagés.

## Fichiers Racine

-   **`run.sh` / `run.bat`** : Scripts pour configurer l'environnement et lancer l'application.
-   **`build.sh` / `build.bat`** : Scripts pour compiler le frontend et packager l'application.
-   **`main.py`** : Point d'entrée de l'application. Lance maintenant FastAPI + pywebview.
-   **`AGENTS.md`** : Guide et feuille de route pour les agents IA travaillant sur le projet.
-   **`Readme.md`** : Présentation du projet et instructions d'installation.
-   **`LICENSE`** : Termes de la licence MIT du projet.
-   **`SECURITY.md`** : Politique de signalement des vulnérabilités de sécurité.
-   **`requirements.txt`** : Dépendances Python.
