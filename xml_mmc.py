import time
from xml.etree import ElementTree as ET
from pathlib import Path

from libs import idgen

currentdir = Path(__file__).parent

testcsv = currentdir / "testinput.csv"
testxml = currentdir / "test_mmc.xml"
testoutput = currentdir / "testoutput.xml"

mmc_spec_ver = "1.7"
mmc_profile = "MMC-1"

delim = ";"
xmlnspaces = {
    "manifest": "http://www.movielabs.com/schema/manifest/v1.7/manifest",
    "md": "http://www.movielabs.com/schema/md/v2.6/md",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}

curlyns = {}
for ns in xmlnspaces:
    curlyns[ns] = "{" + xmlnspaces[ns] + "}"

def parse_csv(filepath):
    with open(filepath, "r", encoding="UTF-8") as fp:
        csvinfo = fp.readlines()

    csvinfo = [x.strip() for x in csvinfo]
    headers = csvinfo[0].split(delim)
    data = csvinfo[1:]
    dictinfo = {}

    for headeritem in enumerate(headers):
        headerindex = headeritem[0]
        header = headeritem[1]
        dictinfo[header] = []
        for row in data:
            splitrow = row.split(delim)
            dictinfo[header].append(splitrow[headerindex])
    
    return dictinfo

# indent function adds newlines and tabs to xml so it's not all on 1 line
# pass root element into function
def indent(elem, level=0):
    i = "\n" + level*"  "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "  "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


def create_root(csvdict, index=0):
    for ns in xmlnspaces:
        ET.register_namespace(ns, xmlnspaces[ns])
    root = ET.Element(curlyns["manifest"]+"MediaManifest")
    root.attrib[curlyns["xsi"]+"schemaLocation"] = "http://www.movielabs.com/schema/manifest/v1.7/manifest manifest-v1.7.xsd"
    root.attrib["ManifestID"] = idgen.idgenswitch["manifest"](csvdict)
    root.attrib["updateNum"] = str(int(time.time()))
    root.attrib["workflow"] = csvdict["workflow"][index]
    root.attrib["ExtraVersionReference"] = idgen.idgenswitch["extraversionref"](csvdict)
    root.attrib["versionDescription"] = csvdict["version_description"][index]
    compat = ET.SubElement(root, curlyns["manifest"]+"Compatibility")
    specver = ET.SubElement(compat, curlyns["manifest"]+"SpecVersion")
    specver.text = mmc_spec_ver
    profile = ET.SubElement(compat, curlyns["manifest"]+"Profile")
    profile.text = mmc_profile
    return root

def output_xml(root, outputpath, encodingtype="UTF-8", xmldecl=True):
    indent(root)
    tree = ET.ElementTree(root)
    tree.write(outputpath, encoding=encodingtype, xml_declaration=xmldecl)

csvdict = parse_csv(testcsv)
root = create_root(csvdict)
output_xml(root, testoutput)

# # -- Creating XML
# ET.register_namespace("", "This is the default ns")
# ET.register_namespace("rootns", "This is the root ns")
# ET.register_namespace("anotherns", "This is the third ns")
# root = ET.Element("{This is the root ns}Roottag")
# subtag = ET.SubElement(root, "TagWithDefaultNS")
# subsubtag = ET.SubElement(subtag, "{This is the third ns}thirdsubtag")
# subsubtag.text = "More Text"
# indent(root)
# tree = ET.ElementTree(root)
# tree.write(testoutput, encoding='UTF-8', xml_declaration=True)