import re
from typing import cast
from pathlib import Path
from dataclasses import dataclass

from . import dataio, mec

currentdir = Path(__file__).parent.parent
testdir = currentdir / "testfiles"
test_mec_output = testdir / "test_mec_output.xml"

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

PARSERS = {
    "feature": dataio.parse_feature,
    "series": dataio.parse_series,
    "season": dataio.parse_season,
    "episode": dataio.parse_episode
}

@dataclass
class Resource:
    type: str
    id: str
    srcpath: Path
    language: str = ""
    codec: str = ""
    framerate: str = ""
    aspectratio: str = ""
    resolution: tuple[str, str] | None = None

class ResourceGroup:
    def __init__(self, coredata: dataio.MECData, rootdir: Path):
        self.coredata = coredata
        self.rootdir = rootdir
        self.datadir = rootdir / "data"
        self.resourcedir = rootdir / "resources"
        self.children = self._gather_children()

    def output_mec(self):
        outputname = f"{self.coredata.title}_{self.coredata.descriptor.upper()}_metadata.xml"
        outputpath = testdir / outputname
        coreroot = mec.create(self.coredata)
        dataio.output_xml(coreroot, outputpath)
        for child in self.children:
            child.output_mec()

    def _gather_children(self) -> list["ResourceGroup"]:
        if self.coredata.type == "feature" or self.coredata.type == "episode":
            return []
        if self.coredata.type == "series":
            seriesdata = cast(dataio.SeriesData, self.coredata)
            seasons = [s for s in seriesdata.seasons if s != ""]
            test = [s for s in self.datadir.iterdir()]
            seasondatafiles = [s for s in self.datadir.iterdir() if s.name.split("_")[0].lower() == "season"]
            if len(seasons) != len(seasondatafiles):
                raise FileNotFoundError("Number of Season data files does not match seasons listed in Series data")
            return [ResourceGroup(PARSERS["season"](s), self.rootdir) for s in seasondatafiles]
        return []
        

class Delivery:
    def __init__(self, rootdir: Path):
        self.rootdir = rootdir
        self.datadir = rootdir / "data"
        self.type = self._delivery_type()
        self.coredata = self._gather_data()
        self.resources = ResourceGroup(self.coredata, self.rootdir)

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
