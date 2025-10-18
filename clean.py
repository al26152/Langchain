import os

docs_path = "docs"
files = os.listdir(docs_path)

renamed = []

for filename in files:
    if "»" in filename:
        new_name = filename.replace("»", "_")
        os.rename(os.path.join(docs_path, filename), os.path.join(docs_path, new_name))
        renamed.append((filename, new_name))

if renamed:
    print("\n--- Renamed Files ---")
    for old, new in renamed:
        print(f"{old} → {new}")
else:
    print("\n--- No files needed renaming ---")