from pathlib import Path

from src.libs.checksums import MD5

TESTDIR = Path(__file__).parent / "testfiles" / "testdir"

test = MD5(TESTDIR)
result = test.run()
print(result)