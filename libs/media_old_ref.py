import re
from pathlib import Path
from abc import ABC, abstractmethod

RE_EPISODE = re.compile(r"_S\d\dE\d\d\d_", re.IGNORECASE)

ACCEPTED_FILETYPES = [".mov", ".scc", ".wav", ".xml"]

VIDEO_FILETYPES = [".mov"]

ID_PREFIX = {
    "audio": "md:audtrackid",
    "video": "md:vidtrackid",
    "subtitle": "md:subtrackid",
    "metadata": "md:cid",
    "experience": "md:experienceid"
}


class Resource:
    def __init__(self, srcpath: Path):
        self.srcpath = srcpath
        self.type = self._parsetype()
        self.splitname = self._splitname()
        self.studio = self.splitname[0].lower()
        self.title = self.splitname[1]
        self.descriptor = self.splitname[2]
        self.audioconfigs = self._language_and_audio(self.splitname[3])
        if not self.audioconfigs and self.type != "metadata":
            self.language = self.splitname[3]
        elif self.type == "video":
            self.language = self.audioconfigs[0][0]
        resolution = self.splitname[4]
        if resolution.lower() != "na":
            resolution = resolution.replace("X", "x")
            self.resolution = tuple(resolution.split("x"))
        self.aspectratio = self.splitname[5]
        self.framerate = self.splitname[6]
        self.id = self._genid()

    def video_as_audio(self) -> list["Resource"]:
        audioresources = []
        for config in self.audioconfigs:
            res = Resource(self.srcpath)
            res.type = "audio"
            res.audioconfigs = [config]
            res.language = config[0]
            res.id = res._genid()
            audioresources.append(res)
        return audioresources

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
        if len(splitname) != 8:
            raise ValueError(f"Invalid naming convention: {self.srcpath.name}")
        return splitname

    def _language_and_audio(self, audiostr: str) -> list[tuple[str, str]]:
        if self.type not in ["audio", "video"] or audiostr.lower() == "mos":
            return []
        splitaudio = audiostr.split("-")
        audioconfig = ("-".join(splitaudio[:2]), "-".join(splitaudio[2:]))
        return [audioconfig]

    def _genid(self) -> str:
        prefix = ID_PREFIX[self.type]
        id_uuid, id_descrip = self._id_descriptors()
        start = f"{prefix}:org:{self.studio.lower()}:{id_uuid}:"
        match self.type:
            case "video" | "metadata":
                end = f"{id_descrip}.{self.type}"
            case "audio":
                end = f"{id_descrip}.audio_{self.audioconfigs[0][1]}.{self.language[:2].lower()}"
            case "subtitle":
                end = f"{id_descrip}.caption.{self.language[:2].lower()}"
            case _:
                raise ValueError(f"Unable to generate ID, unknown type: {self.type}")
        return start+end

    def _id_descriptors(self) -> tuple[str,str]:
        if self.descriptor.lower() == "ftr":
            return self.title, "feature"
        if self.descriptor.lower() == "series":
            return self.title, "series"
        if re.search(r"S\d\d$", self.descriptor, re.IGNORECASE) != None:
            return f"{self.title}_{self.descriptor}", "season"
        if re.search(r"S\d\dE\d\d\d$", self.descriptor, re.IGNORECASE) != None:
            return f"{self.title}_{self.descriptor}", "episode"
        raise ValueError(f"Unable to generate ID, unknown descriptor: {self.descriptor}")



class Content(ABC):
    def __init__(self, title:str, descriptor: str, resourcedir: Path):
        self.title = title
        self.descriptor = descriptor
        self.resourcedir = resourcedir
        self.allresources = self._gather_resources()
        self.video: list[Resource] = []
        self.audio: list[Resource] = []
        self.subtitles: list[Resource] = []
        self.metadata: list[Resource] = []
        self.resdict = {
            "video": self.video,
            "audio": self.audio,
            "subtitle": self.subtitles,
            "metadata": self.metadata
        }
        self._parse_resources()
        self.presid = f"md:presentationid:{self.title}_{self.descriptor}"
        self.expid = f"md:experienceid:{self.title}_{self.descriptor}"

    def is_metadata_only(self) -> bool:
        ismeta = True
        for key, resources in self.resdict.items():
            if key == "metadata":
                continue
            if resources:
                ismeta = False
        return ismeta

    @abstractmethod
    def _gather_resources(self) -> list[Resource]:...

    def _parse_resources(self):
        for res in self.allresources:
            if res.type == "video":
                self.video.append(res)
                continue
            self.resdict[res.type].append(res)
        if (not self.audio and 
            re.search(r"S\d\d$", self.descriptor, re.IGNORECASE) == None and
            re.search(r"S\d\dE\d\d\d$", self.descriptor, re.IGNORECASE == None)):
                self.audio += self.video[0].video_as_audio()

class Feature(Content):
    def _gather_resources(self) -> list[Resource]:
        return [Resource(f) for f in self.resourcedir.iterdir() if f.name[0] != "."]        

class Episode(Content):
    def _gather_resources(self) -> list[Resource]:
        return [Resource(f) for f in self.resourcedir.iterdir()
                if f.name[0] != "." and f"{self.title}_{self.descriptor}_" in f.name]


class Delivery:
    def __init__(self, rootdir: Path):
        self.rootdir: Path = rootdir
        self.resourcesdir: Path = rootdir / "resources"
        self.allfiles: list[Path] = self._parsefiles()
        self.title = self._parsetitle()
        self.type: str = self._parsetype()
        self.content: list[Content] = self._get_content()
        self.seasonmeta, self.seriesmeta = self._get_deliv_meta()


    def _parsefiles(self) -> list[Path]:
        allfiles = [f for f in self.resourcesdir.iterdir()
                    if f.name[0] != "." and f.suffix in ACCEPTED_FILETYPES]
        if len(allfiles) < 1:
            raise FileNotFoundError("No resources found")
        return allfiles

    def _parsetitle(self) -> str:
        splitname = self.allfiles[0].name.split("_")
        if len(splitname) != 8:
            raise ValueError(f"Invalid naming convention: {self.allfiles[0].name}")
        return splitname[1]

    def _parsetype(self) -> str:
        for f in self.allfiles:
            if "_ftr_" in f.name.lower():
                return "ftr"
            ep = RE_EPISODE.search(f.name)
            if ep:
                return "ep"
        raise LookupError("Unable to determine delivery type")

    def _get_content(self) -> list[Content]:
        if self.type == "ftr":
            return [Feature(self.title, "ftr", self.resourcesdir)]
        episodes = []
        for f in self.allfiles:
            if f.name[0] == ".":
                continue
            result = RE_EPISODE.search(f.name)
            if result:
                ep = result.group()[1:-1]
                if ep not in episodes:
                    episodes.append(ep)
        alleps: list[Content] = [Episode(self.title, ep, self.resourcesdir) for ep in episodes]
        allused = [f.srcpath.name for e in alleps for f in e.allresources]
        for f in self.allfiles:
            if f.name not in allused:
                descriptor = f.name.split("_")[2]
                alleps.append(Episode(self.title, descriptor, self.resourcesdir))
        return alleps

    def _get_deliv_meta(self) -> tuple[Content, Content]:
        season = ""
        series = ""
        for c in self.content:
            if c.is_metadata_only():
                if c.descriptor.lower() == "series":
                    series = c
                else:
                    season = c
        if not season:
            raise FileNotFoundError("Unable to locate season metadata")
        if not series:
            raise FileNotFoundError("Unable to locate series metadata")
        return season, series