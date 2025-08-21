# Wavoscope – musician-oriented audio transcription workbench

### Run the app
python -m wavoscope 

### Get requirements
pip install -r requirements.txt

### Dump the project for AI system prompts
python dump_project.py

### Build
python -m nuitka --standalone --enable-plugin=pyside6 --include-package-data=wavoscope --include-qt-plugins=sensible,styles,imageformats --include-data-dir=resources=resources --noinclude-data-files="**/.git/**" --noinclude-data-files="**/.venv/**" --noinclude-data-files="**/__pycache__/**" --noinclude-data-files="**/requirements.txt" --noinclude-data-files="**/Wavoscope.spec" --noinclude-data-files="**/.dump_project.py" --noinclude-data-files="**/README.md" --nofollow-import-to=pytest --windows-icon-from-ico=resources/icons/app-icon.png --output-dir=dist-nuitka --assume-yes-for-downloads --jobs=0 main.py