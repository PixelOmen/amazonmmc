from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from ..enums import MediaTypes
from ..xmlhelpers import newelement, str_to_element

if TYPE_CHECKING:
    from ..mec import MEC
    from ..media import Resource
    from xml.etree import ElementTree as ET

# MOV naming - AMAZONKIDS_HELLOKITTY_SEASON1_101_EN-US_ja-JP_PRORESHQ_5120_25_1920x1080_16x9_HD_178.mov
# Dubbed -     AMAZONKIDS_HELLOKITTY_SEASON1_101_EN-US_ja-JP_PRORESHQ_5120_25_1920x1080_16x9_HD_178_dubbed.mov
# Sub -        AMAZONKIDS_HELLOKITTY_SEASON1_102_EN-US_ja-JP_FULL_SUBTITLE_25.itt

class InventoryElem(ABC):
    def __init__(self, mec: "MEC", roottag: str, checksums: list[str], resource: "Resource"=...) -> None:
        self.rootelem = newelement("manifest", roottag)
        self.mec = mec
        self.checksums = checksums
        self.resource = resource
        if resource is ...:
            self.filepath = self.mec.outputname
        else:
            self.filepath = self.resource.fullpath.name
        self.location = f"file://resources/{self.filepath}"
        self.id: str
        self.hash: str

    def _hash(self) -> str:
        if not self.checksums:
            raise LookupError("MD5 Checksum file is empty")
        for md5 in self.checksums:
            splitline = md5.split(" ")
            if splitline[1].lower() == self.filepath.lower():
                return splitline[0]
        raise LookupError(f"Unable to locate hash for {self.filepath}")

    def _trackid(self, tracktype: str, language: str=...) -> str:
        mecid = self.mec.id
        orgid = self.mec.org
        if self.resource is ...:
            mediatype = self.mec.media.mediatype
            resname = self.mec.outputname
        else:
            mediatype = self.resource.mediatype
            resname = self.resource.fullpath.name
        if mediatype == MediaTypes.EPISODE:
            seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
            trackid = f"md:{tracktype}:org:{orgid}:{mecid}:episode.{seq}"
            if language is not ...:
                trackid += f".{language}"
            return trackid
        elif mediatype == MediaTypes.SEASON:
            seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
            return f"md:{tracktype}:org:{orgid}:{mecid}:season.{seq}"
        elif mediatype == MediaTypes.SERIES:
            return f"md:{tracktype}:org:{orgid}:{mecid}:series"
        else:
            raise NotImplementedError(
                f"Unable to generate trackid for tracktype: {tracktype}. "
                f"Mediatype '{MediaTypes.get_str(mediatype)}' not supported "
                f"for resource: {resname}"
            )

    @abstractmethod
    def _initialize(self) -> None:...

    @abstractmethod
    def generate(self) -> "ET.Element":...


class Audio(InventoryElem):
    def __init__(self, mec: "MEC", checksums: list[str], resource: "Resource") -> None:
        super().__init__(mec, "Audio", checksums, resource)
        self.type = "primary"
        self.codec = "PCM"
        self.language: str
        self.dubbed: bool
        self.region: str
        self._initialize()
        self.hash = self._hash()

    def _initialize(self) -> None:
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

    def generate(self) -> "ET.Element":
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
    def __init__(self, mec: "MEC", checksums: list[str], resource: "Resource") -> None:
        super().__init__(mec, "Video", checksums, resource)
        self.type = "primary"
        self.language: str
        self.region: str
        self.codec: str
        self.width: str
        self.height: str
        self.aspect: str
        self._initialize()
        self.hash = self._hash()

    def _initialize(self) -> None:
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

    def generate(self) -> "ET.Element":
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
    def __init__(self, mec: "MEC", checksums: list[str], resource: "Resource") -> None:
        super().__init__(mec, "Subtitle", checksums, resource)
        self.type = "SDH"
        self.language: str
        self.region: str
        self.multiplier: str
        self.fps: str
        self._initialize()
        self.hash = self._hash()

    def _initialize(self) -> None:
        split_name = self.resource.fullpath.stem.split("_")
        if self.resource.mediatype == MediaTypes.EPISODE:
            self.language = split_name[4]
            self.region = split_name[5]
            fps = split_name[8]
            if len(fps) == 4:
                self.multiplier = "1000/1001"
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

    def generate(self) -> "ET.Element":
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

class Metadata(InventoryElem):
    def __init__(self, mec: "MEC", checksums: list[str]) -> None:
        super().__init__(mec, "Metadata", checksums)
        self.type = "common"
        self.id: str
        self._initialize()
        self.hash = self._hash()

    def _initialize(self) -> None:
        self.id = self._trackid("cid")

    def generate(self) -> "ET.Element":
        self.rootelem.set("ContentID", self.id)
        container = newelement("manifest", "ContainerReference")
        container.set("type", self.type)
        container.append(str_to_element("manifest", "ContainerLocation", self.location))
        hash = str_to_element("manifest", "Hash", self.hash)
        hash.set("method", "MD5")
        container.append(hash)
        self.rootelem.append(container)
        return self.rootelem