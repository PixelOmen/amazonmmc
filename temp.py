from libs.delivery import Delivery

TESTDIR = r"C:\Users\eacosta\Projects\python\amazonmmc\testfiles\testdir"

test = Delivery(TESTDIR)
test.build_mecs()
test.write_mecs()