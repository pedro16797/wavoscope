# Struttura del Progetto

Questo documento descrive la struttura delle cartelle e lo scopo di ogni componente nel repository di Wavoscope.

## Descrizione delle Cartelle

-   **`src/`**: Contiene la logica centrale dell'applicazione e il codice sorgente.
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
        -   `gui.py`: Logica `pywebview` per l'interfaccia grafica.
        -   `launcher.py`: Logica di aiuto per avviare il backend e il frontend.
    -   **`frontend/`**: L'interfaccia utente grafica basata su React.
        -   `src/components/`: Componenti React (Forma d'Onda, Spettro, Timeline, Barra di Riproduzione).
        -   `src/store/`: Gestione dello stato del frontend (Zustand).
        -   `dist/`: Asset di produzione compilati.
        -   `tests/`: Test unitari per i componenti frontend e la logica dello store.
    -   **`scripts/`**: Script di automazione e utility (es. generazione screenshot, creazione del launcher).
    -   **`session/`**: Gestisce la persistenza del progetto e lo stato di alto livello.
        -   `project.py`: Classe `Project` che collega audio, metadati (marcatori) e cache.
        -   `manager.py`: Gestisce i file sidecar `.oscope`.
        -   `flags.py`: Gestisce le liste di marcatori di ritmo e accordi.
        -   `undo.py`: Gestione della cronologia degli annullamenti basata su delta.
    -   **`tests/`**: Test unitari e di integrazione per il backend e la logica centrale.
    -   **`utils/`**: Funzioni di aiuto generali e utility condivise (logging, config, ecc.).
    -   `main.py`: Il punto di ingresso principale per l'applicazione.
    -   `requirements.txt`: Dipendenze Python.

-   **`config/`**: File di configurazione e impostazioni predefinite per l'applicazione.
-   **`docs/`**: Documentazione del progetto, inclusi roadmap e guide alla struttura.
-   **`resources/`**: Asset statici come icone (SVG), temi (JSON), traduzioni (JSON) e risorse dell'app.

## File nella Root

-   **`run.sh` / `run.bat`**: Script per configurare l'ambiente ed avviare l'applicazione.
-   **`Wavoscope` / `Wavoscope.exe`**: Eseguibile del launcher (generato dagli script).
-   **`AGENTS.md`**: Guida e roadmap per gli agenti IA che lavorano sul progetto.
-   **`CONTRIBUTING.md`**: Linee guida per contribuire al progetto.
-   **`Readme.md`**: Panoramica del progetto ed istruzioni per la configurazione.
-   **`LICENSE`**: Termini della licenza MIT del progetto.
-   **`SECURITY.md`**: Policy per la segnalazione di vulnerabilità di sicurezza.
