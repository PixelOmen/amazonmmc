from xml.etree import ElementTree as ET

NS_RESIGESTER = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "md": "http://www.movielabs.com/schema/md/v2.9/md",
    "mdmec": "http://www.movielabs.com/schema/mdmec/v2.9",
}

NS = {key:"{"+value+"}" for key,value in NS_RESIGESTER.items()}

class MEC:
    def __init__(self, data: dict) -> None:
        self.data = data
        self.root = self.newroot()

    def newroot(self) -> ET.Element:
        for ns in NS_RESIGESTER:
            ET.register_namespace(ns, NS_RESIGESTER[ns])
        root = ET.Element(NS["mdmec"]+"CoreMetadata")
        root.set(NS["xsi"]+"schemaLocation", "http://www.movielabs.com/schema/mdmec/v2.9 mdmec-v2.9.xsd")
        return root