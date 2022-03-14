import time
from pathlib import Path
from xml.etree import ElementTree as ET

from libs import media, inventory, presentations, experiences

# Naming convention:
# Vendor_Title_Descriptor_Audio_Resolution_AspectCanvas_Framerate_Note
# Descriptor = FTR, S01E101, S01, SERIES
# Audio = EN-US-51-20
# Resolution = 1920x1080
# AspectCanvas = 16x9, 4x3
# Framerate = 25i, 2398p

currentdir = Path(__file__).parent
testxmldir = currentdir / "samples"
testoutput = currentdir / "testoutput.xml"

ep_test_dir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M\resources")
ftr_test_dir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M_feature\resources")

XMLNSPACES = {
    "manifest": "http://www.movielabs.com/schema/manifest/v1.7/manifest",
    "md": "http://www.movielabs.com/schema/md/v2.6/md",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}

CURLYNS = {key:"{"+value+"}" for key,value in XMLNSPACES.items()}

# indent function adds newlines and tabs to xml so it's not all on 1 line
# pass root element into function
def indent(elem: ET.Element, level: int=0, spaces: int=4):
    i = "\n" + level*(" "*spaces)
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + (" "*spaces)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def output_xml(root, outputpath, encodingtype="UTF-8", xmldecl=True):
    indent(root)
    tree = ET.ElementTree(root)
    tree.write(outputpath, encoding=encodingtype, xml_declaration=xmldecl)

# xmlns definitions are only added to the top once they are used
def create_root() -> ET.Element:
    for ns in XMLNSPACES:
        ET.register_namespace(ns, XMLNSPACES[ns])
    root = ET.Element(CURLYNS["manifest"]+"MediaManifest")
    compatibility = ET.SubElement(root, CURLYNS["manifest"]+"Compatibility")
    ET.SubElement(compatibility, CURLYNS["manifest"]+"SpecVersion").text = "1.5"
    ET.SubElement(compatibility, CURLYNS["manifest"]+"Profile").text = "MMC-1"
    return root


def testfunc():
    root = create_root()
    deliv = media.Delivery(ep_test_dir.parent)
    inventory.create(root, CURLYNS, deliv)
    presentations.create(root, CURLYNS, deliv)
    experiences.create(root, CURLYNS, deliv)
    output_xml(root, testoutput)

testfunc()



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