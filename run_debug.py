from pathlib import Path

import amazonmmc
from amazonmmc.libs.delivery import Delivery

HERE = Path(__file__).parent
TESTDIR = HERE / "testfiles" / "testdir"

amazonmmc.main()
# deliv = Delivery(TESTDIR)
# for mec in deliv.mecs.all:
#     print(mec.outputname)