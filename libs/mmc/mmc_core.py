from abc import ABC
from pathlib import Path
from typing import Any, TYPE_CHECKING
from xml.etree import ElementTree as ET

from .. import errors
from ..enums import WorkTypes, MediaTypes
from ..xmlhelpers import newroot, newelement, key_to_element, str_to_element

from .inventory import Audio, Video, Subtitle

if TYPE_CHECKING:
    from ..mec import MEC, MECGroup, MECEpisodic

class Extensions:
    def __init__(self, mec: "MEC") -> None:
        self.av_exts = mec.search_media("av_exts")
        self.sub_exts = mec.search_media("sub_exts")
        self.art_exts = mec.search_media("art_exts")

class MMCEntity(ABC):
    def __init__(self, mec: "MEC", ext: Extensions) -> None:
        self.mec = mec
        self.extensions = ext

class Episode(MMCEntity):
    def __init__(self, mec: "MEC", ext: Extensions) -> None:
        super().__init__(mec, ext)
        self.audio: list[Audio] = []
        self.video: list[Video] = []
        self._parse_resources()

    def _parse_resources(self) -> None:
        for res in self.mec.media.resources:
            if res.fullpath.suffix.lower() in self.extensions.av_exts:
                self.audio.append(Audio(self.mec, res))
                self.video.append(Video(self.mec, res))

class Season(MMCEntity):
    def __init__(self, mec: "MEC", episodes: list["MEC"], ext: Extensions) -> None:
        super().__init__(mec, ext)
        self.episodes = [Episode(ep, ext) for ep in episodes]

class Series:
    def __init__(self, mecgroup: "MECEpisodic") -> None:
        self.mecgroup = mecgroup
        self.mec = mecgroup.series
        self.extensions = Extensions(self.mec)
        self.seasons = [Season(s, ep, self.extensions) for s, ep in mecgroup.seasons.items()]


class MMC:
    def __init__(self, rootdir: Path) -> None:
        self.rootdir = rootdir
        self.resourcedir = rootdir / "resources"
        self.worktype = WorkTypes.UNKNOWN
        self.rootelem = newroot("manifest", "MediaManifest")
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
        self.rootelem.append(self._compatibility())
        inventory_root = newelement("manifest", "Inventory")
        series = Series(mecgroup)
        for season in series.seasons:
            for ep in season.episodes:
                for audio in ep.audio:
                    inventory_root.append(audio.generate())
        self.rootelem.append(inventory_root)
        return self.rootelem

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