from xml.etree import ElementTree as ET

from . import media

XMLNSPACES = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "md": "http://www.movielabs.com/schema/md/v2.6/md",
    "mdmec": "http://www.movielabs.com/schema/mdmec/v2.9",
}

NS = {key:"{"+value+"}" for key,value in XMLNSPACES.items()}

def root() -> ET.Element:
    for ns in XMLNSPACES:
        ET.register_namespace(ns, XMLNSPACES[ns])
    root = ET.Element(NS["mdmec"]+"CoreMetadata")
    root.set(NS["xsi"]+"schemaLocation", "http://www.movielabs.com/schema/mdmec/v2.8 mdmec-v2.8.xsd")
    return root

def create(delivery: media.Delivery) -> ET.Element:
    pass