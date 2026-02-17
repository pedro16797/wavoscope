import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from session.project import Project
from session.export import generate_musicxml

def test_musicxml_export_advanced(tmp_path):
    # Create a dummy audio file
    audio_path = tmp_path / "test.wav"
    audio_path.write_bytes(b"dummy")

    project = Project(audio_path)

    # 1. 4/4 measure at 120 BPM
    # duration = (4 * 60) / 120 = 2.0s
    project.add_flag(0.0, kind="rhythm", subdivision=4)

    # 2. 7/8 measure (tempo doubling rule)
    # If we want raw_bpm = 240, duration = (7 * 60) / 240 = 1.75s
    # start_t = 2.0. next_t = 2.0 + 1.75 = 3.75s
    project.add_flag(2.0, kind="rhythm", subdivision=7)

    # End flag to define duration of the second measure
    project.add_flag(3.75, kind="rhythm", subdivision=4)

    # Add a harmony flag
    # C Major: C3 (bass), C4, E4, G4 -> MIDI 48, 60, 64, 67
    project.add_harmony_flag(0.5, {"root": "C", "accidental": "", "quality": "M", "extension": "", "alterations": [], "additions": [], "bass": "", "bass_accidental": ""})

    xml_content = project.generate_musicxml()

    # Parse XML to verify structure
    tree = ET.fromstring(xml_content)

    # Check parts
    parts = tree.findall("part")
    assert len(parts) == 2
    assert parts[0].get("id") == "P1" # Piano
    assert parts[1].get("id") == "P2" # Metronome

    # Measure 1: 4/4
    m1_piano = parts[0].find("measure[@number='1']")
    time1 = m1_piano.find("attributes/time")
    assert time1.find("beats").text == "4"
    assert time1.find("beat-type").text == "4"

    # Measure 2: 7/8 (doubled tempo)
    m2_piano = parts[0].find("measure[@number='2']")
    time2 = m2_piano.find("attributes/time")
    assert time2.find("beats").text == "7"
    assert time2.find("beat-type").text == "8"

    # Check tempo in Measure 2
    # raw_bpm was 240. Adj bpm should be 120.
    metronome = m2_piano.find("direction/direction-type/metronome")
    assert metronome.find("per-minute").text == "120"

    # Check Metronome part notes in Measure 1 (should have 4 notes)
    m1_metro = parts[1].find("measure[@number='1']")
    notes_metro = m1_metro.findall("note")
    assert len(notes_metro) == 4

    # Check Piano part chords in Measure 1
    # Should have a rest then a chord
    notes_piano = m1_piano.findall("note")
    # First is rest (offset 0 to 0.5)
    assert notes_piano[0].find("rest") is not None
    # Then chord (C3, C4, E4, G4)
    assert notes_piano[1].find("pitch/step").text == "C"
    assert notes_piano[1].find("pitch/octave").text == "3"

    assert notes_piano[2].find("chord") is not None
    assert notes_piano[2].find("pitch/step").text == "C"
    assert notes_piano[2].find("pitch/octave").text == "4"

    assert notes_piano[3].find("chord") is not None
    assert notes_piano[3].find("pitch/step").text == "E"
    assert notes_piano[3].find("pitch/octave").text == "4"

    assert notes_piano[4].find("chord") is not None
    assert notes_piano[4].find("pitch/step").text == "G"
    assert notes_piano[4].find("pitch/octave").text == "4"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
