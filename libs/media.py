from . import errors
from .enums import MediaTypes
from typing import Any, Union

NOT_IMPLEMENTED = [MediaTypes.FEATURE]

class Media:
    def __init__(self, data: dict, parent: Union["Media", None]=None) -> None:
        self.data = data
        self.parent = parent
        self.mediatype = self._mediatype()
        if self.mediatype in NOT_IMPLEMENTED:
            raise NotImplementedError(MediaTypes.get_str(self.mediatype))

    def find(self, key: str, assertexists: bool=False) -> Any:
        value = self.data.get(key)
        if value is None:
            if assertexists:
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