import xml.etree.ElementTree as ET
from typing import List, Dict, Any
import datetime

def generate_musicxml(session_data: Dict[str, Any], audio_filename: str) -> str:
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
    score_part = ET.SubElement(part_list, "score-part", id="P1")
    ET.SubElement(score_part, "part-name").text = "Transcription"

    # Part
    part = ET.SubElement(root, "part", id="P1")

    flags = session_data.get("flags", [])
    harmony_flags = session_data.get("harmony_flags", [])
    time_sig = session_data.get("time_signature", {"numerator": 4, "denominator": 4})
    num = time_sig.get("numerator", 4)
    den = time_sig.get("denominator", 4)

    rhythm_flags = [f for f in flags if f.get("type") == "rhythm"]
    if not rhythm_flags:
        # Default empty measure if no rhythm flags
        _add_empty_measure(part, 1, num, den, 120, True)
    else:
        last_tempo = -1.0
        divisions = 480

        for i in range(len(rhythm_flags)):
            start_t = rhythm_flags[i]["t"]

            if i + 1 < len(rhythm_flags):
                end_t = rhythm_flags[i+1]["t"]
            else:
                if i > 0:
                    end_t = start_t + (start_t - rhythm_flags[i-1]["t"])
                else:
                    end_t = start_t + 2.0

            duration = end_t - start_t
            if duration <= 0: duration = 1.0

            bpm = (num * 60.0) / duration

            measure = ET.SubElement(part, "measure", number=str(i + 1))

            if i == 0:
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

            if rhythm_flags[i].get("is_section_start"):
                rehearsal_text = rhythm_flags[i].get("name") or rhythm_flags[i].get("auto_name")
                if rehearsal_text:
                    direction = ET.SubElement(measure, "direction", placement="above")
                    dir_type = ET.SubElement(direction, "direction-type")
                    ET.SubElement(dir_type, "rehearsal").text = rehearsal_text

            if abs(bpm - last_tempo) > 5:
                direction = ET.SubElement(measure, "direction", placement="above")
                dir_type = ET.SubElement(direction, "direction-type")
                metronome = ET.SubElement(dir_type, "metronome")
                ET.SubElement(metronome, "beat-unit").text = "quarter"
                ET.SubElement(metronome, "per-minute").text = str(round(bpm))
                last_tempo = bpm

            measure_harmonies = [h for h in harmony_flags if start_t <= h["t"] < end_t]
            measure_harmonies.sort(key=lambda x: x["t"])

            total_measure_div = num * divisions

            for h in measure_harmonies:
                h_t = h["t"]
                h_offset_ratio = (h_t - start_t) / duration
                h_offset_div = int(h_offset_ratio * total_measure_div)
                _add_harmony(measure, h["chord"], h_offset_div)

            note = ET.SubElement(measure, "note")
            ET.SubElement(note, "rest", measure="yes")
            ET.SubElement(note, "duration").text = str(total_measure_div)
            ET.SubElement(note, "voice").text = "1"

    xml_str = ET.tostring(root, encoding='unicode')
    return '<?xml version="1.0" encoding="UTF-8" standalone="no"?>\n' + \
           '<!DOCTYPE score-partwise PUBLIC "-//Recordare//DTD MusicXML 4.0 Partwise//EN" "http://www.musicxml.org/dtds/partwise.dtd">\n' + \
           xml_str

def _add_empty_measure(part, number, num, den, bpm, is_first):
    measure = ET.SubElement(part, "measure", number=str(number))
    if is_first:
        attr = ET.SubElement(measure, "attributes")
        ET.SubElement(attr, "divisions").text = "480"
        time = ET.SubElement(attr, "time")
        ET.SubElement(time, "beats").text = str(num)
        ET.SubElement(time, "beat-type").text = str(den)

    direction = ET.SubElement(measure, "direction", placement="above")
    dir_type = ET.SubElement(direction, "direction-type")
    metronome = ET.SubElement(dir_type, "metronome")
    ET.SubElement(metronome, "beat-unit").text = "quarter"
    ET.SubElement(metronome, "per-minute").text = str(round(bpm))

    note = ET.SubElement(measure, "note")
    ET.SubElement(note, "rest", measure="yes")
    ET.SubElement(note, "duration").text = str(num * 480)
    ET.SubElement(note, "voice").text = "1"

def _add_harmony(measure, chord_data, offset_div):
    harmony = ET.SubElement(measure, "harmony")
    if offset_div > 0:
        ET.SubElement(harmony, "offset").text = str(offset_div)

    root = ET.SubElement(harmony, "root")
    ET.SubElement(root, "root-step").text = chord_data["root"]
    alter = 0
    if chord_data["accidental"] == "#": alter = 1
    elif chord_data["accidental"] == "b": alter = -1
    if alter != 0:
        ET.SubElement(root, "root-alter").text = str(alter)

    quality = chord_data.get("quality", "M")
    extension = chord_data.get("extension", "")

    kind_val = "major"
    if quality == "m":
        if not extension: kind_val = "minor"
        elif extension == "7": kind_val = "minor-seventh"
        elif extension == "9": kind_val = "minor-ninth"
        elif extension == "11": kind_val = "minor-11th"
        elif extension == "13": kind_val = "minor-13th"
    elif quality == "dim":
        kind_val = "diminished-seventh" if extension == "7" else "diminished"
    elif quality == "aug":
        kind_val = "augmented"
    elif quality == "sus2":
        kind_val = "suspended-second"
    elif quality == "sus4":
        kind_val = "suspended-fourth"
    elif quality == "M":
        if extension == "7": kind_val = "dominant"
        elif extension == "9": kind_val = "dominant-ninth"
        elif extension == "11": kind_val = "dominant-11th"
        elif extension == "13": kind_val = "dominant-13th"

    kind = ET.SubElement(harmony, "kind")
    kind.text = kind_val
    kind.set("text", _format_chord_simple(chord_data))

    if chord_data.get("bass"):
        bass = ET.SubElement(harmony, "bass")
        ET.SubElement(bass, "bass-step").text = chord_data["bass"]
        balter = 0
        if chord_data.get("bass_accidental") == "#": balter = 1
        elif chord_data.get("bass_accidental") == "b": balter = -1
        if balter != 0:
            ET.SubElement(bass, "bass-alter").text = str(balter)

    for alt in chord_data.get("alterations", []):
        degree = ET.SubElement(harmony, "degree")
        val = "".join(filter(str.isdigit, alt))
        if val:
            ET.SubElement(degree, "degree-value").text = val
            ET.SubElement(degree, "degree-alter").text = "1" if "#" in alt or "+" in alt else "-1" if "b" in alt or "-" in alt else "0"
            ET.SubElement(degree, "degree-type").text = "alter"

    for add in chord_data.get("additions", []):
        degree = ET.SubElement(harmony, "degree")
        val = "".join(filter(str.isdigit, add))
        if val:
            ET.SubElement(degree, "degree-value").text = val
            ET.SubElement(degree, "degree-alter").text = "0"
            ET.SubElement(degree, "degree-type").text = "add"

def _format_chord_simple(c):
    s = c["root"] + c["accidental"]
    if c["quality"] != "M": s += c["quality"]
    s += c["extension"]
    for a in c.get("alterations", []): s += a
    for a in c.get("additions", []): s += a
    if c.get("bass"): s += "/" + c["bass"] + c.get("bass_accidental", "")
    return s
