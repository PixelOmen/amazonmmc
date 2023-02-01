from typing import cast
from xml.etree import ElementTree as ET

from ..mec import MECGroup, MECEpisodic
from ..enums import WorkTypes, MediaTypes
from ..xmlhelpers import newroot, newelement, key_to_element, str_to_element

class MMC:
    def __init__(self, mecs: MECGroup) -> None:
        self.mecs = mecs

    def episodic(self) -> ET.Element:
        pass