import enum
from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
from posixpath import split

@dataclass
class MECData:
    type: str
    id: str
    genres: list[str]
    releaseyear: str
    orgid: str
    origlanguage: str
    localizedinfo: list[dict[str,str]]
    altids: list[dict[str,str]]
    ratings: list[dict[str,str]]
    people: list[dict[str,str]]
    companycredits: list[dict[str,str]]

@dataclass
class SeriesData(MECData):
    seasons: list[str]

@dataclass
class SeasonData(MECData):
    episodes: list[str]

@dataclass
class EpData(MECData):
    releasedate: str
    resources: list[dict[str,str]]

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

    def _read_data(self, datapath: Path) -> list[str]:
        with open(str(datapath), "r", encoding="utf-8") as fp:
            maindata_lines = fp.readlines()
        return maindata_lines

    def _parse_multiline(self, data: list[str], startindex: int, multicell: int=...) -> tuple[list[dict[str,str]],int]:
        keys = data[startindex].strip("\n").split(";")[1:-1]
        keys = [k.lower() for k in keys]
        multiline_dicts = []
        endindex = startindex + 1
        for line in data[startindex+1:]:
            splitline = line.strip("\n").split(";")
            if splitline[0] != "":
                break
            emptyline = True
            for remaining in splitline[1:]:
                if remaining != "":
                    emptyline = False
            if emptyline:
                endindex += 1
                break
            if multicell is not ...:
                linedict = self._parse_multicell(keys, splitline[1:], multicell)
            else:
                try:
                    linedict = {keys[i]:v for i,v in enumerate(splitline[1:]) if v != ""}
                except IndexError as r:
                    print(splitline[1:])
                    print("Error parsing CSV, possibly an extra semicolon")
                    exit()
            multiline_dicts.append(linedict)
            endindex += 1
        return multiline_dicts, endindex

    def _parse_multicell(self, keys: list[str], splitline: list[str], multiindex: int) -> dict[str, str]:
        linedict = {}
        valuelist = []
        for index, value in enumerate(splitline):
            if value == "":
                continue
            if index >= multiindex:
                valuelist.append(value)
            else:
               linedict[keys[index]] = value
        linedict[keys[multiindex]] = valuelist
        return linedict
                


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
        series_data = self._read_data(series_datafile)
        id = series_data[0].split(";")[1]
        seasons = series_data[1].split(";")[1:]
        genres = series_data[2].split(";")[1:]
        releaseyear = series_data[3].split(";")[1]
        og_lan = series_data[4].split(";")[1]
        orgid = series_data[5].split(";")[1]
        localinfo, altindex = self._parse_multiline(series_data, 7)
        altids, ratingsindex = self._parse_multiline(series_data, altindex)
        ratings, peopleindex = self._parse_multiline(series_data, ratingsindex)
        people, creditsindex = self._parse_multiline(series_data, peopleindex, 2)
        companycredits, _ = self._parse_multiline(series_data, creditsindex)
        self.series = SeriesData("series", id, genres, releaseyear, orgid, og_lan, localinfo, altids, ratings, people, companycredits, seasons)

    def _parse_season(self):
        pass

    def _parse_episode(self):
        pass

