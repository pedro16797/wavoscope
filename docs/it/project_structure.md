# Struttura del Progetto

Questo documento descrive la struttura delle cartelle e lo scopo di ogni componente nel repository di Wavoscope.

## Descrizione delle Cartelle

-   **`audio/`**: Contiene il motore audio principale.
    -   `audio_backend.py`: Motore principale di riproduzione audio, gestisce I/O di file, controllo velocità e streaming in tempo reale.
    -   `chord_analyzer.py`: Rilevamento accordi basato su chroma per i marcatori di armonia.
    -   `ringbuffer.py`: Implementazione di un buffer circolare senza lock per i dati audio.
    -   `spectrum_analyzer.py`: Logica per il calcolo FFT e dati spettrali.
    -   `synth.py`: Sintesi semplice per i clic del metronomo.
    -   `waveform_cache.py`: Gestisce la generazione e la cache dei dati della forma d'onda per una visualizzazione efficiente.
-   **`backend/`**: Backend web moderno basato su FastAPI.
    -   `main.py`: Punto di ingresso per il server FastAPI, serve gli endpoint API e gli asset del frontend.
    -   `state.py`: Stato globale condiviso (istanza attiva del `Project`).
    -   `routers/`: Router FastAPI modularizzati per diversi domini API (audio, riproduzione, progetto, ecc.).
-   **`cli/`**: Contiene utility per l'interfaccia a riga di comando.
    -   `flag_cli.py`: Utility per gestire i marcatori tramite terminale.
-   **`config/`**: File di configurazione e impostazioni predefinite per l'applicazione.
-   **`docs/`**: Documentazione del progetto, inclusi roadmap e guide alla struttura.
-   **`frontend/`**: L'interfaccia utente grafica basata su React.
    -   `src/components/`: Componenti React (Forma d'Onda, Spettro, Timeline, Barra di Riproduzione).
    -   `src/store/`: Gestione dello stato del frontend (Zustand).
    -   `dist/`: Asset di produzione compilati.
-   **`resources/`**: Asset statici come icone (SVG), temi (JSON), traduzioni (JSON) e risorse dell'app.
-   **`scripts/`**: Script di automazione e utility (es. generazione screenshot).
-   **`session/`**: Gestisce la persistenza del progetto e lo stato di alto livello.
    -   `project.py`: Classe `Project` che collega audio, metadati (marcatori) e cache.
-   **`utils/`**: Funzioni di aiuto generali e utility condivise.

## File nella Root

-   **`run.sh` / `run.bat`**: Script per configurare l'ambiente ed avviare l'applicazione.
-   **`main.py`**: Punto di ingresso dell'applicazione. Ora avvia FastAPI + pywebview.
-   **`AGENTS.md`**: Guida e roadmap per gli agenti IA che lavorano sul progetto.
-   **`Readme.md`**: Panoramica del progetto ed istruzioni per la configurazione.
-   **`LICENSE`**: Termini della licenza MIT del progetto.
-   **`SECURITY.md`**: Policy per la segnalazione di vulnerabilità di sicurezza.
-   **`requirements.txt`**: Dipendenze Python.
