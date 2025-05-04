# compute_migration_hashes.py
import os, hashlib

migrations_dir = os.path.join(os.getcwd(), '..', 'migrations')
hashes = []
for fname in sorted(os.listdir(migrations_dir)):
    if fname.endswith('.py'):
        path = os.path.join(migrations_dir, fname)
        with open(path, 'rb') as f:
            data = f.read()
        md5 = hashlib.md5(data).hexdigest()
        hashes.append(f"{md5}  {fname}")
print("\n".join(hashes))
