from abc import ABC
from pathlib import Path
from typing import Any, TYPE_CHECKING
from xml.etree import ElementTree as ET

from .. import errors
from ..enums import WorkTypes, MediaTypes
from ..xmlhelpers import newroot, newelement, key_to_element, str_to_element

from . import inventory
from .inventory import Audio, Video, Subtitle

if TYPE_CHECKING:
    from ..mec import MEC, MECGroup, MECEpisodic

class MMCEntity(ABC):
    def __init__(self, mec: "MEC") -> None:
        self.mec = mec

class Episode(MMCEntity):
    def __init__(self, mec: "MEC") -> None:
        super().__init__(mec)
        self.audio = [Audio(mec, res) for res in self.mec.media.resources]

class Season(MMCEntity):
    def __init__(self, mec: "MEC", episodes: list["MEC"]) -> None:
        super().__init__(mec)
        self.episodes = [Episode(ep) for ep in episodes]

class Series(MMCEntity):
    def __init__(self, mecgroup: "MECEpisodic") -> None:
        super().__init__(mecgroup.series)
        self.mecgroup = mecgroup
        self.seasons = [Season(s, ep) for s, ep in mecgroup.seasons.items()]


class MMC:
    def __init__(self, rootdir: Path) -> None:
        self.rootdir = rootdir
        self.resourcedir = rootdir / "resources"
        self.worktype = WorkTypes.UNKNOWN
        self.root = newroot("manifest", "MediaManifest")
        self._outputname = ""

    @property
    def outputname(self) -> str:
        if self.worktype == WorkTypes.UNKNOWN:
            raise RuntimeError("Unable to get MMC outputname, worktype unknown")
        if not self._outputname:
            raise AttributeError("MMC must be generated before output name can be generated")
        return self._outputname

    def episodic(self, mecgroup: "MECEpisodic") -> ET.Element:
        self._validate_resources(mecgroup)
        self.worktype = WorkTypes.EPISODIC
        seriesid = mecgroup.series.search_media("id", assertcurrent=True)
        self._outputname = f"{seriesid}_MMC.xml"
        self.root.append(self._compatibility())
        self.root.append(inventory.episodic(mecgroup))
        return self.root

    def _get_value(self, key: str, datadict: dict) -> Any:
        value = datadict.get(key)
        if value is None:
            raise KeyError(f"Unable to locate '{key}' in MMC")
        return value

    def _validate_resources(self, mecgroup: "MECGroup") -> None:
        if not mecgroup.all:
            raise RuntimeError("MMC did not recieve any MECs")
        unknowns: list[str] = []
        for item in self.resourcedir.iterdir():
            if not item.is_file() or item.suffix.lower() == ".xml":
                continue
            found = False
            for mec in mecgroup.all:
                for res in mec.media.resources:
                    if res.fullpath.name == item.name:
                        found = True
                        break
                if found:
                    break
            if not found:
                unknowns.append(item.name)
        if unknowns:
            raise errors.ResourceError(unknowns)

    def _compatibility(self) -> ET.Element:
        compat_root = newelement("manifest", "Compatibility")
        specver = str_to_element("manifest", "SpecVersion", "1.5")
        profile = str_to_element("manifest", "Profile", "MMC-1")
        compat_root.append(specver)
        compat_root.append(profile)
        return compat_root