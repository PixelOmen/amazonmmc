from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

from ..enums import MediaTypes
from ..xmlhelpers import newelement, key_to_element, str_to_element

if TYPE_CHECKING:
    from ..media import Resource
    from ..mec import MEC, MECEpisodic

# MOV naming - AMAZONKIDS_HELLOKITTY_SEASON1_101_EN-US_ja-JP_5120_25_1920x1080_16x9_HD_178.mov
# Dubbed -     AMAZONKIDS_HELLOKITTY_SEASON1_101_EN-US_ja-JP_5120_25_1920x1080_16x9_HD_178_dubbed.mov
"""
<manifest:Audio AudioTrackID="md:audtrackid:org:amazonkids:HELLO_KITTY_INTL_S1_101:episode.1.audio.en">
    <md:Type>primary</md:Type>
    <md:Encoding>
        <md:Codec>PCM</md:Codec>
    </md:Encoding>
    <md:Language dubbed="false">en-US</md:Language>
    <md:Region>ja-JP</md:Region>
    <manifest:ContainerReference>
        <manifest:ContainerLocation>file://resources/AMAZONKIDS_HELLOKITTY_SEASON1_101_EN-US_5120_25_1920x1080_16x9_HD_178.mov</manifest:ContainerLocation>
        <manifest:Hash method="MD5">ac4dcac3d366c1a5b009fa2a2120222c</manifest:Hash>
    </manifest:ContainerReference>
</manifest:Audio>
"""

class Audio:
    def __init__(self, mec: "MEC", resource: "Resource") -> None:
        self.rootelem = newelement("manifest", "Audio")
        self.mec = mec
        self.resource = resource
        self.type = "primary"
        self.codec = "PCM"
        self.hash = self._hash()
        self.id: str
        self.language: str
        self.dubbed: bool
        self.region: str
        self.location: str
        self._parse_resource()
        self._hash()

    def _parse_resource(self) -> None:
        mecid = self.mec.id
        org = self.mec.search_media("AssociatedOrg")
        orgid = org["organizationID"]
        split_name = self.resource.fullpath.name.split("_")
        if self.resource.mediatype == MediaTypes.EPISODE:
            self.language = split_name[4]
            self.dubbed = True if split_name[-1].lower() == "dubbed" else False
            self.region = split_name[5]
            self.location = f"file://resources/{self.resource.fullpath.name}"
            seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
            self.id = f"md:audtrackid:org:{orgid}:{mecid}:episode.{seq}.{self.language}"
        elif self.resource.mediatype == MediaTypes.SEASON:
            pass
        elif self.resource.mediatype == MediaTypes.SERIES:
            pass
        else:
            raise NotImplementedError(
                f"Mediatype '{self.resource.mediatype}' not supported "
                f"for resource: {self.resource.fullpath.name}"
            )

    def _hash(self) -> str:
        return "Still working on this"

    def generate(self) -> ET.Element:
        self.rootelem.set("AudioTrackID", self.id)

        self.rootelem.append(str_to_element("md", "Type", self.type))

        encoding = newelement("md", "Encoding")
        encoding.append(str_to_element("md", "Codec", self.codec))
        self.rootelem.append(encoding)

        language = str_to_element("md", "Language", self.language)
        if self.dubbed:
            language.set("dubbed", "true")
        else:
            language.set("dubbed", "false")
        self.rootelem.append(language)

        self.rootelem.append(str_to_element("md", "Region", self.region))

        container_root = newelement("manifest", "ContainerReference")
        container_root.append(str_to_element("manifest", "ContainerLocation", self.location))
        hash_root = str_to_element("manifest", "Hash", self.hash)
        hash_root.set("method", "MD5")
        container_root.append(hash_root)
        self.rootelem.append(container_root)
        
        return self.rootelem

class Video:
    def __init__(self, mec: "MEC", resource: "Resource") -> None:
        pass

class Subtitle:
    pass


def episodic(mecgroup: "MECEpisodic") -> ET.Element:
    root = newelement("manifest", "Inventory")
    return root

# def _video() -> ET.Element:
#     pass

# def _subtitle() -> ET.Element:
#     pass

# def _metadata() -> ET.Element:
#     pass