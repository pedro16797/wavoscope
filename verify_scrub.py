import os
from pathlib import Path
from session.project import Project
import json

def verify_scrubbing():
    audio_path = Path("test_verify.wav")
    audio_path.write_bytes(b"dummy")

    project = Project(audio_path)

    # Add a rhythm flag with non-defaults to see renames
    project.add_flag(1.0, subdivision=8, name="Verse")

    # Add a harmony flag with non-defaults to see renames
    project.add_harmony_flag(2.0, {"root": "D", "accidental": "#", "quality": "m", "extension": "7", "alterations": ["b5"], "additions": ["add9"], "bass": "A", "bass_accidental": ""})

    # Save it
    project.save()

    sidecar_path = Path("test_verify.wav.oscope")
    content = sidecar_path.read_text()
    data = json.loads(content)

    print("Scrubbed JSON content:")
    print(json.dumps(data, indent=2))

    # Check that defaults are scrubbed and keys are renamed
    flag = data["flags"][0]
    assert "auto_name" not in flag
    assert "subdivision" not in flag
    assert "div" in flag
    assert flag["div"] == 8
    assert "n" in flag
    assert flag["n"] == "Verse"

    hflag = data["harmony_flags"][0]
    assert "chord" not in hflag
    assert "c" in hflag
    chord = hflag["c"]
    assert "r" in chord
    assert chord["r"] == "D"
    assert "ca" in chord
    assert chord["ca"] == "#"
    assert "q" in chord
    assert chord["q"] == "m"
    assert "ext" in chord
    assert chord["ext"] == "7"
    assert "alt" in chord
    assert chord["alt"] == ["b5"]
    assert "add" in chord
    assert chord["add"] == ["add9"]
    assert "b" in chord
    assert chord["b"] == "A"
    assert "ba" not in chord # bass_accidental is "" so it should be scrubbed

    # Reload and check filling and auto_name recomputation
    new_project = Project(audio_path)

    filled_flag = new_project.session_data["flags"][0]
    print("\nFilled flag data:")
    print(filled_flag)
    assert filled_flag["subdivision"] == 8
    assert filled_flag["name"] == "Verse"
    assert filled_flag["auto_name"] == "1" # Should be recomputed

    filled_chord = new_project.session_data["harmony_flags"][0]["chord"]
    print("\nFilled chord data:")
    print(filled_chord)
    assert filled_chord["root"] == "D"
    assert filled_chord["quality"] == "m"
    assert filled_chord["bass_accidental"] == "" # Restored from default

    print("\nVerification successful!")

    # Cleanup
    if audio_path.exists(): audio_path.unlink()
    if sidecar_path.exists(): sidecar_path.unlink()

if __name__ == "__main__":
    verify_scrubbing()
