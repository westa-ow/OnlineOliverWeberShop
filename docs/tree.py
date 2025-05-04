# tree_limited.py
import os, sys

MAX_LEVEL = 2

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")
def walk(dir_path, prefix='', level=0):
    if level > MAX_LEVEL:
        return
    entries = sorted(e for e in os.listdir(dir_path)
                     if not (
                         e in ('venv','env','__pycache__','.git')
                         or e.startswith('.')
                         or e == 'node_modules'
                         or e == 'media'
                     ))
    for i, entry in enumerate(entries):
        path = os.path.join(dir_path, entry)
        is_last = (i == len(entries)-1)
        connector = '└── ' if is_last else '├── '
        print(prefix + connector + entry)
        if os.path.isdir(path):
            extension = '    ' if is_last else '│   '
            walk(path, prefix + extension, level+1)

if __name__ == '__main__':
    walk(os.getcwd())
