from . import errors
from pathlib import Path
from .enums import MediaTypes
from typing import Any, Union
from dataclasses import dataclass

IMPLEMENTED = [
    MediaTypes.GENERAL,
    MediaTypes.SERIES,
    MediaTypes.SEASON,
    MediaTypes.EPISODE
]

@dataclass
class Resource:
    dir: Path
    filename: str

class Media:
    def __init__(self, resourcedir: str|Path, data: dict, parent: Union["Media", None]=None) -> None:
        self.resourcedir = Path(resourcedir)
        self.data = data
        self.parent = parent
        self.mediatype = self._mediatype()
        if self.mediatype not in IMPLEMENTED:
            raise NotImplementedError(MediaTypes.get_str(self.mediatype))
        self.id = self._id()
        self.resources = self._resources()

    def find(self, key: str, assertcurrent: bool=False) -> Any:
        value = self.data.get(key)
        if value is None:
            if assertcurrent:
                mediatype = MediaTypes.get_str(self.mediatype)
                raise KeyError(f"Unable to locate '{key}' in {mediatype}")
            if self.parent is not None:
                return self.parent.find(key)
        return value

    def _mediatype(self) -> int:
        mediatype = self.data.get("mediatype")
        if mediatype is None:
            msg = "Unable to locate mediatype in Media"
            raise errors.JSONParsingError(msg)
        return MediaTypes.get_int(mediatype)

    def _id(self) -> str:
        if self.mediatype == MediaTypes.GENERAL:
            return "GENERAL"
        else:
            return self.find("id", assertcurrent=True)

    def _resources(self) -> list[Resource]:
        if self.mediatype != MediaTypes.EPISODE:
            return []

        ep_seq = self.find("SequenceInfo", assertcurrent=True)
        if self.parent is None:
            raise RuntimeError(f"Unable to locate parent Media in episode {ep_seq}")
        if len(ep_seq) < 2:
            ep_seq = "0" + ep_seq
        season_num = self.parent.find("SequenceInfo", assertcurrent=True)
        ep_num = f"{season_num}{ep_seq}"       

        allfiles = []
        for item in self.resourcedir.iterdir():
            if item.is_file() and item.suffix.lower() != ".xml":
                if f"_{ep_num}_" in item.name:
                    allfiles.append(item)
        return allfiles