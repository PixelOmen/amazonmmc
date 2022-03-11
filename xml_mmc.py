import time
from pathlib import Path
from xml.etree import ElementTree as ET

from libs import idgen, media

currentdir = Path(__file__).parent
testxmldir = currentdir / "samples"
testoutput = currentdir / "testoutput.xml"

testresourcedir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M\resources")

xmlnspaces = {
    "manifest": "http://www.movielabs.com/schema/manifest/v1.7/manifest",
    "md": "http://www.movielabs.com/schema/md/v2.6/md",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}

curlyns = {}
for ns in xmlnspaces:
    curlyns[ns] = "{" + xmlnspaces[ns] + "}"

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

def get_eidr(xmlpath: Path=...) -> str:
    if xmlpath is ...:
        xmlpath = currentdir 
    for f in xmlpath.iterdir():
        if f.suffix.lower() == ".xml":
            return f.stem
    raise FileNotFoundError("Unable to locate MMC")

# xmlns definitions are only added to the top once they are used
def create_root() -> ET.Element:
    for ns in xmlnspaces:
        ET.register_namespace(ns, xmlnspaces[ns])
    root = ET.Element(curlyns["manifest"]+"MediaManifest")
    compatibility = ET.SubElement(root, curlyns["manifest"]+"Compatibility")
    ET.SubElement(compatibility, curlyns["manifest"]+"SpecVersion").text = "1.5"
    ET.SubElement(compatibility, curlyns["manifest"]+"Profile").text = "MMC-1"
    return root


def testfunc():
    eidr = get_eidr(testxmldir)
    root = create_root()
    output_xml(root, testoutput)
    print(eidr)

def testfunc2():
    eidr = get_eidr(testxmldir)
    resources = list(testresourcedir.iterdir())
    for f in resources:
        if f.name[0] == ".":
            continue
        r = media.Resource(f,eidr)
        print(r.id)

testfunc2()



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