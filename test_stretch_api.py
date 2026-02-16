import python_stretch.Signalsmith as ps
import numpy as np

tsm = ps.Stretch()
tsm.preset(1, 44100.0)
tsm.setTimeFactor(2.0) # 0.5x speed

input_chunk = np.random.uniform(-1, 1, (1, 1024)).astype(np.float32)
output = tsm.process(input_chunk)
print(f"Input: {input_chunk.shape}, Output: {output.shape}")

output2 = tsm.process(input_chunk)
print(f"Input: {input_chunk.shape}, Output: {output2.shape}")

tsm.setTimeFactor(0.5) # 2.0x speed
output3 = tsm.process(input_chunk)
print(f"Input: {input_chunk.shape}, Output: {output3.shape}")
