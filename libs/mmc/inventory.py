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
        self.mec = mec
        self.resource = resource
        self.type = "primary"
        self.encoding = "PCM"
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
        split_name = self.resource.fullpath.name.split("_")
        if self.resource.mediatype == MediaTypes.EPISODE:
            self.language = split_name[4]
            self.dubbed = True if split_name[-1].lower() == "dubbed" else False
            self.region = split_name[5]
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
        return ""

class Video:
    pass

class Subtitle:
    pass


def episodic(mecgroup: "MECEpisodic") -> ET.Element:
    root = newelement("manifest", "Inventory")
    return root

# def _episodic_factory(mecgroup: "MECEpisodic") -> Series:
#     av_exts: list[str] = mecgroup.generalmedia.find("av_exts")
#     sub_exts: list[str] = mecgroup.generalmedia.find("sub_exts")
#     av_res: list["Resource"] = []
#     sub_res: list["Resource"] = []
#     for ep in mecgroup.episodes:
#         for res in ep.media.resources:
#             suffix = res.fullpath.suffix.lower()
#             if suffix in av_exts and res not in av_res:
#                 av_res.append(res)
#             elif suffix in sub_exts and res not in sub_res:
#                 sub_res.append(res)
#     return av_res, sub_res

# def _audio(audio: Audio) -> ET.Element:
#     pass

# def _video() -> ET.Element:
#     pass

# def _subtitle() -> ET.Element:
#     pass

# def _metadata() -> ET.Element:
#     pass