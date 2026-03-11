<p align="center">
  <img src="resources/icons/WavoscopeLogo.svg" alt="Wavoscope Logo" width="256">
</p>

# Wavoscope - Strumento di Analisi e Trascrizione Audio

Wavoscope è un potente strumento di visualizzazione audio in tempo reale e aiuto alla trascrizione, progettato per musicisti, trascrittori ed ingegneri del suono. Offre forme d'onda ad alta fedeltà, analisi spettrale e un robusto sistema di marcatori per aiutarti a deconstruire flussi audio complessi.

![Interfaccia Principale](docs/images/main_view.png)

---

## 🚀 Per Iniziare

### Avvio di Wavoscope
Wavoscope è progettato per essere autonomo. Non è necessario installare Python o altre dipendenze manualmente.
- **Windows:** Fai doppio clic su `run.bat`. Questo configurerà automaticamente l'ambiente e creerà un file `Wavoscope.exe` nella cartella principale per l'uso futuro.
- **Linux/macOS:** Esegui `bash run.sh` nel tuo terminale. Questo creerà un binario `Wavoscope` nella cartella principale.

### Sviluppo e Test
Se stai eseguendo dal codice sorgente e vuoi eseguire i test:
- **Test Backend:** `PYTHONPATH=src python3 -m pytest src/tests`
- **Test Frontend:** `cd src/frontend && npm test`

Al primo avvio, Wavoscope scaricherà automaticamente il proprio runtime Python e configurerà l'ambiente necessario. L'operazione potrebbe richiedere alcuni minuti a seconda della connessione Internet. Dopo il primo avvio, potrai semplicemente usare l'eseguibile `Wavoscope` generato (con l'icona dell'applicazione).

### Gestione Progetto & Salvataggi Automatici
Wavoscope utilizza un sistema di file "sidecar". Quando apri un file audio, Wavoscope crea o carica un file `.oscope` nella stessa directory per memorizzare i tuoi marcatori, loop e impostazioni.
- **Apri:** Clicca sull'icona della cartella nella barra di riproduzione per caricare qualsiasi formato audio comune (MP3, WAV, FLAC, ecc.).
- **Salva:** Clicca sull'icona del floppy disk. L'icona si illuminerà con il colore di accento del tuo tema quando ci sono modifiche non salvate.
- **Salvataggio automatico:** Wavoscope crea automaticamente istantanee del tuo lavoro a intervalli regolari. Puoi configurare la frequenza del salvataggio automatico, il numero massimo di istantanee da conservare e la posizione di archiviazione nella scheda **Impostazioni > Salvataggio automatico**. Per impostazione predefinita, i salvataggi avvengono solo se ci sono modifiche non salvate. Puoi abilitare il **Salvataggio forzato** per creare sempre istantanee indipendentemente dalle modifiche. Per impostazione predefinita, i salvataggi automatici sono memorizzati nella cartella temporanea del tuo sistema.

---

## 🎵 Navigazione e Riproduzione

- **Zoom:** Usa la **rotella del mouse** sulla forma d'onda o sullo spettro per ingrandire o rimpicciolire.
- **Scorrimento:** Usa la **rotella del mouse** sulla **timeline** per scorrere avanti o indietro nel tempo.
- **Panoramica:** **Clicca e trascina** la forma d'onda o lo spettro per spostarti lungo la timeline.
- **Suddivisioni Adattive:** La timeline regola automaticamente i passi della griglia (da 0.01s a diverse ore) mentre esegui lo zoom, garantendo il miglior dettaglio senza affollamento visivo.
- **Cursore di Riproduzione:** **Clic sinistro** sulla forma d'onda per spostare la testina di riproduzione.
- **Controllo Velocità:** Usa lo slider nella barra inferiore per regolare la velocità da 0.1x a 2.0x. Wavoscope utilizza un algoritmo di time-stretching di alta qualità che preserva l'intonazione (pitch).
- **Volume & Overdrive:** Regola il volume generale con il cursore. Clicca sull'**icona del volume** o premi `G` per attivare la **modalità Overdrive**, che estende l'intervallo di volume dal 100% al 400%. L'app ricorda livelli di volume separati per le modalità normale e overdrive.
- **Tempo e Tap Tempo:** Il tempo attuale (in BPM) è visualizzato nell'intestazione della forma d'onda. Fare clic ripetutamente per misurare manualmente il tempo (**Tap Tempo**). Torna automaticamente al tempo misurato dopo 3 secondi di inattività.

---

## 🔍 Analisi Spettrale e Filtraggio

La metà inferiore dello schermo mostra uno spettrogramma a trasformata Q costante (CQT), mappato su una tastiera di pianoforte. Puoi regolare la **finestra FFT** e lo **spostamento d'ottava** usando i controlli nell'intestazione dell'analizzatore di spettro.

![Filtraggio Spettrale](docs/images/spectrum_filter.png)

### Filtraggio Avanzato
Puoi isolare strumenti o note specifiche usando il filtro passa-banda in tempo reale. Le maniglie del filtro (linee verticali sullo spettro) sono sempre disponibili:
- **Attiva/Disattiva Taglio:** **Clic destro** su una maniglia del filtro per abilitare o disabilitare quel limite.
- **Posizionamento Rapido:** **Clic destro** in qualsiasi punto dello spettrogramma per spostare la maniglia del filtro più vicina e abilitarla.
- **Feedback Visivo:** Quando un taglio è abilitato, l'area esterna al suo intervallo viene oscurata per aiutarti a concentrarti. Se entrambi sono disabilitati, il filtro viene bypassato.

---

## 🚩 Marcatori e Trascrizione

Wavoscope utilizza un sistema a doppio marcatore per aiutarti a mappare la struttura e l'armonia di un brano.

### Marcatori di Ritmo (Misure/Battute)
- **Posizionamento:** Premi `B` (predefinito) o fai **clic sinistro** sulla timeline per inserire un marcatore di ritmo.
- **Suddivisioni:** Apri il dialogo del marcatore (**clic destro** sulla maniglia) per impostare le suddivisioni (es. 4 per i quarti). Queste appaiono come sottili linee verticali sulla timeline.
- **Metronomo:** I marcatori di ritmo attivano automaticamente un clic del metronomo durante la riproduzione se i clic di suddivisione sono abilitati.
- **Maiusc + Clic:** Posiziona automaticamente un nuovo marcatore allo stesso intervallo del precedente, perfetto per mappare rapidamente un ritmo regolare.
- **Sezioni:** Imposta un marcatore come "Inizio Sezione" per dargli un'etichetta (come "Strofa" o "Ritornello").

![Dialogo Marcatore Ritmo](docs/images/rhythm_dialog.png)

### Marcatori di Armonia (Accordi)
- **Posizionamento:** Premi `C` (predefinito) o fai **clic destro** sulla timeline per inserire un marcatore di armonia.
- **Editor Accordi:** **Clic destro** su un marcatore esistente per aprire il dialogo degli accordi. Puoi digitare i nomi degli accordi (es. "Am7", "C/G") o usare i selettori.
- **Analisi Automatica:** Usa il pulsante **Suggerisci** per lasciare che Wavoscope analizzi l'audio in quella posizione e raccomandi l'accordo più probabile.
- **Ascolto:** **Tieni premuto il clic sinistro** sulla maniglia di un marcatore di armonia o clicca sul pulsante "Play" nel dialogo per ascoltare l'accordo tramite il sintetizzatore interno.

![Dialogo Marcatore Armonia](docs/images/harmony_dialog.png)

### Gestione dei Marcatori
- **Trascinamento:** Puoi **cliccare e trascinare** qualsiasi maniglia di marcatore sulla timeline per affinarne la posizione.
- **Sovrapposizioni:** Quando un marcatore di Ritmo e uno di Armonia occupano lo stesso spazio, vengono visualizzati a mezza altezza (Armonia sopra, Ritmo sotto) in modo da poter interagire con entrambi.
- **Loop:** Usa il pulsante Loop nella barra di riproduzione per passare tra i marcatori o l'intero brano.

---

## 🎤 Trascrizione del Testo

Wavoscope include una traccia interattiva per i testi che permette una trascrizione e un allineamento ad alta velocità.

![Trascrizione Testo](docs/images/lyrics_track.png)

### Flusso di Lavoro per la Trascrizione
1. **Attiva Traccia:** Clicca sul pulsante "Testo" nell'intestazione della forma d'onda per mostrare la traccia di trascrizione.
2. **Aggiungi e Digita:** Premi `V` o fai un **singolo clic** in uno spazio vuoto della traccia per aggiungere una parola.
3. **Inserimento Rapido:** Mentre digiti in una casella di testo, premi **Spazio** o **Trattino (`-`)**. Questo avverrà automaticamente:
    - Conferma la parola corrente.
    - Crea una nuova casella di testo immediatamente dopo (alla posizione attuale o alla fine della precedente).
    - Sposta il focus sulla nuova casella così puoi continuare a digitare senza fermare la musica.
4. **Navigazione:** Usa `Maiusc + Sinistra/Destra` / `Maiusc \+ A/D` per saltare tra gli elementi del testo. Perfetto per verificare il timing.

### Modifica e Ridimensionamento
- **Spostamento:** **Trascina** il centro (80%) di una casella di testo per spostarla.
- **Timing:** **Trascina** i bordi (soglia del 10%) di una casella di testo per regolare l'inizio o la fine.
- **Precisione:** Usa le **frecce della tastiera** quando un testo è selezionato per spostarlo di 0.1s. Usa le frecce **Su/Giù** per regolare la durata.
- **Formattazione:** Le caselle di testo sfumano e nascondono il testo automaticamente quando diventano troppo piccole a bassi livelli di zoom, mantenendo l'interfaccia pulita.

---

## ⚙️ Impostazioni e Personalizzazione

![Dialogo Impostazioni](docs/images/settings_dialog.png)

Accedi alle impostazioni tramite l'icona dell'ingranaggio nella barra di riproduzione:
- **Tasti Piano Visibili:** Regola quanti tasti vengono mostrati nella tastiera dello spettro.
- **Volume Clic:** Controlla il volume delle suddivisioni del metronomo.

### Temi
Wavoscope è completamente personalizzabile tramite i temi. Scegli lo stile che preferisci:
- **Cosmic:** Viola profondo e accenti nebulosi.
- **Dark:** Modalità scura classica, riposante per gli occhi.
- **Doll:** Rosa energico e toni giocosi.
- **Hacker:** Verde terminale retrò su nero.
- **Light:** Aspetto professionale pulito e ad alta luminosità.
- **Neon:** Blu elettrico e vibrazioni ad alto contrasto.
- **OLED:** Sfondo nero puro per il massimo contrasto.
- **Retrowave:** Estetica synthwave anni '80.
- **Toy:** Colori primari vivaci.
- **Warm:** Toni caldi e naturali per sessioni prolungate.


---

## 🌍 Localizzazione

Wavoscope supporta diverse lingue. Puoi cambiare la lingua nella scheda **Impostazioni > Globale**.

### Traduzioni Personalizzate
Wavoscope è progettato per essere guidato dalla comunità. Puoi aggiungere o modificare le traduzioni modificando i file JSON nella cartella `resources/locales`.
- Per aggiungere una nuova lingua, crea un nuovo file JSON (es. `fr.json`) e aggiungi un campo `"meta": { "name": "Français" }`.
- L'applicazione rileverà ed elencherà automaticamente ogni file di traduzione valido nel menu delle impostazioni.

---

## ⌨️ Comandi Completi

### Scorciatoie da Tastiera
| Azione | Tasto |
| :--- | :--- |
| **Riproduci / Pausa** | `Spazio` |
| **Interrompi riproduzione** | `Maiusc + Spazio` |
| **Attiva Metronomo** | `M` |
| **Attiva Impostazioni** | `Esc` |
| **Salta Avanti/Indietro** | `Sinistra` / `Destra` / `A` / `D` |
| **Aumenta/Diminuisci Velocità** | `Su` / `Giù` / `W` / `S` |
| **Alza/Abbassa Ottava** | `Maiusc + Sinistra/Destra` / `Maiusc \+ A/D` |
| **Dimensione finestra FFT** | `Maiusc + Su/Giù` / `Maiusc \+ W/S` |
| **Aggiungi Marcatore Ritmo** | `B` |
| **Aggiungi Marcatore Armonia** | `C` |
| **Attiva passa-basso** | `F` |
| **Attiva passa-alto** | `Maiusc + F` |
| **Aggiungi/Conferma Testo** | `V` |
| **Dividi e Avanza Testo**| `Spazio` / `-` (Dentro l'input) |
| **Cicla Modalità Loop** | `Tab` |
| **Deseleziona Tutto** | `Maiusc + V` |
| **Salta tra i Testi** | `Maiusc + Sinistra/Destra` / `Maiusc \+ A/D` |
| **Elimina Elemento** | `Canc` / `Backspace` |
| **Apri File** | `Ctrl + O` |
| **Salva Progetto** | `Ctrl + S` |
| **Esporta MusicXML** | `Ctrl + E` |

### Interazioni Mouse
| Area | Azione | Interazione |
| :--- | :--- | :--- |
| **Timeline** | Aggiungi Marcatore Ritmo | `Clic Sinistro` |
| **Timeline** | Posizionamento Auto Marcatore Ritmo | `Maiusc + Clic Sinistro` |
| **Timeline** | Aggiungi Marcatore Armonia | `Clic Destro` |
| **Timeline** | Sposta Marcatore | `Trascina Sinistro` |
| **Timeline** | Ascolta Accordo | `Tieni Premuto Clic Sinistro` |
| **Timeline** | Scorrimento Vista | `Rotella Mouse` |
| **Forma d'Onda** | Sposta Testina | `Clic Sinistro` |
| **Forma d'Onda** | Panoramica Vista | `Trascina Sinistro` |
| **Forma d'Onda** | Zoom | `Rotella Mouse` |
| **Spettro** | Suona Nota Sinusoidale | `Clic / Trascina Sinistro` |
| **Spettro** | Attiva/Disattiva Taglio | `Clic Destro` maniglia |
| **Spettro** | Posiziona Taglio | `Clic Destro` ovunque |
| **Spettro** | Regola Taglio | `Trascina Sinistro` maniglia |
