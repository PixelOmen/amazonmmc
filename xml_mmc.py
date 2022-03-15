import time
from pathlib import Path
from xml.etree import ElementTree as ET

from libs import media, dataio

currentdir = Path(__file__).parent
test_mmc_output = currentdir / "testfiles" / "test_mmc_output.xml"
test_mec_output = currentdir / "testfiles" / "test_mec_output.xml"

ep_test_dir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M\resources")
ftr_test_dir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M_feature\resources")


def testfunc2():
    deliv = media.Delivery(ep_test_dir.parent)
    print(deliv.coregroup.coredata.localizedinfo)

def testfunc3():
    deliv = media.Delivery(ep_test_dir.parent)
    deliv.coregroup.output_mec()

testfunc3()

# def testfunc():
#     root = create_root()
#     deliv = media.Delivery(ep_test_dir.parent)
#     inventory.create(root, CURLYNS, deliv)
#     presentations.create(root, CURLYNS, deliv)
#     experiences.create(root, CURLYNS, deliv)
#     output_xml(root, test_mmc_output)

# -- Creating XML
# ET.register_namespace("testinfo", "http://www.movielabs.com/schema/manifest/v1.10/manifest")
# ET.register_namespace("anotherns", "This is the third ns")
# root = ET.Element("{http://www.movielabs.com/schema/manifest/v1.10/manifest}MediaManifest")
# subtag = ET.SubElement(root, "TagWithDefaultNS")
# subsubtag = ET.SubElement(subtag, "{This is the third ns}thirdsubtag")
# subsubtag.text = "More Text"
# indent(root)
# tree = ET.ElementTree(root)
# tree.write(testoutput, encoding='UTF-8', xml_declaration=True)