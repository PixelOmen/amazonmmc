from xml.etree import ElementTree as ET

from ..mec import MECGroup, MECEpisodic
from ..enums import WorkTypes
from ..xmlhelpers import newelement, key_to_element, str_to_element


def episodic(mecgroup: MECEpisodic) -> ET.Element:
    root = newelement("manifest", "Inventory")
    if mecgroup.worktype != WorkTypes.EPISODIC:
        worktype = WorkTypes.get_str(mecgroup.worktype)
        msg = f"MMC.episodic called on MECGroup.worktype: {worktype}"
        raise RuntimeError(msg)
    for ep in mecgroup.episodes:
        pass
    return root

# def _audio() -> ET.Element:
#     pass

# def _video() -> ET.Element:
#     pass

# def _subtitle() -> ET.Element:
#     pass

# def _metadata() -> ET.Element:
#     pass