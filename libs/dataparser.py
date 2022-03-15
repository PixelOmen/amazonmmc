from pathlib import Path
from dataclasses import dataclass

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


def read_data(datapath: Path) -> list[str]:
    with open(str(datapath), "r", encoding="utf-8") as fp:
        maindata_lines = fp.readlines()
    return maindata_lines

def find_index(data: list[str], key: str) -> int:
    for index,line in enumerate(data):
        if key.lower() == line.split(";")[0].lower():
            return index
    raise IndexError(f"Unable to locate key: {key}")

def parse_multiline(data: list[str], startindex: int, multicell: int=...) -> tuple[list[dict[str,str]],int]:
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
            linedict = parse_multicell(keys, splitline[1:], multicell)
        else:
            try:
                linedict = {keys[i]:v for i,v in enumerate(splitline[1:]) if v != ""}
            except IndexError as r:
                print(splitline[1:])
                raise IndexError("Error parsing CSV, possibly an extra semicolon")
        multiline_dicts.append(linedict)
        endindex += 1
    return multiline_dicts, endindex

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

