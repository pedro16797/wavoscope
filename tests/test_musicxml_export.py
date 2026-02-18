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

def test_musicxml_export_annotations(tmp_path):
    # Create a dummy audio file
    audio_path = tmp_path / "test2.wav"
    audio_path.write_bytes(b"dummy")
    project = Project(audio_path)

    # 1. Section start with name
    # auto_name will be "A"
    project.add_flag(0.0, kind="rhythm", name="Verse", section_start=True)

    # 2. Non-section flag with name
    project.add_flag(2.0, kind="rhythm", name="Drum Fill", section_start=False)

    # 3. Section start without name
    # auto_name will be "B"
    project.add_flag(4.0, kind="rhythm", name="", section_start=True)

    # End flag
    project.add_flag(6.0, kind="rhythm")

    xml_content = project.generate_musicxml()
    tree = ET.fromstring(xml_content)
    piano_part = tree.find("part[@id='P1']")

    # Measure 1: should have <rehearsal>A</rehearsal> and <words>Verse</words>
    m1 = piano_part.find("measure[@number='1']")
    assert m1.find("direction/direction-type/rehearsal").text == "A"
    words1 = [w.text for w in m1.findall("direction/direction-type/words")]
    assert "Verse" in words1

    # Measure 2: should have <words>Drum Fill</words> but NO <rehearsal>
    m2 = piano_part.find("measure[@number='2']")
    assert m2.find("direction/direction-type/rehearsal") is None
    words2 = [w.text for w in m2.findall("direction/direction-type/words")]
    assert "Drum Fill" in words2

    # Measure 3: should have <rehearsal>B</rehearsal> but NO <words>
    m3 = piano_part.find("measure[@number='3']")
    assert m3.find("direction/direction-type/rehearsal").text == "B"
    words3 = [w.text for w in m3.findall("direction/direction-type/words")]
    # Empty string or non-existent is fine.
    assert "Drum Fill" not in words3
    assert "" not in words3 or len(words3) == 1

def test_musicxml_export_metadata(tmp_path):
    from utils.config import Config
    cfg = Config()
    cfg.set("ui.musicxml_author", "Test Author")

    audio_path = tmp_path / "test_metadata.wav"
    audio_path.write_bytes(b"dummy")
    project = Project(audio_path)
    project.add_flag(0.0, kind="rhythm")
    project.add_flag(2.0, kind="rhythm")

    xml_content = project.generate_musicxml()
    tree = ET.fromstring(xml_content)
    creator = tree.find("identification/creator")
    assert creator is not None
    assert creator.text == "Test Author"
    assert creator.attrib["type"] == "composer"

    software = tree.find("identification/encoding/software")
    assert software.text == "Wavoscope by Lendas do Alén"

def test_musicxml_export_inheritance_and_gap(tmp_path):
    audio_path = tmp_path / "test_inheritance.wav"
    audio_path.write_bytes(b"dummy")
    project = Project(audio_path)

    # 7 second gap, then four 7/8 measures (2s each)
    # F1 (start M2) at 7.0s, subdiv=7
    project.add_flag(7.0, kind="rhythm", subdivision=7)
    # F2 (start M3) at 9.0s, subdiv=0 (should inherit 7)
    project.add_flag(9.0, kind="rhythm", subdivision=0)
    # F3 (start M4) at 11.0s, subdiv=0 (should inherit 7)
    project.add_flag(11.0, kind="rhythm", subdivision=0)
    # F4 (start M5) at 13.0s, subdiv=0 (should inherit 7)
    project.add_flag(13.0, kind="rhythm", subdivision=0)
    # F5 (start M6) at 15.0s, subdiv=4 (shift back to 4/4)
    project.add_flag(15.0, kind="rhythm", subdivision=4)
    # End flag
    project.add_flag(17.0, kind="rhythm")

    xml_content = project.generate_musicxml()
    tree = ET.fromstring(xml_content)
    piano_part = tree.find("part[@id='P1']")
    measures = piano_part.findall("measure")

    # M1: Gap (0-7s). Should have subdiv=7 (inherited from first real flag)
    # num=7, den=4 (initial measures use den=4). BPM = 7*60/7 = 60.
    m1 = measures[0]
    assert m1.find("attributes/time/beats").text == "7"
    assert m1.find("attributes/time/beat-type").text == "4"

    # M2: (7-9s). subdiv=7. raw_bpm = 7*60/2 = 210.
    # 210 > 1.7 * 60. So den=8, bpm=105.
    m2 = measures[1]
    assert m2.find("attributes/time/beats").text == "7"
    assert m2.find("attributes/time/beat-type").text == "8"
    assert m2.find("direction/direction-type/metronome/per-minute").text == "105"

    # M3: (9-11s). subdiv=0 -> inherits 7. raw_bpm = 210.
    # 210 > 1.7 * 105. So den=8, bpm=105.
    m3 = measures[2]
    # In MusicXML, attributes are only present when they change.
    # M3 should not have attributes if it's the same as M2.
    assert m3.find("attributes") is None

    # M4, M5 should also NOT have attributes (they stay 7/8)
    assert measures[3].find("attributes") is None
    assert measures[4].find("attributes") is None

    # M6: (15-17s). subdiv=4. raw_bpm = 4*60/2 = 120.
    # 120 < 1.7 * 105 (178.5). So den=4, bpm=120.
    m6 = measures[5]
    assert m6.find("attributes/time/beats").text == "4"
    assert m6.find("attributes/time/beat-type").text == "4"

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
