import uvicorn
import os
import sys
from pathlib import Path
import types

# Robust way to ensure 'wavoscope' is importable regardless of structure
root = Path(__file__).resolve().parent
if str(root) not in sys.path:
    sys.path.insert(0, str(root))

if "wavoscope" not in sys.modules:
    wavoscope = types.ModuleType("wavoscope")
    wavoscope.__path__ = [str(root)]
    sys.modules["wavoscope"] = wavoscope

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
