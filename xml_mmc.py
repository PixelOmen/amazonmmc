from pathlib import Path

from libs import media

currentdir = Path(__file__).parent
test_mmc_output = currentdir / "testfiles" / "test_mmc_output.xml"
test_mec_output = currentdir / "testfiles" / "test_mec_output.xml"

ep_test_dir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M\resources")
ftr_test_dir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M_feature\resources")


def testfunc2():
    deliv = media.Delivery(ep_test_dir.parent)
    print(deliv.toplevelgroup.coredata.localizedinfo)

def testfunc3():
    deliv = media.Delivery(ep_test_dir.parent)
    deliv.output_mec()
    deliv.output_mmc()

testfunc3()