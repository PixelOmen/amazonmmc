from pathlib import Path

from libs.delivery import Delivery

HERE = Path(__file__).parent
TESTDIR = HERE / "testfiles" / "testdir"

deliv = Delivery(TESTDIR)
for mec in deliv.mmc.mecs.all:
    print(mec.media.id)
    for res in mec.media.resources:
        print(res)
    print()