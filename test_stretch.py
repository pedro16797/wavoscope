import python_stretch
import numpy as np

try:
    tsm = python_stretch.Stretch(channels=1, samplerate=44100)
    print("Stretch initialized")
    print("Methods:", dir(tsm))

    # Test process
    input_data = np.zeros((1, 1024), dtype=np.float32)
    # output_data = np.zeros((1, 1024), dtype=np.float32)
    # tsm.process(input_data, output_data)
    # print("Process called")

except Exception as e:
    print("Error:", e)
