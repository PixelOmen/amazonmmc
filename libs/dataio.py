from pathlib import Path
from dataclasses import dataclass
from abc import ABC, abstractmethod
from xml.etree import ElementTree as ET

@dataclass
class MECData(ABC):
    type: str
    title: str
    id: str
    genres: list[str]
    releaseyear: str
    orgid: str
    origlanguage: str
    localizedinfo: list[dict[str,str]]
    altids: list[dict[str,str]]
    ratings: list[dict[str,str]]
    companycredits: list[dict[str,str]]

    @property
    @abstractmethod
    def descriptor(self) -> str:...

@dataclass
class FeatureData(MECData):
    people: list[dict[str,str]]

    @property
    def descriptor(self) -> str:
        return self.type

@dataclass
class SeriesData(MECData):
    seasons: list[str]

    @property
    def descriptor(self) -> str:
        return self.type

@dataclass
class SeasonData(MECData):
    parentid: str
    season: str
    sequence: str
    episodes: list[str]
    people: list[dict[str,str]]

    @property
    def descriptor(self) -> str:
        return self.season

@dataclass
class EpisodeData(MECData):
    parentid: str
    episode: str
    sequence: str
    releasedate: str
    releasehistory: list[dict[str, str]]
    people: list[dict[str,str]]
    resources: list[dict[str,str]]

    @property
    def descriptor(self) -> str:
        return self.episode



def read_data(datapath: Path) -> list[str]:
    with open(str(datapath), "r", encoding="utf-8") as fp:
        maindata_lines = fp.readlines()
    return [l.strip("\r\n") for l in maindata_lines]

# indent function adds newlines and tabs to xml so it's not all on 1 line
# pass root element into function
def indent(elem: ET.Element, level: int=0, spaces: int=4):
    i = "\n" + level*(" "*spaces)
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + (" "*spaces)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def output_xml(root, outputpath, encodingtype="UTF-8", xmldecl=True):
    indent(root)
    tree = ET.ElementTree(root)
    tree.write(outputpath, encoding=encodingtype, xml_declaration=xmldecl)



def find_index(data: list[str], key: str) -> int:
    for index,line in enumerate(data):
        if key.lower() == line.split(";")[0].lower():
            return index
    raise IndexError(f"Unable to locate key: {key}")

def parse_multiline(data: list[str], startindex: int, multicell: int=...) -> list[dict[str,str]]:
    keys = data[startindex].strip("\n").split(";")[1:]
    keys = [k.lower() for k in keys]
    multiline_dicts = []
    for line in data[startindex+1:]:
        splitline = line.strip("\n").split(";")
        if splitline[0] != "":
            break
        emptyline = True
        for remaining in splitline[1:]:
            if remaining != "":
                emptyline = False
        if emptyline:
            break
        if multicell is not ...:
            linedict = parse_multicell(keys, splitline[1:], multicell)
        else:
            try:
                linedict = {keys[i]:v for i,v in enumerate(splitline[1:]) if v != ""}
            except IndexError as r:
                print(splitline[1:])
                raise IndexError("Error parsing CSV, possibly an extra semicolon")
        multiline_dicts.append(linedict)
    return multiline_dicts

def parse_multicell(keys: list[str], splitline: list[str], multiindex: int) -> dict[str, str]:
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




def parse_feature():
    pass

def parse_series(seriesfile: Path) -> MECData:
    series_data = read_data(seriesfile)
    title = series_data[find_index(series_data, "title")].split(";")[1]
    id = series_data[find_index(series_data, "id")].split(";")[1]
    seasons = series_data[find_index(series_data, "seasons")].split(";")[1:]
    genres = series_data[find_index(series_data, "genres")].split(";")[1:]
    releaseyear = series_data[find_index(series_data, "releaseyear")].split(";")[1]
    origlanguage = series_data[find_index(series_data, "originallanguage")].split(";")[1]
    orgid = series_data[find_index(series_data, "organizationid")].split(";")[1]
    localizedinfo = parse_multiline(series_data, find_index(series_data, "localizedinfo"))
    altids = parse_multiline(series_data, find_index(series_data, "altids"))
    ratings = parse_multiline(series_data, find_index(series_data, "ratings"))
    companycredits = parse_multiline(series_data, find_index(series_data, "companycredits"))
    return SeriesData(
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
        companycredits=companycredits,
        seasons=seasons
    )

def parse_season(seasonfile: Path):
    series_data = read_data(seasonfile)
    parentid = series_data[find_index(series_data, "parentid")].split(";")[1]
    title = series_data[find_index(series_data, "title")].split(";")[1]
    id = series_data[find_index(series_data, "id")].split(";")[1]
    season = series_data[find_index(series_data, "season")].split(";")[1]
    sequence = series_data[find_index(series_data, "sequence")].split(";")[1]
    episodes = series_data[find_index(series_data, "episodes")].split(";")[1:]
    genres = series_data[find_index(series_data, "genres")].split(";")[1:]
    releaseyear = series_data[find_index(series_data, "releaseyear")].split(";")[1]
    origlanguage = series_data[find_index(series_data, "originallanguage")].split(";")[1]
    orgid = series_data[find_index(series_data, "organizationid")].split(";")[1]
    localizedinfo = parse_multiline(series_data, find_index(series_data, "localizedinfo"))
    altids = parse_multiline(series_data, find_index(series_data, "altids"))
    ratings = parse_multiline(series_data, find_index(series_data, "ratings"))
    people = parse_multiline(series_data, find_index(series_data, "people"), 2)
    companycredits = parse_multiline(series_data, find_index(series_data, "companycredits"))
    return SeasonData(
        type="season",
        title=title,
        parentid=parentid,
        id=id,
        season=season,
        sequence=sequence,
        episodes=episodes,
        genres=genres,
        releaseyear=releaseyear,
        orgid=orgid,
        origlanguage=origlanguage,
        localizedinfo=localizedinfo,
        altids=altids,
        ratings=ratings,
        people=people,
        companycredits=companycredits,
    )

def parse_episode(episodefile: Path):
    episode_data = read_data(episodefile)
    parentid = episode_data[find_index(episode_data, "parentid")].split(";")[1]
    title = episode_data[find_index(episode_data, "title")].split(";")[1]
    id = episode_data[find_index(episode_data, "id")].split(";")[1]
    episode = episode_data[find_index(episode_data, "episode")].split(";")[1]
    sequence = episode_data[find_index(episode_data, "sequence")].split(";")[1]
    genres = episode_data[find_index(episode_data, "genres")].split(";")[1:]
    releaseyear = episode_data[find_index(episode_data, "releaseyear")].split(";")[1]
    releasedate = episode_data[find_index(episode_data, "releasedate")].split(";")[1]
    origlanguage = episode_data[find_index(episode_data, "originallanguage")].split(";")[1]
    orgid = episode_data[find_index(episode_data, "organizationid")].split(";")[1]
    releasehistory = parse_multiline(episode_data, find_index(episode_data, "releasehistory"))
    localizedinfo = parse_multiline(episode_data, find_index(episode_data, "localizedinfo"))
    altids = parse_multiline(episode_data, find_index(episode_data, "altids"))
    ratings = parse_multiline(episode_data, find_index(episode_data, "ratings"))
    people = parse_multiline(episode_data, find_index(episode_data, "people"), 2)
    companycredits = parse_multiline(episode_data, find_index(episode_data, "companycredits"))
    resources = parse_multiline(episode_data, find_index(episode_data, "resources"))
    return EpisodeData(
        type="episode",
        title=title,
        parentid=parentid,
        id=id,
        episode=episode,
        sequence=sequence,
        genres=genres,
        releaseyear=releaseyear,
        releasedate=releasedate,
        releasehistory=releasehistory,
        orgid=orgid,
        origlanguage=origlanguage,
        localizedinfo=localizedinfo,
        altids=altids,
        ratings=ratings,
        people=people,
        companycredits=companycredits,
        resources=resources
    )