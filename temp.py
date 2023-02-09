import uuid
from pathlib import Path

TESTDIR = Path(__file__).parent / "testfiles" / "testdir"
RESOURCES = TESTDIR / "resources"

files: list[Path] = []
for file in RESOURCES.iterdir():
    if not file.is_file():
        continue
    files.append(file)

md5dict: dict[str, str] = {}
for file in files:
    md5dict[str(uuid.uuid4())] = file.name


md5path = TESTDIR / "data" / "checksums.md5"
with open(md5path, "w") as fp:
    for k,v in md5dict.items():
        fp.write(f"{k} {v}\n")
