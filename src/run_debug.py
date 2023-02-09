from pathlib import Path

from libs.delivery import Delivery

HERE = Path(__file__).parent
TESTDIR = HERE.parent / "testfiles" / "testdir"

deliv = Delivery(TESTDIR)
deliv.write_mmc()