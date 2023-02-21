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
    mediatype: int
    fullpath: Path

class Media:
    def __init__(self, resourcedir: str|Path, data: dict, parent: Union["Media", None]=None) -> None:
        self.resourcedir = Path(resourcedir)
        self.data = data
        self.parent = parent
        self.mediatype = self._mediatype()
        if self.mediatype not in IMPLEMENTED:
            raise NotImplementedError(MediaTypes.get_str(self.mediatype))
        self.id = self._id()
        self.org = self.find("AssociatedOrg")["organizationID"]
        self.resources = self._resources()

    def find(self, key: str, assertcurrent: bool=False, assertexists: bool=True) -> Any:
        value = self.data.get(key)
        if value is None:
            if assertcurrent:
                if not assertexists:
                    return None
                mediatype = MediaTypes.get_str(self.mediatype)
                raise KeyError(f"Unable to locate '{key}' in {mediatype}")
            if self.parent is None:
                if assertexists:
                    mediatype = MediaTypes.get_str(self.mediatype)
                    raise KeyError(f"Unable to locate '{key}' in {mediatype}")
                else:
                    return None
            else:
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
        if self.mediatype == MediaTypes.EPISODE:
            ep_seq = self.find("SequenceInfo", assertcurrent=True)
            if self.parent is None:
                raise RuntimeError(f"Unable to locate parent Media in episode {ep_seq}")
            if len(ep_seq) < 2:
                ep_seq = "0" + ep_seq
            season_num = self.parent.find("SequenceInfo", assertcurrent=True)
            ep_num = f"{season_num}{ep_seq}"
            searchterm = ep_num   
        elif self.mediatype == MediaTypes.SEASON:
            season_seq = self.find("SequenceInfo", assertcurrent=True)
            searchterm = f"SEASON{season_seq}"
        elif self.mediatype == MediaTypes.SERIES:
            searchterm = self.find("title", assertcurrent=True)
        else:
            return []

        allresources: list[Resource] = []
        for item in self.resourcedir.iterdir():
            if not item.is_file() or item.name[0] == ".":
                continue
            if item.is_file() and item.suffix.lower() != ".xml":
                if f"_{searchterm}_" in item.name:
                    allresources.append(Resource(self.mediatype, item))
        return allresources