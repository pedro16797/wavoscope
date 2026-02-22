<p align="center">
  <img src="resources/icons/WavoscopeLogo.svg" alt="Wavoscope Logo" width="256">
</p>

# Wavoscope - Audioanalyse- und Transkriptionstool

Wavoscope ist ein leistungsstarkes Echtzeit-Audiovisualisierungs- und Transkriptionstool, das für Musiker, Transkriptoren und Toningenieure entwickelt wurde. Es bietet High-Fidelity-Wellenformen, Spektralanalyse und ein robustes Markierungssystem, um Sie bei der Dekonstruktion komplexer Audioinhalte zu unterstützen.

![Hauptoberfläche](docs/images/main_view.png)

---

## 🚀 Erste Schritte

### Projektmanagement
Wavoscope verwendet ein "Sidecar"-Dateisystem. Wenn Sie eine Audiodatei öffnen, erstellt oder lädt Wavoscope eine `.oscope`-Datei im selben Verzeichnis, um Ihre Markierungen, Loops und Einstellungen zu speichern.
- **Öffnen:** Klicken Sie auf das Ordnersymbol in der Wiedergabeleiste, um ein beliebiges gängiges Audioformat (MP3, WAV, FLAC usw.) zu laden.
- **Speichern:** Klicken Sie auf das Disketten-Symbol. Das Symbol leuchtet in der Akzentfarbe Ihres Designs, wenn ungespeicherte Änderungen vorliegen.

---

## 🎵 Navigation & Wiedergabe

- **Zoomen:** Verwenden Sie das **Mausrad** über der Wellenform oder dem Spektrum, um hinein- oder herauszuzoomen.
- **Scrollen:** Verwenden Sie das **Mausrad** über der **Timeline**, um in der Zeit vor- oder zurückzuspringen.
- **Verschieben:** **Klicken und ziehen** Sie die Wellenform oder das Spektrum, um sich durch die Timeline zu bewegen.
- **Adaptive Unterteilungen:** Die Timeline passt ihre Gitterschritte automatisch an (von 0,01s bis zu mehreren Stunden), wenn Sie zoomen. Dies gewährleistet optimale Detailtiefe ohne Überfüllung.
- **Abspielposition:** **Linksklick** auf die Wellenform, um die Abspielposition zu verschieben.
- **Geschwindigkeitssteuerung:** Verwenden Sie den Schieberegler in der unteren Leiste, um die Geschwindigkeit von 0,1x bis 2,0x anzupassen. Wavoscope verwendet hochwertiges Time-Stretching, das die Tonhöhe (Pitch) beibehält.

---

## 🔍 Spektralanalyse & Filterung

Die untere Hälfte des Bildschirms zeigt ein Constant-Q-Transform (CQT) Spektrogramm, das auf eine Klaviatur abgebildet ist. Sie können das **FFT-Fenster** und die **Oktavverschiebung** über die Steuerelemente im Header des Spektralanalysators anpassen.

![Spektralfilterung](docs/images/spectrum_filter.png)

### Fortgeschrittene Filterung
Sie können bestimmte Instrumente oder Noten mit dem Echtzeit-Bandpassfilter isolieren. Die Filtergriffe (vertikale Linien im Spektrum) sind immer verfügbar:
- **Cutoff umschalten:** **Rechtsklick** auf einen Filtergriff, um diese Grenze zu aktivieren oder zu deaktivieren.
- **Schnellplatzierung:** **Rechtsklick** an eine beliebige Stelle im Spektrogramm, um den nächstgelegenen Filtergriff dorthin zu bewegen und zu aktivieren.
- **Visuelles Feedback:** Wenn ein Cutoff aktiviert ist, wird der Bereich außerhalb seines Bereichs abgedunkelt, um Ihnen die Konzentration zu erleichtern. Wenn beide deaktiviert sind, wird der Filter umgangen.

---

## 🚩 Markierungen & Transkription

Wavoscope verwendet ein duales Markierungssystem, um Ihnen bei der Kartierung der Struktur und Harmonie eines Tracks zu helfen.

### Rhythmus-Markierungen (Takt-Markierungen)
- **Platzierung:** Drücken Sie `B` (Standard) oder **Linksklick** auf die Timeline, um eine Rhythmus-Markierung zu setzen.
- **Unterteilungen:** Öffnen Sie den Markierungsdialog (**Rechtsklick** auf den Markierungsgriff), um Unterteilungen festzulegen (z. B. 4 für Viertelnoten). Diese erscheinen als schwache vertikale Linien in der Timeline.
- **Metronom:** Rhythmus-Markierungen lösen während der Wiedergabe automatisch einen Metronom-Klick aus, wenn Unterteilungsklicks aktiviert sind.
- **Umschalt-Klick:** Platziert automatisch eine neue Flagge im gleichen Intervall wie die vorherige, ideal zum schnellen Zuordnen eines regelmäßigen Schlags.
- **Abschnitte:** Markieren Sie eine Markierung als "Abschnittsbeginn", um ihr ein Label zu geben (wie "Strophe" oder "Refrain").

![Rhythmus-Markierungsdialog](docs/images/rhythm_dialog.png)

### Harmonie-Markierungen (Akkord-Markierungen)
- **Platzierung:** Drücken Sie `H` (Standard) oder **Rechtsklick** auf die Timeline, um eine Harmonie-Markierung zu setzen.
- **Akkord-Editor:** **Rechtsklick** auf eine vorhandene Markierung, um den Akkord-Dialog zu öffnen. Sie können Akkordnamen eingeben (z. B. "Am7", "C/G") oder die Selektoren verwenden.
- **Automatische Analyse:** Verwenden Sie die Schaltfläche **Vorschlagen**, damit Wavoscope das Audio an dieser Position analysiert und den wahrscheinlichsten Akkord empfiehlt.
- **Anhören:** **Halten Sie den Linksklick** auf einen Harmonie-Markierungsgriff oder klicken Sie auf die Schaltfläche "Play" im Dialog, um den Akkord über den internen Synthesizer zu hören.

![Harmonie-Markierungsdialog](docs/images/harmony_dialog.png)

### Markierungen verwalten
- **Ziehen:** Sie können jeden Markierungsgriff in der Timeline **anklicken und ziehen**, um seine Position fein abzustimmen.
- **Überlappungen:** Wenn eine Rhythmus- und eine Harmonie-Markierung denselben Platz einnehmen, werden sie in halber Höhe angezeigt (Harmonie oben, Rhythmus unten), sodass Sie weiterhin mit beiden interagieren können.
- **Looping:** Verwenden Sie die Loop-Schaltfläche in der Wiedergabeleiste, um zwischen Markierungen oder dem gesamten Track zu wechseln.

---

## 🎤 Songtext-Transkription

Wavoscope verfügt über eine interaktive Songtext-Spur, die eine schnelle Transkription und Ausrichtung ermöglicht.

![Songtext-Transkription](docs/images/lyrics_track.png)

### Transkriptions-Workflow
1. **Spur umschalten:** Klicken Sie auf die Schaltfläche "Lyrics" im Header der Wellenform, um die Transkriptionsspur anzuzeigen.
2. **Hinzufügen & Tippen:** Drücken Sie `L` oder machen Sie einen **Einfachklick** auf eine leere Stelle in der Songtext-Spur, um ein Wort hinzuzufügen.
3. **Schnelleingabe:** Während Sie in ein Textfeld tippen, drücken Sie die **Leertaste** oder den **Bindestrich (`-`)**. Dies wird automatisch:
    - Das aktuelle Wort bestätigen.
    - Ein neues Textfeld direkt im Anschluss erstellen (an der aktuellen Abspielposition oder dem vorherigen Ende).
    - Den Fokus auf das neue Feld verschieben, sodass Sie weiter tippen können, ohne die Musik anzuhalten.
4. **Springen:** Verwenden Sie `Umschalt + Links/Rechts`, um zwischen Songtext-Elementen zu springen. Dies ist perfekt zum Überprüfen des Timings.

### Bearbeiten & Größe anpassen
- **Verschieben:** **Ziehen** Sie die Mitte (80%) eines Textfeldes, um es zu verschieben.
- **Timing:** **Ziehen** Sie die Ränder (10% Schwellenwert) eines Textfeldes, um dessen Start- oder Endzeit anzupassen.
- **Präzision:** Verwenden Sie die **Pfeiltasten**, wenn ein Songtext ausgewählt ist, um ihn um 0,1s zu verschieben. Verwenden Sie **Auf/Ab**, um die Dauer anzupassen.
- **Formatierung:** Textfelder werden automatisch ausgeblendet oder maskiert, wenn sie bei niedrigen Zoomstufen zu klein werden, um die Benutzeroberfläche sauber zu halten.

---

## ⚙️ Einstellungen & Anpassung

![Einstellungsdialog](docs/images/settings_dialog.png)

Greifen Sie über das Zahnradsymbol in der Wiedergabeleiste auf die Einstellungen zu:
- **Sichtbare Klaviertasten:** Passen Sie an, wie viele Tasten im Piano Roll des Spektrums angezeigt werden.
- **Klick-Lautstärke:** Steuern Sie die Lautstärke der Metronom-Unterteilungen.

### Designs (Themes)
Wavoscope ist vollständig anpassbar. Wählen Sie einen Look, der zu Ihrer Umgebung passt:
- **Cosmic:** Tiefe Purpurtöne und nebulöse Akzente.
- **Dark:** Klassischer, augenschonender Dunkelmodus.
- **Doll:** Energetisches Pink und spielerische Töne.
- **Hacker:** Retro-Terminal-Grün auf Schwarz.
- **Light:** Sauberer, heller professioneller Look.
- **Neon:** Elektrisches Blau und kontrastreicher Vibe.
- **OLED:** Rein schwarzer Hintergrund für maximalen Kontrast.
- **Retrowave:** 80er-Jahre Synthwave-Ästhetik.
- **Toy:** Kräftige Primärfarben.
- **Warm:** Erdige, angenehme Töne für lange Sitzungen.


---

## 🌍 Lokalisierung

Wavoscope unterstützt mehrere Sprachen. Sie können die Sprache im Tab **Einstellungen > Global** ändern.

### Benutzerdefinierte Übersetzungen
Wavoscope ist so konzipiert, dass es von der Community getragen wird. Sie können Übersetzungen hinzufügen oder ändern, indem Sie die JSON-Dateien im Verzeichnis `resources/locales` bearbeiten.
- Um eine neue Sprache hinzuzufügen, erstellen Sie eine neue JSON-Datei (z. B. `fr.json`) und fügen Sie ein Feld `"meta": { "name": "Français" }` hinzu.
- Die App erkennt und listet automatisch jede gültige Übersetzungsdatei im Einstellungsmenü auf.

---

## ⌨️ Umfassende Steuerung

### Tastenkombinationen
| Aktion | Taste |
| :--- | :--- |
| **Wiedergabe / Pause** | `Leertaste` |
| **Vorwärts/Rückwärts springen** | `Links` / `Rechts` |
| **Geschwindigkeit +/-** | `Oben` / `Unten` |
| **Rhythmus-Markierung** | `B` |
| **Harmonie-Markierung** | `H` |
| **Songtext hinzufügen/bestätigen** | `L` |
| **Teilen & Weiter (Lyrics)**| `Leertaste` / `-` (Im Eingabefeld) |
| **Loop-Modi durchlaufen** | `Tab` |
| **Auswahl aufheben** | `Umschalt + L` |
| **Zwischen Lyrics springen** | `Umschalt + Links/Rechts` |
| **Element löschen** | `Entf` / `Rücktaste` |
| **Datei öffnen** | `Strg + O` |
| **Projekt speichern** | `Strg + S` |

### Maus-Interaktionen
| Bereich | Aktion | Interaktion |
| :--- | :--- | :--- |
| **Timeline** | Rhythmus-Markierung | `Linksklick` |
| **Timeline** | Rhythmus-Flag automatisch platzieren | `Umschalt + Linksklick` |
| **Timeline** | Harmonie-Markierung | `Rechtsklick` |
| **Timeline** | Markierung verschieben | `Links ziehen` |
| **Timeline** | Harmonie anhören | `Linksklick halten` auf Markierung |
| **Timeline** | Ansicht scrollen | `Mausrad` |
| **Wellenform** | Abspielposition verschieben | `Linksklick` |
| **Wellenform** | Ansicht verschieben | `Links ziehen` |
| **Wellenform** | Ein-/Auszoomen | `Mausrad` |
| **Spektrum** | Sinuston spielen | `Linksklick / ziehen` |
| **Spektrum** | Cutoff umschalten | `Rechtsklick` auf Griff |
| **Spektrum** | Cutoff platzieren | `Rechtsklick` irgendwo |
| **Spektrum** | Cutoff anpassen | `Links ziehen` am Griff |
