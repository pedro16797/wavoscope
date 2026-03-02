# Trascrizione ed Allineamento del Testo

Wavoscope offre una traccia dedicata per i testi per la trascrizione interattiva, l'allineamento a livello di parola e l'esportazione MusicXML. Questa funzione è progettata per un inserimento rapido e una regolazione precisa del tempo.

## Concetti Fondamentali

### La Traccia del Testo
La traccia del testo è una traccia specializzata basata su canvas situata sopra la forma d'onda principale. Mostra gli elementi del testo come caselle modificabili.
- **Visibilità:** Attiva la traccia usando il pulsante "Testo" nell'intestazione della forma d'onda.
- **Scala:** L'altezza della traccia è fissa (32px), ma il suo contenuto si adatta allo zoom e allo scorrimento globale.
- **Selezione:** È possibile selezionare solo un testo alla volta. Selezionando un elemento, questo viene evidenziato e vengono attivate scorciatoie specifiche.

### Flusso di Lavoro: "Digita-Dividi-Avanza"
Il modo più efficiente per trascrivere una canzone è seguire questo flusso:
1.  **Inizio:** Premi `V` o clicca su uno spazio vuoto per creare il primo testo alla posizione attuale.
2.  **Digita:** Inserisci la prima parola.
3.  **Dividi:** Premi `Spazio` (per nuove parole) o `-` (per sillabe all'interno di una parola). Questo conferma il testo corrente e crea immediatamente una nuova casella.
    - **Differenziazione visiva:** Le parole divise da trattini (sillabe) sono collegate visivamente da una linea orizzontale nella timeline. Il trattino stesso viene memorizzato nei dati ma nascosto nell'interfaccia utente quando non è in fase di modifica, offrendo un aspetto pulito.
4.  **Ripeti:** Il focus si sposta automaticamente sulla nuova casella, permettendoti di continuare a trascrivere mentre la musica suona.
5.  **Conferma:** Premi `Invio` o clicca altrove per terminare la modifica.

## Interazioni e Scorciatoie

### Controllo Mouse
- **Singolo Clic (spazio vuoto):** Aggiunge un nuovo testo a quel timestamp ed entra in modalità modifica.
- **Clic Sinistro (casella esistente):** Seleziona il testo.
- **Singolo Clic (casella selezionata):** Deseleziona il testo.
- **Trascinamento (centro 80%):** Sposta l'elemento lungo la timeline.
- **Trascinamento (bordi 10%):** Ridimensiona il testo. Trascinare il bordo sinistro regola l'inizio; trascinare il bordo destro regola la durata.
- **Doppio Clic:** Entra in modalità modifica per il testo cliccato.
- **Clic sullo Sfondo:** Deseleziona il testo corrente.

### Scorciatoie da Tastiera

| Tasto | Azione | Contesto |
|-------|--------|----------|
| `V` | Aggiungi / Conferma ed Avanza | Globale |
| `Maiusc + V` | Deseleziona Tutto | Globale |
| `Tab` | Cicla Modalità Loop | Globale |
| `Invio` | Inizia/Termina Modifica | Selezionato |
| `Esc` | Annulla Modifica / Deseleziona | Selezionato |
| `Frecce / `A` / `D` / `W` / `S` (Sinistra/Destra)` | Regola Posizione (0.1s) | Selezionato (Non in modifica) |
| `Frecce / `A` / `D` / `W` / `S` (Su/Giù)` | Regola Durata (0.1s) | Selezionato (Non in modifica) |
| `Maiusc + Frecce / `A` / `D` / `W` / `S`` | Salta tra i Testi | Globale / Selezionato |
| `Spazio / -` | Conferma e Genera Successivo | In modifica |

## Implementazione Tecnica

### Frontend
- **`LyricsTimeline.tsx`**: Utilizza un sistema di gestione dello stato basato su riferimenti per gestire le interazioni ad alta frequenza (trascinamento) localmente prima della conferma al backend. Utilizza un `ResizeObserver` per il rendering reattivo del canvas.
- **Gestione dello Stato**: Integrata in `projectSlice.ts`. Le operazioni CRUD sono ottimizzate per aggiornare lo stato locale direttamente dalle risposte del backend, minimizzando il traffico di rete.
- **Visualizzazione**: Dispone di un motore di rendering dinamico che gestisce il troncamento e la sfumatura del testo per gli elementi piccoli.

### Backend
- **Struttura Dati**: I testi sono memorizzati come una lista ordinata di oggetti `{text, timestamp, duration}` nel file `.oscope`.
- **Motore di Loop**: Il `LoopingEngine` supporta una modalità `lyric`, che imposta automaticamente l'intervallo del loop sul testo attualmente selezionato.
- **Esportazione MusicXML**: `src/session/export.py` divide le misure in segmenti ad ogni limite di testo e armonia. Questo garantisce che i tag `<lyric>` siano perfettamente allineati con la struttura ritmica nella partitura esportata.

## Consigli per l'Allineamento
- **Zoom Elevato:** Per l'allineamento a livello di parola, aumenta lo zoom finché non vedi chiaramente i transienti nella forma d'onda.
- **Loop:** Usa la modalità loop `lyric` (cambia con `Tab`) per ripetere la parola corrente mentre regoli i punti di inizio e fine.
- **Metronomo:** Mantieni i clic di suddivisione attivi per assicurarti che i testi siano allineati con i marcatori di battuta sottostanti (Marcatori di Ritmo).
