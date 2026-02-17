import os
import json
import xml.etree.ElementTree as ET
from pathlib import Path
from session.project import Project
from session.export import generate_musicxml

def test_musicxml_export_feedback(tmp_path):
    # Create a dummy audio file
    audio_path = tmp_path / "test.wav"
    audio_path.write_bytes(b"dummy")

    project = Project(audio_path)

    # 1. 4/4 measure at 120 BPM
    # duration = (4 * 60) / 120 = 2.0s
    project.add_flag(0.0, kind="rhythm", subdivision=4)

    # 2. Another 4/4 measure with slight tempo change (e.g. 122 BPM)
    # duration = (4 * 60) / 122 = 1.967s
    # start_t = 2.0. next_t = 3.967s
    project.add_flag(2.0, kind="rhythm", subdivision=4)

    # 3. Another 4/4 measure with significant tempo change (e.g. 130 BPM)
    # duration = (4 * 60) / 130 = 1.846s
    # start_t = 3.967. next_t = 5.813s
    project.add_flag(3.967, kind="rhythm", subdivision=4)

    # End flag
    project.add_flag(5.813, kind="rhythm", subdivision=4)

    # Add harmony flags
    project.add_harmony_flag(0.5, {"root": "C", "accidental": "", "quality": "M", "extension": "", "alterations": [], "additions": [], "bass": "", "bass_accidental": ""})

    xml_content = project.generate_musicxml()
    tree = ET.fromstring(xml_content)
    parts = tree.findall("part")

    # Check Measure 1 (Piano)
    m1_piano = parts[0].find("measure[@number='1']")
    # Should have a harmony tag
    assert m1_piano.find("harmony") is not None
    assert m1_piano.find("harmony/root/root-step").text == "C"
    # Should have a whole rest note
    note = m1_piano.find("note")
    assert note.find("rest") is not None
    # No more notes (explicit chord notes removed)
    assert len(m1_piano.findall("note")) == 1

    # Check Tempo markers (5 BPM threshold)
    # Measure 1: 120 BPM (Initial tempo, always noted)
    assert m1_piano.find("direction/direction-type/metronome/per-minute").text == "120"

    # Measure 2: 122 BPM. Diff = 2. Should NOT have a tempo marker.
    m2_piano = parts[0].find("measure[@number='2']")
    assert m2_piano.find("direction/direction-type/metronome") is None

    # Measure 3: 130 BPM. Diff vs 120 = 10. Should HAVE a tempo marker.
    m3_piano = parts[0].find("measure[@number='3']")
    assert m3_piano.find("direction/direction-type/metronome/per-minute").text == "130"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
