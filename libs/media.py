import re
from pathlib import Path
from abc import ABC, abstractmethod

from . import dataparser

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
    pass

class Delivery:
    def __init__(self, rootdir: Path):
        self.rootdir = rootdir
        self.datadir = rootdir / "data"
        self.resourcedir = rootdir / "resources"
        self.type = self._delivery_type()
        self._gather_child_data()

    def _delivery_type(self) -> str:
        for file in self.datadir.iterdir():
            splitname = file.name.split("_")[0].lower()
            if splitname == "feature":
                return "feature"
            if splitname == "series":
                return "series"
        raise FileNotFoundError("Unable to determine delivery type")

    def _gather_child_data(self):
        parsers = {
            "feature": self._parse_feature,
            "series": self._parse_series,
            "season": self._parse_season,
            "episode": self._parse_season
        }
        parsers[self.type]()               

    def _parse_feature(self):
        pass

    def _parse_series(self):
        series_datafile = None
        for file in self.datadir.iterdir():
            if file.name.split("_")[0].lower() == "series":
                series_datafile = file
                break
        if not series_datafile:
            raise FileNotFoundError("Unable to locate series data")
        series_data = dataparser.read_data(series_datafile)
        id = series_data[dataparser.find_index(series_data, "id")].split(";")[1]
        seasons = series_data[dataparser.find_index(series_data, "seasons")].split(";")[1:]
        genres = series_data[dataparser.find_index(series_data, "genres")].split(";")[1:]
        releaseyear = series_data[dataparser.find_index(series_data, "releaseyear")].split(";")[1]
        origlanguage = series_data[dataparser.find_index(series_data, "originallanguage")].split(";")[1]
        orgid = series_data[dataparser.find_index(series_data, "organizationid")].split(";")[1]
        localizedinfo, altindex = dataparser.parse_multiline(series_data, dataparser.find_index(series_data, "localizedinfo"))
        altids, ratingsindex = dataparser.parse_multiline(series_data, altindex)
        ratings, peopleindex = dataparser.parse_multiline(series_data, ratingsindex)
        people, creditsindex = dataparser.parse_multiline(series_data, peopleindex, 2)
        companycredits, _ = dataparser.parse_multiline(series_data, creditsindex)
        self.series = dataparser.SeriesData(
            type="series",
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

    def _parse_season(self):
        pass

    def _parse_episode(self):
        pass

