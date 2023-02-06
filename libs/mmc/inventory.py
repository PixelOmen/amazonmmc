from typing import TYPE_CHECKING
from abc import ABC, abstractmethod
from xml.etree import ElementTree as ET

from ..enums import MediaTypes
from ..xmlhelpers import newelement, str_to_element

if TYPE_CHECKING:
    from ..mec import MEC
    from ..media import Resource

# MOV naming - AMAZONKIDS_HELLOKITTY_SEASON1_101_EN-US_ja-JP_PRORESHQ_5120_25_1920x1080_16x9_HD_178.mov
# Dubbed -     AMAZONKIDS_HELLOKITTY_SEASON1_101_EN-US_ja-JP_PRORESHQ_5120_25_1920x1080_16x9_HD_178_dubbed.mov
# Sub -        AMAZONKIDS_HELLOKITTY_SEASON1_102_EN-US_ja-JP_FULL_SUBTITLE_25.itt

class InventoryElem(ABC):
    def __init__(self, mec: "MEC", resource: "Resource", roottag: str) -> None:
        self.rootelem = newelement("manifest", roottag)
        self.mec = mec
        self.resource = resource
        self.location = f"file://resources/{self.resource.fullpath.name}"
        self.id: str
        self.hash: str

    def _hash(self) -> str:
        return "Still working on this"

    def _trackid(self, tracktype: str, language: str=...) -> str:
        mecid = self.mec.id
        org = self.mec.search_media("AssociatedOrg")
        orgid = org["organizationID"]
        if self.resource.mediatype == MediaTypes.EPISODE:
            seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
            trackid = f"md:{tracktype}:org:{orgid}:{mecid}:episode.{seq}"
            if language is not ...:
                trackid += f".{language}"
            return trackid
        elif self.resource.mediatype == MediaTypes.SEASON:
            raise NotImplementedError(
                f"Unable to generate trackid for tracktype: {tracktype}. "
                f"Mediatype '{self.resource.mediatype}' not implemented yet "
                f"for resource: {self.resource.fullpath.name}"
            )
        elif self.resource.mediatype == MediaTypes.SERIES:
            raise NotImplementedError(
                f"Unable to generate trackid for tracktype: {tracktype}. "
                f"Mediatype '{self.resource.mediatype}' not implemented yet "
                f"for resource: {self.resource.fullpath.name}"
            )
        else:
            raise NotImplementedError(
                f"Unable to generate trackid for tracktype: {tracktype}. "
                f"Mediatype '{self.resource.mediatype}' not supported "
                f"for resource: {self.resource.fullpath.name}"
            )

    @abstractmethod
    def _parse_resource(self) -> None:...

    @abstractmethod
    def generate(self) -> ET.Element:...


class Audio(InventoryElem):
    def __init__(self, mec: "MEC", resource: "Resource") -> None:
        super().__init__(mec, resource, "Audio")
        self.type = "primary"
        self.codec = "PCM"
        self.language: str
        self.dubbed: bool
        self.region: str
        self._parse_resource()
        self.hash = self._hash()

    def _parse_resource(self) -> None:
        split_name = self.resource.fullpath.stem.split("_")
        if self.resource.mediatype == MediaTypes.EPISODE:
            self.language = split_name[4]
            self.dubbed = True if split_name[-1].lower() == "dubbed" else False
            self.region = split_name[5]
            self.id = self._trackid("audtrackid", self.language)
        else:
            raise NotImplementedError(
                f"(AUDIO) Mediatype '{self.resource.mediatype}' not supported "
                f"for resource: {self.resource.fullpath.name}"
            )

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

class Video(InventoryElem):
    def __init__(self, mec: "MEC", resource: "Resource") -> None:
        super().__init__(mec, resource, "Video")
        self.type = "primary"
        self.language: str
        self.region: str
        self.codec: str
        self.width: str
        self.height: str
        self.aspect: str
        self._parse_resource()
        self.hash = self._hash()

    def _parse_resource(self) -> None:
        split_name = self.resource.fullpath.stem.split("_")
        if self.resource.mediatype == MediaTypes.EPISODE:
            self.language = split_name[4]
            self.region = split_name[5]
            self.codec = split_name[6]
            resolution = split_name[9].lower().split("x")
            self.width = resolution[0]
            self.height = resolution[1]
            self.aspect = split_name[10].lower().replace("x", ":")
            self.id = self._trackid("vidtrackid", self.language)
        else:
            raise NotImplementedError(
                f"(VIDEO) Mediatype '{self.resource.mediatype}' not supported "
                f"for resource: {self.resource.fullpath.name}"
            )

    def generate(self) -> ET.Element:
        self.rootelem.set("VideoTrackID", self.id)
        self.rootelem.append(str_to_element("md", "Type", self.type))
        
        encoding = newelement("md", "Encoding")
        encoding.append(str_to_element("md", "Codec", self.codec))
        self.rootelem.append(encoding)

        picture = newelement("md", "Picture")
        picture.append(str_to_element("md", "AspectRatio", self.aspect))
        picture.append(str_to_element("md", "WidthPixels", self.width))
        picture.append(str_to_element("md", "HeightPixels", self.height))
        self.rootelem.append(picture)

        self.rootelem.append(str_to_element("md", "Language", self.language))
        self.rootelem.append(str_to_element("md", "Region", self.region))

        container = newelement("manifest", "ContainerReference")
        container.append(str_to_element("manifest", "ContainerLocation", self.location))
        hash = str_to_element("manifest", "Hash", self.hash)
        hash.set("method", "MD5")
        container.append(hash)
        self.rootelem.append(container)
        return self.rootelem

class Subtitle(InventoryElem):
    def __init__(self, mec: "MEC", resource: "Resource") -> None:
        super().__init__(mec, resource, "Subtitle")
        self.type = "SDH"
        self.language: str
        self.region: str
        self.multiplier: str
        self.fps: str
        self._parse_resource()
        self.hash = self._hash()

    def _parse_resource(self) -> None:
        split_name = self.resource.fullpath.stem.split("_")
        if self.resource.mediatype == MediaTypes.EPISODE:
            self.language = split_name[4]
            self.region = split_name[5]
            fps = split_name[8]
            if len(fps) == 4:
                self.multiplier = "1/1001"
                self.fps = str(round(int(fps)))
            else:
                self.multiplier = "1/1"
                self.fps = fps
            self.id = self._trackid("subtrackid", self.language)
        else:
            raise NotImplementedError(
                f"(SUBTITLE) Mediatype '{self.resource.mediatype}' not supported "
                f"for resource: {self.resource.fullpath.name}"
            )

    def generate(self) -> ET.Element:
        self.rootelem.set("SubtitleTrackID", self.id)
        self.rootelem.append(str_to_element("md", "Type", self.type))

        self.rootelem.append(str_to_element("md", "Language", self.language))
        self.rootelem.append(str_to_element("md", "Region", self.region))
        
        encoding = newelement("md", "Encoding")
        fps = str_to_element("md", "FrameRate", self.fps)
        fps.set("multiplier", self.multiplier)
        encoding.append(fps)
        self.rootelem.append(encoding)

        container = newelement("manifest", "ContainerReference")
        container.append(str_to_element("manifest", "ContainerLocation", self.location))
        hash = str_to_element("manifest", "Hash", self.hash)
        hash.set("method", "MD5")
        container.append(hash)
        self.rootelem.append(container)
        return self.rootelem

class Metadata:
    pass