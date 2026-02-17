import xml.etree.ElementTree as ET
from typing import List, Dict, Any, Tuple
import datetime
from .chord_utils import get_chord_midi_notes

def generate_musicxml(session_data: Dict[str, Any], audio_filename: str, progress_callback=None) -> str:
    root = ET.Element("score-partwise", version="4.0")

    # Work info
    work = ET.SubElement(root, "work")
    ET.SubElement(work, "work-title").text = audio_filename.rsplit('.', 1)[0]

    # Identification
    identification = ET.SubElement(root, "identification")
    encoding = ET.SubElement(identification, "encoding")
    ET.SubElement(encoding, "software").text = "Wavoscope"
    ET.SubElement(encoding, "encoding-date").text = datetime.date.today().isoformat()

    # Part list
    part_list = ET.SubElement(root, "part-list")

    score_part1 = ET.SubElement(part_list, "score-part", id="P1")
    ET.SubElement(score_part1, "part-name").text = "Piano"

    score_part2 = ET.SubElement(part_list, "score-part", id="P2")
    ET.SubElement(score_part2, "part-name").text = "Metronome"

    # Parts
    part_piano = ET.SubElement(root, "part", id="P1")
    part_metro = ET.SubElement(root, "part", id="P2")

    flags = session_data.get("flags", [])
    harmony_flags = session_data.get("harmony_flags", [])
    project_time_sig = session_data.get("time_signature", {"numerator": 4, "denominator": 4})

    rhythm_flags = [f for f in flags if f.get("type") == "rhythm"]

    if not rhythm_flags:
        # Minimal empty score
        _add_measure_piano(part_piano, 1, project_time_sig["numerator"], project_time_sig["denominator"], 120, True, [], 480)
        _add_measure_metro(part_metro, 1, project_time_sig["numerator"], project_time_sig["denominator"], True, 480)
    else:
        divisions = 480
        last_bpm = -1.0
        last_num = -1
        last_den = -1

        for i in range(len(rhythm_flags)):
            if progress_callback:
                progress_callback(i / len(rhythm_flags), f"Exporting measure {i+1} of {len(rhythm_flags)}...")

            start_t = rhythm_flags[i]["t"]
            if i + 1 < len(rhythm_flags):
                end_t = rhythm_flags[i+1]["t"]
            else:
                if i > 0:
                    end_t = start_t + (start_t - rhythm_flags[i-1]["t"])
                else:
                    end_t = start_t + 2.0

            duration = max(0.1, end_t - start_t)

            # Determine Time Signature Numerator from subdivision
            subdiv = rhythm_flags[i].get("subdivision", 0)
            if subdiv == 0:
                subdiv = project_time_sig["numerator"]

            num = subdiv
            den = 4

            # Calculate raw BPM assuming denominator 4
            raw_bpm = (num * 60.0) / duration

            # 2x Tempo logic
            if last_bpm > 0:
                if raw_bpm > 1.7 * last_bpm:
                    den = 8
                    bpm = raw_bpm / 2
                else:
                    den = 4
                    bpm = raw_bpm
            else:
                # First measure
                den = 4
                bpm = raw_bpm

            last_bpm = bpm

            # Rehearsal mark
            rehearsal = None
            if rhythm_flags[i].get("is_section_start"):
                rehearsal = rhythm_flags[i].get("name") or rhythm_flags[i].get("auto_name")

            # Harmony flags in this measure
            measure_harmonies = [h for h in harmony_flags if start_t <= h["t"] < end_t]
            measure_harmonies.sort(key=lambda x: x["t"])

            is_first = (i == 0)
            attr_change = is_first or (num != last_num) or (den != last_den)

            _add_measure_piano(part_piano, i+1, num, den, bpm, attr_change, measure_harmonies, divisions, start_t, end_t, rehearsal)
            _add_measure_metro(part_metro, i+1, num, den, attr_change, divisions)

            last_num = num
            last_den = den

    if progress_callback:
        progress_callback(0.9, "Finalizing XML structure...")
    xml_str = ET.tostring(root, encoding='unicode')

    if progress_callback:
        progress_callback(1.0, "Export complete.")

    return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + \
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n' + \
           xml_str

def _add_measure_piano(part, number, num, den, bpm, attr_change, harmonies, divisions, start_t=0, end_t=0, rehearsal=None):
    measure = ET.SubElement(part, "measure", number=str(number))

    if attr_change:
        attr = ET.SubElement(measure, "attributes")
        ET.SubElement(attr, "divisions").text = str(divisions)
        key = ET.SubElement(attr, "key")
        ET.SubElement(key, "fifths").text = "0"
        time = ET.SubElement(attr, "time")
        ET.SubElement(time, "beats").text = str(num)
        ET.SubElement(time, "beat-type").text = str(den)
        clef = ET.SubElement(attr, "clef")
        ET.SubElement(clef, "sign").text = "G"
        ET.SubElement(clef, "line").text = "2"

    if rehearsal:
        direction = ET.SubElement(measure, "direction", placement="above")
        dir_type = ET.SubElement(direction, "direction-type")
        ET.SubElement(dir_type, "rehearsal").text = rehearsal

    # Tempo
    direction = ET.SubElement(measure, "direction", placement="above")
    dir_type = ET.SubElement(direction, "direction-type")
    metronome = ET.SubElement(dir_type, "metronome")
    ET.SubElement(metronome, "beat-unit").text = "quarter"
    ET.SubElement(metronome, "per-minute").text = str(round(bpm))

    total_dur_div = int(num * divisions * (4 / den))

    if not harmonies:
        note = ET.SubElement(measure, "note")
        ET.SubElement(note, "rest", measure="yes")
        ET.SubElement(note, "duration").text = str(total_dur_div)
        ET.SubElement(note, "voice").text = "1"
    else:
        current_t = start_t
        for idx, h in enumerate(harmonies):
            # Fill gap with rest if any
            if h["t"] > current_t + 0.001:
                gap_ratio = (h["t"] - current_t) / (end_t - start_t)
                gap_div = int(gap_ratio * total_dur_div)
                if gap_div > 0:
                    note = ET.SubElement(measure, "note")
                    ET.SubElement(note, "rest")
                    ET.SubElement(note, "duration").text = str(gap_div)
                    ET.SubElement(note, "voice").text = "1"

            # Add harmony tag
            _add_harmony_tag(measure, h["chord"])

            # Chord duration
            next_t = harmonies[idx+1]["t"] if idx + 1 < len(harmonies) else end_t
            chord_ratio = (next_t - h["t"]) / (end_t - start_t)
            chord_div = int(chord_ratio * total_dur_div)

            if chord_div > 0:
                midi_notes = get_chord_midi_notes(h["chord"])
                for j, midi in enumerate(midi_notes):
                    note = ET.SubElement(measure, "note")
                    if j > 0: ET.SubElement(note, "chord")
                    pitch = ET.SubElement(note, "pitch")
                    step, alter, octave = _midi_to_pitch(midi)
                    ET.SubElement(pitch, "step").text = step
                    if alter != 0: ET.SubElement(pitch, "alter").text = str(alter)
                    ET.SubElement(pitch, "octave").text = str(octave)
                    ET.SubElement(note, "duration").text = str(chord_div)
                    ET.SubElement(note, "voice").text = "1"

            current_t = next_t

def _add_measure_metro(part, number, num, den, attr_change, divisions):
    measure = ET.SubElement(part, "measure", number=str(number))

    if attr_change:
        attr = ET.SubElement(measure, "attributes")
        ET.SubElement(attr, "divisions").text = str(divisions)
        time = ET.SubElement(attr, "time")
        ET.SubElement(time, "beats").text = str(num)
        ET.SubElement(time, "beat-type").text = str(den)
        clef = ET.SubElement(attr, "clef")
        ET.SubElement(clef, "sign").text = "percussion"
        ET.SubElement(clef, "line").text = "2"

    # Add N notes for the metronome
    note_dur = int(divisions * (4 / den))
    for i in range(num):
        note = ET.SubElement(measure, "note")
        unpitched = ET.SubElement(note, "unpitched")
        ET.SubElement(unpitched, "display-step").text = "G"
        ET.SubElement(unpitched, "display-octave").text = "5"
        ET.SubElement(note, "duration").text = str(note_dur)
        ET.SubElement(note, "voice").text = "1"
        ET.SubElement(note, "type").text = "quarter" if den == 4 else "eighth"
        if i == 0:
            ET.SubElement(note, "notehead").text = "x"

def _midi_to_pitch(midi: int) -> Tuple[str, int, int]:
    steps = ['C', 'C', 'D', 'D', 'E', 'F', 'F', 'G', 'G', 'A', 'A', 'B']
    alters = [0, 1, 0, 1, 0, 0, 1, 0, 1, 0, 1, 0]
    step = steps[midi % 12]
    alter = alters[midi % 12]
    octave = (midi // 12) - 1
    return step, alter, octave

def _add_harmony_tag(measure, chord_data):
    harmony = ET.SubElement(measure, "harmony")
    root = ET.SubElement(harmony, "root")
    ET.SubElement(root, "root-step").text = chord_data["root"]
    alter = 0
    if chord_data["accidental"] == "#": alter = 1
    elif chord_data["accidental"] == "b": alter = -1
    if alter != 0:
        ET.SubElement(root, "root-alter").text = str(alter)

    kind = ET.SubElement(harmony, "kind")
    quality = chord_data.get("quality", "M")
    ext = chord_data.get("extension", "")

    kind_val = "major"
    if quality == "m":
        if not ext: kind_val = "minor"
        elif ext == "7": kind_val = "minor-seventh"
        elif ext == "9": kind_val = "minor-ninth"
        elif ext == "11": kind_val = "minor-11th"
        elif ext == "13": kind_val = "minor-13th"
    elif quality == "dim":
        kind_val = "diminished-seventh" if ext == "7" else "diminished"
    elif quality == "aug":
        kind_val = "augmented"
    elif quality == "sus2":
        kind_val = "suspended-second"
    elif quality == "sus4":
        kind_val = "suspended-fourth"
    elif quality == "M":
        if ext == "7": kind_val = "dominant"
        elif ext == "9": kind_val = "dominant-ninth"
        elif ext == "11": kind_val = "dominant-11th"
        elif ext == "13": kind_val = "dominant-13th"

    kind.text = kind_val
    kind.set("text", _format_chord_simple(chord_data))

def _format_chord_simple(c):
    s = c["root"] + c["accidental"]
    if c["quality"] != "M": s += c["quality"]
    s += c["extension"]
    for a in c.get("alterations", []): s += a
    for a in c.get("additions", []): s += a
    if c.get("bass"): s += "/" + c["bass"] + c.get("bass_accidental", "")
    return s
