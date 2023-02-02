from pathlib import Path
from typing import cast, Any
from xml.etree import ElementTree as ET

from .. import errors
from ..mec import MECGroup, MECEpisodic
from ..enums import WorkTypes, MediaTypes
from ..xmlhelpers import newroot, newelement, key_to_element, str_to_element

class MMC:
    def __init__(self, mecs: MECGroup, resourcedir: Path) -> None:
        self.mecs = mecs
        self.resourcedir = resourcedir
        self.worktype = WorkTypes.UNKNOWN
        self.root = newroot("manifest", "MediaManifest")
        self._validate_resources()

    @property
    def outputname(self) -> str:
        if self.worktype == WorkTypes.UNKNOWN:
            raise RuntimeError("Unable to get MMC outputname, worktype unknown")
        return self._outputname()

    def episodic(self) -> ET.Element:
        mecs = cast(MECEpisodic, self.mecs)
        self.worktype = WorkTypes.EPISODIC
        self.root.append(self._compatibility())
        return self.root

    def _outputname(self) -> str:
        if self.worktype == WorkTypes.EPISODIC:
            mecs = cast(MECEpisodic, self.mecs)
            seriesid = mecs.series.search_media("id", assertcurrent=True)
            return f"{seriesid}_MMC.xml"
        else:
            raise NotImplementedError(
                "Unable to get MMC outputname, "
                "only episodic workflows are currently supported"
            )

    def _get_value(self, key: str, datadict: dict) -> Any:
        value = datadict.get(key)
        if value is None:
            raise KeyError(f"Unable to locate '{key}' in MMC")
        return value

    def _validate_resources(self) -> None:
        if not self.mecs.all:
            raise RuntimeError("MMC did not recieve any MECs")
        unknowns: list[str] = []
        for item in self.resourcedir.iterdir():
            if not item.is_file() or item.suffix.lower() == ".xml":
                continue
            found = False
            for mec in self.mecs.all:
                for res in mec.media.resources:
                    if res.name == item.name:
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