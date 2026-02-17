import os
import json
from pathlib import Path
from session.project import Project
from session.export import generate_musicxml

def test_musicxml_export(tmp_path):
    # Create a dummy audio file
    audio_path = tmp_path / "test.wav"
    audio_path.write_bytes(b"dummy")

    project = Project(audio_path)

    # Add some flags
    project.add_flag(0.0, kind="rhythm", name="Intro", section_start=True)
    project.add_flag(2.0, kind="rhythm")
    project.add_flag(4.0, kind="rhythm")

    project.add_harmony_flag(0.5, {"root": "C", "accidental": "", "quality": "M", "extension": "7", "alterations": [], "additions": [], "bass": "", "bass_accidental": ""})
    project.add_harmony_flag(2.5, {"root": "F", "accidental": "", "quality": "M", "extension": "", "alterations": [], "additions": [], "bass": "", "bass_accidental": ""})

    # Update time signature
    project.update_time_signature(3, 4)

    xml_content = project.generate_musicxml()

    assert '<?xml version="1.0" encoding="UTF-8" standalone="no"?>' in xml_content
    assert '<work-title>test</work-title>' in xml_content
    assert '<beats>3</beats>' in xml_content
    assert '<beat-type>4</beat-type>' in xml_content
    assert '<rehearsal>Intro</rehearsal>' in xml_content
    assert '<root-step>C</root-step>' in xml_content
    assert '<kind text="C7">dominant</kind>' in xml_content
    assert '<root-step>F</root-step>' in xml_content
    assert '<kind text="F">major</kind>' in xml_content

    # Check tempo calculation
    # Measure 1: 0.0 to 2.0. Duration = 2.0. Numerator = 3.
    # BPM = (3 * 60) / 2.0 = 90.
    assert '<per-minute>90</per-minute>' in xml_content

    # Measure 2: 2.0 to 4.0. Duration = 2.0. BPM = 90.
    # No new tempo marker expected since it's the same.
    assert xml_content.count('<per-minute>') == 1

    # Add a flag that changes tempo
    project.add_flag(5.0, kind="rhythm") # Measure 3: 4.0 to 5.0. Duration = 1.0. BPM = (3*60)/1.0 = 180.
    xml_content_2 = project.generate_musicxml()
    assert '<per-minute>180</per-minute>' in xml_content_2
    assert xml_content_2.count('<per-minute>') == 2

if __name__ == "__main__":
    import pytest
    pytest.main([__file__])
