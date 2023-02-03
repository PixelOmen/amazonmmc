from xml.etree import ElementTree as ET

from ..mec import MECGroup, MECEpisodic
from ..enums import WorkTypes
from ..xmlhelpers import newelement, key_to_element, str_to_element


def episodic(mecgroup: MECEpisodic) -> ET.Element:
    root = newelement("manifest", "Inventory")
    for season in mecgroup.seasons:
        print(season.outputname)
        for res in season.media.resources:
            print(res.name)
    for ep in mecgroup.episodes:
        print(ep.outputname)
        for res in ep.media.resources:
            print(res.name)
    return root

# def _audio() -> ET.Element:
#     pass

# def _video() -> ET.Element:
#     pass

# def _subtitle() -> ET.Element:
#     pass

# def _metadata() -> ET.Element:
#     pass