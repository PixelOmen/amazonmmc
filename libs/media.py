import re
from pathlib import Path
from typing import cast

from . import dataio, mec

currentdir = Path(__file__).parent.parent
test_mec_output = currentdir / "testfiles" / "test_mec_output.xml"

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
    def __init__(self, type: str, filename: str):
        pass

class ResourceGroup:
    def __init__(self, coredata: dataio.MECData, rootdir: Path):
        self.coredata = coredata
        self.rootdir = rootdir
        self.datadir = rootdir / "data"
        self.resourcedir = rootdir / "resources"

    def output_mec(self):
        if self.coredata.type.lower() != "episode":
            outputname = f"{self.coredata.title}_{self.coredata.type.upper()}_metadata.xml"
        else:
            coredata = cast(dataio.EpisodeData, self.coredata)
            outputname = f"{self.coredata.title}_{coredata.episode.upper()}_metadata.xml"
        outputpath = self.resourcedir / outputname
        coreroot = mec.create(self.coredata)
        dataio.output_xml(coreroot, test_mec_output)

class Delivery:
    def __init__(self, rootdir: Path):
        self.rootdir = rootdir
        self.datadir = rootdir / "data"
        self.type = self._delivery_type()
        self.coregroup = self._gather_data()

    def _delivery_type(self) -> str:
        for file in self.datadir.iterdir():
            splitname = file.name.split("_")[0].lower()
            if splitname == "feature":
                return "feature"
            if splitname == "series":
                return "series"
        raise FileNotFoundError("Unable to determine delivery type")

    def _gather_data(self) -> ResourceGroup:
        parsers = {
            "feature": self._parse_feature,
            "series": self._parse_series,
            "season": self._parse_season,
            "episode": self._parse_season
        }
        return parsers[self.type]()

    def _parse_feature(self):
        pass

    def _parse_series(self) -> ResourceGroup:
        series_datafile = None
        for file in self.datadir.iterdir():
            if file.name.split("_")[0].lower() == "series":
                series_datafile = file
                break
        if not series_datafile:
            raise FileNotFoundError("Unable to locate series data")
        series_data = dataio.read_data(series_datafile)
        title = series_data[dataio.find_index(series_data, "title")].split(";")[1]
        id = series_data[dataio.find_index(series_data, "id")].split(";")[1]
        seasons = series_data[dataio.find_index(series_data, "seasons")].split(";")[1:]
        genres = series_data[dataio.find_index(series_data, "genres")].split(";")[1:]
        releaseyear = series_data[dataio.find_index(series_data, "releaseyear")].split(";")[1]
        origlanguage = series_data[dataio.find_index(series_data, "originallanguage")].split(";")[1]
        orgid = series_data[dataio.find_index(series_data, "organizationid")].split(";")[1]
        localizedinfo, altindex = dataio.parse_multiline(series_data, dataio.find_index(series_data, "localizedinfo"))
        altids, ratingsindex = dataio.parse_multiline(series_data, altindex)
        ratings, peopleindex = dataio.parse_multiline(series_data, ratingsindex)
        people, creditsindex = dataio.parse_multiline(series_data, peopleindex, 2)
        companycredits, _ = dataio.parse_multiline(series_data, creditsindex)
        coredata = dataio.SeriesData(
            type="series",
            title=title,
            id=id,
            genres=genres,
            releaseyear=releaseyear,
            orgid=orgid,
            origlanguage=origlanguage,
            localizedinfo=localizedinfo,
            altids=altids,
            ratings=ratings,
            people=people,
            companycredits=companycredits,
            seasons=seasons
        )
        return ResourceGroup(coredata, self.rootdir)

    def _parse_season(self):
        pass

    def _parse_episode(self):
        pass

