import os

def main():
    root = os.getcwd()
    for dirpath, dirnames, filenames in os.walk(root, topdown=True):
        # skip hidden dirs & dive into sub-folders
        dirnames[:] = [d for d in dirnames if not d.startswith(('_', '.', 'dist', 'venv'))]
        for fname in filenames:
            if fname.startswith(('_', '.')) | fname.endswith((".exe", ".spec")):
                continue
            rel_path = os.path.relpath(os.path.join(dirpath, fname), root)
            try:
                with open(os.path.join(dirpath, fname), 'r', encoding='utf-8') as f:
                    content = f.read()
                    if content == '':
                        content = '<empty file>'
            except (UnicodeDecodeError, OSError):
                content = '<binary / unreadable>'
            print(f"{rel_path}:\n{content}\n")

if __name__ == "__main__":
    main()