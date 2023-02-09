from pathlib import Path

from src.libs.delivery import Delivery

TESTDIR = Path(__file__).parent / "testfiles" / "testdir"

test = Delivery(TESTDIR)
test.checksums()