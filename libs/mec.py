from xml.etree import ElementTree as ET

from . import dataio

XMLNSPACES = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "md": "http://www.movielabs.com/schema/md/v2.6/md",
    "mdmec": "http://www.movielabs.com/schema/mdmec/v2.9",
}

NS = {key:"{"+value+"}" for key,value in XMLNSPACES.items()}

def newroot() -> ET.Element:
    for ns in XMLNSPACES:
        ET.register_namespace(ns, XMLNSPACES[ns])
    root = ET.Element(NS["mdmec"]+"CoreMetadata")
    root.set(NS["xsi"]+"schemaLocation", "http://www.movielabs.com/schema/mdmec/v2.8 mdmec-v2.8.xsd")
    return root

def create(data: dataio.MECData) -> ET.Element:
    root = newroot()
    basic_elem = ET.SubElement(root, NS["mdmec"]+"Basic")
    basic_elem.set("ContentID", f"md:cid:org:{data.id}")
    for region in data.localizedinfo:
        pass

    return root