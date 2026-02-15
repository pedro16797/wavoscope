import time
from audio.synth import SimpleSynth

def test_synth():
    try:
        synth = SimpleSynth(44100)
        print("Synth started. Playing tone for 2 seconds...")
        synth.start_tone(440.0) # A4
        time.sleep(2)
        synth.stop_tone(440.0)
        print("Done.")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    test_synth()
