# Songtext-Transkription und Ausrichtung

Wavoscope bietet eine dedizierte Songtext-Spur für interaktive Transkription, wortgenaue Ausrichtung und MusicXML-Export. Diese Funktion ist für schnelle Eingabe und präzise Zeitanpassung optimiert.

## Grundkonzepte

### Die Songtext-Spur
Die Songtext-Spur ist eine spezialisierte, Canvas-basierte Spur oberhalb der Hauptwellenform. Sie zeigt Songtext-Elemente als bearbeitbare Boxen an.
- **Sichtbarkeit:** Schalten Sie die Spur über die Schaltfläche "Lyrics" im Wellenform-Header ein/aus.
- **Skalierung:** Die Spurhöhe ist fest (32px), aber ihr Inhalt skaliert mit dem globalen Zoom und Scrollen.
- **Auswahl:** Es kann jeweils nur ein Songtext-Element ausgewählt werden. Die Auswahl hebt das Element hervor und aktiviert spezifische Tastenkombinationen.

### Transkriptions-Workflow: "Tippen-Teilen-Weiter"
Der effizienteste Weg, einen Song zu transkribieren, ist dieser Workflow:
1.  **Start:** Drücken Sie `L` oder klicken Sie auf eine leere Stelle, um das erste Element an der aktuellen Abspielposition zu erstellen.
2.  **Tippen:** Geben Sie das erste Wort ein.
3.  **Teilen:** Drücken Sie die `Leertaste` (für neue Wörter) oder `-` (für Silben innerhalb eines Wortes). Dies bestätigt den aktuellen Text und erstellt sofort eine neue Textbox.
    - **Visuelle Differenzierung:** Durch Bindestriche getrennte Wörter (Silben) werden in der Timeline visuell durch eine horizontale Linie verbunden. Der Bindestrich selbst wird in den Daten gespeichert, aber in der Benutzeroberfläche ausgeblendet, wenn er nicht bearbeitet wird, was für ein sauberes Erscheinungsbild sorgt.
4.  **Wiederholen:** Der Fokus springt automatisch in die neue Box, sodass Sie weiterschreiben können, während die Musik läuft.
5.  **Bestätigen:** Drücken Sie `Enter` oder klicken Sie an eine andere Stelle, um die Bearbeitung zu beenden.

## Interaktion und Kürzel

### Maussteuerung
- **Einfachklick (Leerraum):** Fügt einen neuen Songtext an diesem Zeitstempel hinzu und wechselt in den Bearbeitungsmodus.
- **Linksklick (vorhandene Box):** Wählt das Element aus.
- **Einfachklick (ausgewählte Box):** Hebt die Auswahl auf.
- **Ziehen (Mitte 80%):** Verschiebt das Element entlang der Timeline.
- **Ziehen (Ränder 10%):** Passt die Dauer an. Das Ziehen des linken Randes ändert den Startzeitpunkt, der rechte Rand ändert die Dauer.
- **Doppelklick:** Wechselt direkt in den Bearbeitungsmodus für dieses Element.
- **Klick auf Hintergrund:** Hebt die aktuelle Auswahl auf.

### Tastenkombinationen

| Taste | Aktion | Kontext |
|-------|--------|----------|
| `L` | Hinzufügen / Bestätigen & Weiter | Global |
| `Umschalt + L` | Alles abwählen | Global |
| `Tab` | Loop-Modi durchlaufen | Global |
| `Enter` | Bearbeitung starten/beenden | Ausgewählt |
| `Esc` | Bearbeitung abbrechen / Abwählen | Ausgewählt |
| `Pfeiltasten (Links/Rechts)` | Position anpassen (0,1s) | Ausgewählt (Nicht im Editiermodus) |
| `Pfeiltasten (Oben/Unten)` | Dauer anpassen (0,1s) | Ausgewählt (Nicht im Editiermodus) |
| `Umschalt + Pfeiltasten` | Zwischen Lyrics springen | Global / Ausgewählt |
| `Leertaste / -` | Bestätigen & Nächstes erstellen | Beim Editieren |

## Technische Implementierung

### Frontend
- **`LyricsTimeline.tsx`**: Verwendet ein Ref-basiertes Zustandsmanagement, um hochfrequente Interaktionen (Ziehen) lokal zu verarbeiten, bevor sie an das Backend gesendet werden. Nutzt einen `ResizeObserver` für reaktive Canvas-Darstellung.
- **Zustandsmanagement**: Integriert in `projectSlice.ts`. CRUD-Operationen sind optimiert, um den lokalen Zustand direkt aus den Backend-Antworten zu aktualisieren (Minimierung von Latenz).
- **Visualisierung**: Verfügt über eine dynamische Rendering-Engine, die Textkürzungen und Ausblendungen für kleine Elemente handhabt.

### Backend
- **Datenstruktur**: Lyrics werden als sortierte Liste von Objekten `{text, timestamp, duration}` in der `.oscope`-Datei gespeichert.
- **Loop-Engine**: Die `LoopingEngine` unterstützt einen `lyric`-Modus, der den Loop-Bereich automatisch auf das aktuell ausgewählte Element setzt.
- **MusicXML-Export**: `session/export.py` teilt Takte an jeder Songtext- und Harmonie-Grenze in Segmente auf. Dies stellt sicher, dass `<lyric>`-Tags in der exportierten Partitur perfekt mit der rhythmischen Struktur übereinstimmen.

## Tipps zur Ausrichtung
- **Hoher Zoom:** Vergrößern Sie die Wellenform so weit, dass Sie Transienten (Anschläge) deutlich sehen können.
- **Loops:** Nutzen Sie den `lyric` Loop-Modus (umschalten mit `Tab`), um das aktuelle Wort zu wiederholen, während Sie Start- und Endpunkte anpassen.
- **Metronom:** Lassen Sie die Unterteilungsklicks an, um sicherzustellen, dass Ihre Lyrics mit dem zugrundeliegenden Beat (Rhythmus-Markierungen) übereinstimmen.
