import re
from pathlib import Path
from typing import Generator

from . import inventory

FACTORIES = {
    "audio": inventory.audio,
    "video": inventory.video,
    "subtitle": inventory.subtitle,
    "metadata": inventory.metadata
}

RE_EPISODE = re.compile(r"_S\d\dE\d\d\d_", re.IGNORECASE)

ID_PREFIX = {
    "audio": "md:audtrackid",
    "video": "md:vidtrackid",
    "subtitle": "md:subtrackid",
    "metadata": "md:cid"
}

class Resource:
    def __init__(self, srcpath: Path, eidr: str):
        self.srcpath = srcpath
        self.eidr = eidr
        self.type = self._parsetype()
        self.splitname = self._splitname()
        self.studio = self.splitname[0].lower()
        self.title = self.splitname[1]
        self.descriptor = self.splitname[2]
        self.audioconfigs = self._language_and_audio(self.splitname[3])
        self.language = self.splitname[3] if not self.audioconfigs and self.type != "metadata" else ""
        self.aspectratio = self.splitname[4]
        self.framerate = self.splitname[5]
        self.id = self._genid()

    def _parsetype(self) -> str:
        match self.srcpath.suffix:
            case ".mov":
                return "video"
            case ".wav":
                return "audio"
            case ".scc":
                return "subtitle"
            case ".xml":
                return "metadata"
            case _:
                raise TypeError(f"Unsupported filetype: {self.srcpath.name}")

    def _splitname(self) -> list[str]:
        splitname = self.srcpath.name.split("_")
        if len(splitname) != 7:
            raise NameError(f"Invalid naming convention: {self.srcpath.name}")
        return splitname

    def _language_and_audio(self, audiostr: str) -> list[tuple[str, str, str]]:
        if self.type not in ["audio", "video"] or audiostr.lower() == "mos":
            return []
        splitaudio = audiostr.split("-")
        audioconfigs = []
        start = 0
        end = 3
        for _ in range(int(len(splitaudio)/3)):
            group = splitaudio[start:end]
            lan = f"{group[0]}-{group[1]}"
            audio = group[2]
            audioconfigs.append((lan, audio))
            start = end
            end += 3
        return audioconfigs

    def _genid(self) -> str:
        prefix = ID_PREFIX[self.type]
        start = f"{prefix}:org:{self.title}:{self.studio.lower()}:"
        id_descrip = self._id_descriptor()
        
        match self.type:
            case "video" | "metadata":
                end = f"{id_descrip}.{self.type}"
            case "audio":
                end = f"{id_descrip}.audio.{self.language[:2].lower()}"
            case "subtitle":
                end = f"{id_descrip}.caption.{self.language[:2].lower()}"
            case _:
                raise TypeError(f"Unable to generate ID, unknown type: {self.type}")

        return start+end
    
    def _id_descriptor(self) -> str:
        if self.descriptor.lower() == "ftr":
            return "feature"
        if self.descriptor.lower() == "series":
            return "series"
        if re.search(r"S\d\d$", self.descriptor, re.IGNORECASE) != None:
            return f"season_{self.descriptor[1:]}"
        if re.search(r"S\d\dE\d\d\d$", self.descriptor, re.IGNORECASE) != None:
            return f"episode_{self.descriptor[4:]}"
        raise TypeError(f"Unable to generate ID, unknown descriptor: {self.descriptor}")

class Content:
    def __init__(self, content_type: str, resourcedir: Path):
        self.type = content_type
        self.resourcedir = resourcedir

class Delivery:
    def __init__(self, rootdir: Path):
        self.rootdir: Path = rootdir
        self.resourcesdir: Path = rootdir / "resources"
        self.mmc: Path = self._get_mmc()
        self.eidr: str = self.mmc.stem
        self.type: str = self._parsetype()
        self.allfiles: Generator[Path, None, None] = self.resourcesdir.iterdir()
        self.content: list[Content] = self._get_resources()

    def _get_mmc(self) -> Path:
        mmc = [m for m in self.rootdir.iterdir() if m.suffix.lower() == ".xml"]
        if len(mmc) < 1:
            raise FileNotFoundError("MMC not found")
        if len(mmc) > 1:
            raise ValueError("Multiple xmls detected in root")
        return mmc[0]

    def _parsetype(self) -> str:
        for f in self.allfiles:
            if "_ftr_" in f.name.lower():
                return "ftr"
            ep = RE_EPISODE.search(f.name)
            if ep:
                return "ep"
        raise LookupError("Unable to determine delivery type")

    def _get_resources(self) -> list[Content]:
        if self.type == "ftr":
            return [Content("ftr", self.resourcesdir)]
        episodes = []
        for f in self.allfiles:
            if f.name[0] == ".":
                continue
            result = RE_EPISODE.search(f.name)
            if result:
                ep = result.group()
                if ep not in episodes:
                    episodes.append(ep)