import uuid
from pathlib import Path

import amazonmmc
from amazonmmc.libs.delivery import Delivery

HERE = Path(__file__).parent
TESTDIR = HERE / "testfiles" / "testdir"
RESOURCES = TESTDIR / "resources"

def fakemd5():
    md5dict: dict[str, str] = {}
    for file in RESOURCES.iterdir():
        if not file.is_file():
            continue
        md5dict[str(uuid.uuid4())] = file.name

    md5path = TESTDIR / "data" / "checksums.md5"
    with open(md5path, "w") as fp:
        for k,v in md5dict.items():
            fp.write(f"{k} {v}\n")

if __name__ == "__main__":
    amazonmmc.main()
