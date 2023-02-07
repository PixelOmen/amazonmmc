from abc import ABC
from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Any, TYPE_CHECKING, cast

from .. import errors
from ..mec import MECEpisodic
from ..enums import WorkTypes, MediaTypes
from ..xmlhelpers import newroot, newelement, key_to_element, str_to_element

from .inventory import Audio, Metadata, Video, Subtitle

if TYPE_CHECKING:
    from ..mec import MEC, MECGroup

class Extensions:
    def __init__(self, mec: "MEC") -> None:
        self.av_exts = mec.search_media("av_exts")
        self.sub_exts = mec.search_media("sub_exts")
        self.art_exts = mec.search_media("art_exts")

class MMCEntity(ABC):
    def __init__(self, mec: "MEC", ext: Extensions, checksums: list[str]) -> None:
        self.mec = mec
        self.extensions = ext
        self.checksums = checksums

class Episode(MMCEntity):
    def __init__(self, mec: "MEC", ext: Extensions, checksums: list[str]) -> None:
        super().__init__(mec, ext, checksums)
        self.audio: list[Audio] = []
        self.video: list[Video] = []
        self.subtitle: list[Subtitle] = []
        self.metadata = Metadata(mec, checksums)
        self._parse_resources()

    def _parse_resources(self) -> None:
        for res in self.mec.media.resources:
            if res.fullpath.suffix.lower() in self.extensions.av_exts:
                self.audio.append(Audio(self.mec, self.checksums, res))
                self.video.append(Video(self.mec, self.checksums, res))
            elif res.fullpath.suffix.lower() in self.extensions.sub_exts:
                self.subtitle.append(Subtitle(self.mec, self.checksums, res))

class Season(MMCEntity):
    def __init__(self, mec: "MEC", episodes: list["MEC"], ext: Extensions, checksums: list[str]) -> None:
        super().__init__(mec, ext, checksums)
        self.episodes = [Episode(ep, ext, checksums) for ep in episodes]
        self.metadata = Metadata(mec, checksums)

class Series:
    def __init__(self, rootdir: Path, mecgroup: "MECEpisodic") -> None:
        self.rootdir = rootdir
        self.mecgroup = mecgroup
        self.mec = mecgroup.series
        self.extensions = Extensions(self.mec)
        self.checksums = self._readmd5()
        self.metadata = Metadata(self.mec, self.checksums)
        self.seasons = [Season(s, ep, self.extensions, self.checksums) for s, ep in mecgroup.seasons.items()]

    def inventory(self) -> list[ET.Element]:
        inventoryelems: list[ET.Element] = []
        for season in self.seasons:
            for ep in season.episodes:
                for video in ep.video:
                    inventoryelems.append(video.generate())
                for audio in ep.audio:
                    inventoryelems.append(audio.generate())
                for sub in ep.subtitle:
                    inventoryelems.append(sub.generate())
                inventoryelems.append(ep.metadata.generate())
            inventoryelems.append(season.metadata.generate())
        inventoryelems.append(self.metadata.generate())
        return inventoryelems

    def _readmd5(self) -> list[str]:
        checksums = self.rootdir / "data" / "checksums.md5"
        lines = []
        with open(checksums, "r", encoding="UTF-8") as fp:
            for line in fp.readlines():
                lines.append(line.strip())
        return lines


class MMC:
    def __init__(self, worktype: int, rootdir: Path, mecgroup: "MECGroup") -> None:
        self.rootdir = rootdir
        self.resourcedir = rootdir / "resources"
        self.worktype = worktype
        self.mecgroup = mecgroup
        self.rootelem = newroot("manifest", "MediaManifest")
        self._outputname = ""
        self.generated = False

    @property
    def outputname(self) -> str:
        if self.worktype == WorkTypes.UNKNOWN:
            raise RuntimeError("Unable to get MMC outputname, worktype unknown")
        if not self._outputname:
            raise AttributeError("MMC must be generated before output name can be generated")
        return self._outputname

    def generate(self) -> ET.Element:
        if self.generated:
            return self.rootelem
        if self.worktype == WorkTypes.EPISODIC:
            if isinstance(self.mecgroup, MECEpisodic):
                mecgroup = cast(MECEpisodic, self.mecgroup)
            else:
                raise RuntimeError(f"Delivery worktype is episodic but MECGroup is of type: {type(self.mecgroup)}")
            self.episodic(mecgroup)
            self.generated =True
            return self.rootelem
        else:
            raise NotImplementedError("Only episodic workflows are currently supported")

    def episodic(self, mecgroup: MECEpisodic) -> ET.Element:
        mecgroup.generate()
        self._validate_resources(mecgroup)
        self.worktype = WorkTypes.EPISODIC
        seriesid = mecgroup.series.search_media("id", assertcurrent=True)
        self._outputname = f"{seriesid}_MMC.xml"
        self.rootelem.append(self._compatibility())
        inventory_root = newelement("manifest", "Inventory")
        series = Series(self.rootdir, mecgroup)
        for elem in series.inventory():
            inventory_root.append(elem)
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