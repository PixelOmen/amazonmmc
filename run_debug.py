from pathlib import Path

import src
from src.libs.delivery import Delivery

HERE = Path(__file__).parent
TESTDIR = HERE / "testfiles" / "testdir"

src.main()
# deliv = Delivery(TESTDIR)
# for mec in deliv.mecs.all:
#     print(mec.outputname)