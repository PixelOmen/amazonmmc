import re
from pathlib import Path
from dataclasses import dataclass
from typing import cast, TYPE_CHECKING

from . import dataio, mec, mmc

if TYPE_CHECKING:
    from xml.etree import ElementTree as ET

TEST = False

CURRENTDIR = Path(__file__).parent.parent
TESTDIR = CURRENTDIR / "testfiles"

RE_EPISODE = re.compile(r"_S\d\dE\d\d\d_", re.IGNORECASE)

ACCEPTED_FILETYPES = [".mov", ".scc", ".wav", ".xml"]
VIDEO_FILETYPES = [".mov"]

PARSERS = {
    "feature": dataio.parse_feature,
    "series": dataio.parse_series,
    "season": dataio.parse_season,
    "episode": dataio.parse_episode
}

@dataclass
class Resource:
    type: str
    srcpath: Path
    language: str = ""
    codec: str = ""
    framerate: str = ""
    aspectstr: str = ""
    resolutionstr: str = ""
    resourceid: str = ""
    hash: str = ""
    def __post_init__(self):
        self.resolution = self.resolutionstr.replace("X", "x").split("x")
        self.aspect = self.aspectstr.replace("X", "x").replace("x", ":")

class ResourceGroup:
    def __init__(self, coredata: dataio.MECData, rootdir: Path):
        self.coredata = coredata
        self.rootdir = rootdir
        self.datadir = rootdir / "data"
        self.resourcedir = rootdir / "resources"
        self.children = self._gather_children()
        self.resources = self._gather_resources()
        self.presid = ""
        self.expid = ""

    def get_mec(self) -> list[tuple["ET.Element", Path]]:
        all_mecs = []
        mec_name = f"{self.coredata.title}_{self.coredata.descriptor.upper()}_metadata.xml"
        outputdir = TESTDIR if TEST else self.resourcedir
        outputpath = outputdir / mec_name
        self.mec = Resource(type="metadata", srcpath=outputpath)
        self.resources.append(self.mec)
        coreroot = mec.create(self.coredata)
        all_mecs.append((coreroot, outputpath))
        for child in self.children:
            all_mecs += child.get_mec()
        return all_mecs            

    def allresources(self) -> list[Resource]:
        allresources = []
        for child in self.children:
            for resource in child.resources:
                allresources.append(resource)
            allresources += child.allresources()
        return allresources

    def _gather_children(self) -> list["ResourceGroup"]:
        if self.coredata.type == "feature" or self.coredata.type == "episode":
            return []
        if self.coredata.type == "series":
            seasondata = cast(dataio.SeriesData, self.coredata)
            seasons = [s.lower() for s in seasondata.seasons if s != ""]
            seasondatafiles = [s for s in self.datadir.iterdir() if s.stem.split("_")[0].lower() == "season" and s.stem.split("_")[1].lower() in seasons]
            if len(seasons) != len(seasondatafiles):
                raise FileNotFoundError("Number of Season data files does not match seasons listed in Series data")
            return [ResourceGroup(PARSERS["season"](s), self.rootdir) for s in seasondatafiles]
        if self.coredata.type == "season":
            seasondata = cast(dataio.SeasonData, self.coredata)
            episodes = [e.lower() for e in seasondata.episodes if e != ""]
            episodedatafiles = [e for e in self.datadir.iterdir() if e.stem.split("_")[0].lower() == "episode" and e.stem.split("_")[1].lower() in episodes]
            if len(episodes) != len(episodedatafiles):
                raise FileNotFoundError("Number of Episode data files does not match episodes listed in Season data")
            return [ResourceGroup(PARSERS["episode"](e), self.rootdir) for e in episodedatafiles]
        raise FileNotFoundError("Bad coredata type")

    def _gather_resources(self) -> list[Resource]:
        if self.coredata.type != "feature" and self.coredata.type != "episode":
            return []
        resources = []
        resdata = cast(dataio.EpisodeData, self.coredata)
        for res in resdata.resources:
            filepath = self.resourcedir / res["filename"]
            if not filepath.is_file():
                raise FileNotFoundError(f"Unable to locate resource: {res['filename']}")
            resources.append(Resource(
                type=res["type"],
                srcpath=filepath,
                language=res["language"],
                codec=res["codec"],
                framerate=res["framerate"],
                aspectstr=res["aspect"],
                resolutionstr=res["resolution"],
            ))
        return resources
        

class Delivery:
    def __init__(self, rootdir: Path):
        self.rootdir = rootdir
        self.datadir = rootdir / "data"
        self.type = self._delivery_type()
        self.coredata = self._gather_data()
        self.checksums = self._get_checksums()
        self.toplevelgroup = ResourceGroup(self.coredata, self.rootdir)

    def output_mec(self) -> None:
        mecdata = self.toplevelgroup.get_mec()
        for root, outputpath in mecdata:
            dataio.output_xml(root, outputpath)

    def output_mmc(self) -> None:
        allresources = self.toplevelgroup.allresources()
        checksums = self._get_checksums()
        for res in allresources:
            hash = checksums[res.srcpath.name]
            if not hash:
                raise LookupError(f"Unable to locate hash value: {res.srcpath.name}")
            res.hash = hash
        mmc_tree = mmc.create(self.toplevelgroup)
        outputdir = TESTDIR if TEST else self.rootdir
        dataio.output_xml(mmc_tree, outputdir / f"{self.coredata.title}_MMC.xml")

    def _delivery_type(self) -> str:
        for file in self.datadir.iterdir():
            splitname = file.name.split("_")[0].lower()
            if splitname == "feature":
                return "feature"
            if splitname == "series":
                return "series"
        raise FileNotFoundError("Unable to determine delivery type")

    def _gather_data(self) -> dataio.MECData:
        datafile = None
        for file in self.datadir.iterdir():
            if file.name.split("_")[0].lower() == self.type:
                datafile = file
                break
        if not datafile:
            raise FileNotFoundError("Unable to locate top level data")
        return PARSERS[self.type](datafile)

    def _get_checksums(self) -> dict[str, str]:
        checksumpath = self.datadir / "checksums.txt"
        if not checksumpath.is_file():
            raise FileNotFoundError("Unable to locate checksum data")
        alldata = dataio.read_data(self.datadir / "checksums.txt")
        checksumdata = {}
        for line in alldata:
            splitdata = line.split("=")
            checksumdata[splitdata[0]] = splitdata[1]
        return checksumdata