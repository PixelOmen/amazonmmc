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
    people: list[dict[str,str]]
    companycredits: list[dict[str,str]]

    @property
    @abstractmethod
    def descriptor(self) -> str:...

@dataclass
class FeatureData(MECData):
    
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
    season: str
    episodes: list[str]

    @property
    def descriptor(self) -> str:
        return self.season

@dataclass
class EpisodeData(MECData):
    episode: str
    releasedate: str
    resources: list[dict[str,str]]

    @property
    def descriptor(self) -> str:
        return self.episode


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