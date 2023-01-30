from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from .media import Media

NS_RESIGESTER = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "md": "http://www.movielabs.com/schema/md/v2.9/md",
    "mdmec": "http://www.movielabs.com/schema/mdmec/v2.9",
}

NS = {key:"{"+value+"}" for key,value in NS_RESIGESTER.items()}


class MEC:
    def __init__(self, media: "Media") -> None:
        self.media = media
        self.root = self._newroot()

    def episodic(self) -> ET.Element:
        basic_elem = self._basic()
        self.root.append(basic_elem)
        return self.root

    def _newroot(self) -> ET.Element:
        for ns in NS_RESIGESTER:
            ET.register_namespace(ns, NS_RESIGESTER[ns])
        root = ET.Element(NS["mdmec"]+"CoreMetadata")
        root.set(NS["xsi"]+"schemaLocation", "http://www.movielabs.com/schema/mdmec/v2.9 mdmec-v2.9.xsd")
        return root

    def _basic(self) -> ET.Element:
        basicroot = ET.Element(NS["mdmec"]+"Basic")
        localizedinfo = self._localized()
        basicroot.append(localizedinfo)
        return basicroot

    def _localized(self) -> ET.Element:
        locroot = ET.Element(NS["md"]+"LocalizedInfo")
        return locroot