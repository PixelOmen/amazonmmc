from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

from . import inventory, presentations, experiences

if TYPE_CHECKING:
    from .media import ResourceGroup

XMLNSPACES = {
    "manifest": "http://www.movielabs.com/schema/manifest/v1.7/manifest",
    "md": "http://www.movielabs.com/schema/md/v2.6/md",
    "xs": "http://www.w3.org/2001/XMLSchema",
    "xsi": "http://www.w3.org/2001/XMLSchema-instance"
}

CURLYNS = {key:"{"+value+"}" for key,value in XMLNSPACES.items()}

# xmlns definitions are only added to the top once they are used
def newroot() -> ET.Element:
    for ns in XMLNSPACES:
        ET.register_namespace(ns, XMLNSPACES[ns])
    root = ET.Element(CURLYNS["manifest"]+"MediaManifest")
    compatibility = ET.SubElement(root, CURLYNS["manifest"]+"Compatibility")
    ET.SubElement(compatibility, CURLYNS["manifest"]+"SpecVersion").text = "1.5"
    ET.SubElement(compatibility, CURLYNS["manifest"]+"Profile").text = "MMC-1"
    return root

def create(topgroup: "ResourceGroup") -> ET.Element:
    root_elem = newroot()
    inventory.create(root_elem, CURLYNS, topgroup)
    presentations.create(root_elem, CURLYNS, topgroup)
    experiences.create(root_elem, CURLYNS, topgroup)
    return root_elem