import xml.etree.ElementTree as ET
from session.project import Project
from session.export import generate_musicxml

def test_musicxml_export_padding(tmp_path):
    # Create a dummy audio file
    audio_path = tmp_path / "test_padding.wav"
    audio_path.write_bytes(b"dummy")

    project = Project(audio_path)

    # Audio duration is 10 seconds
    # First flag at 4.0s
    project.add_flag(4.0, type="rhythm", div=4)
    # Second flag at 6.0s
    project.add_flag(6.0, type="rhythm", div=4)

    # We mock the duration for the export call
    xml_content = generate_musicxml(project.session_data, "test_padding.mp3", audio_duration=10.0)
    tree = ET.fromstring(xml_content)
    piano_part = tree.find("part[@id='P1']")
    measures = piano_part.findall("measure")

    # Current expected logic:
    # Virtual start at 0.0 added. rhythm_flags: [0.0, 4.0, 6.0]
    # Padding loop:
    # rhythm_flags[-1] is 6.0. interval = 6.0 - 4.0 = 2.0.
    # curr_t = 8.0. Append 8.0. rhythm_flags: [0.0, 4.0, 6.0, 8.0]
    # curr_t = 10.0. Append 10.0. rhythm_flags: [0.0, 4.0, 6.0, 8.0, 10.0]
    # curr_t = 12.0. Loop terminates (12.0 > 10.0 + 1.0)
    # Total rhythm_flags: [0.0, 4.0, 6.0, 8.0, 10.0] -> 5 flags -> 4 measures.

    assert len(measures) == 4
