from pathlib import Path

from libs.delivery import Delivery

HERE = Path(__file__).parent
TESTDIR = HERE / "testfiles" / "testdir"

test = Delivery(TESTDIR)
test.write_mmc()