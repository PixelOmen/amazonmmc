from typing import TYPE_CHECKING

from ..xmlhelpers import newelement, str_to_element

if TYPE_CHECKING:
    from xml.etree import ElementTree as ET

    from .inventory import Metadata
    from .experiences import Experience

class ALID:
    def __init__(self, experience: "Experience", metadata: "Metadata") -> None:
        self.experience = experience
        self.metadata = metadata
        self.id = self._id()
        self.rootelem = newelement("manifest", "ALIDExperienceMap")
        
    def _id(self) -> str:
        # md:alid:org:amazonkids:HELLO_KITTY_INTL_S1_105
        mecid = self.metadata.mec.id
        org = self.metadata.mec.org
        return f"md:alid:org:{org}:{mecid}"

    def generate(self) -> "ET.Element":
        self.rootelem.append(str_to_element("manifest", "ALID", self.id))
        exp_root = str_to_element("manifest", "ExperienceID", self.experience.id)
        exp_root.set("condition", "For-sale")
        self.rootelem.append(exp_root)
        return self.rootelem
