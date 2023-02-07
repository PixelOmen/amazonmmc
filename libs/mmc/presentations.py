from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Union
from xml.etree import ElementTree as ET

from ..xmlhelpers import newelement, str_to_element

if TYPE_CHECKING:
    from ..mec import MEC
    from .inventory import Audio, Video, Subtitle

class Presentation(ABC):
    def __init__(self, mec: "MEC", audio: "Audio", video: "Video", subtitle: Union["Subtitle", None]) -> None:
        self.mec = mec
        self.audio = audio
        self.video = video
        self.subtitle = subtitle
        self.rootelem = newelement("manifest", "Presentation")

    def _id(self, idtype: str, seq: str=...) -> str:
        """
        mmc_core.Episode._gen_presentations needs to be
        extended to allow for other lanuage id selections
        """
        mecid = self.mec.id
        trackid = f"md:presentationid:org:{self.mec.org}:{mecid}:{idtype}"
        if seq is not ...:
            trackid += f".{seq}"
        trackid += f".{self.video.language}" # not ideal
        return trackid

    @abstractmethod
    def generate(self) -> ET.Element:...

class EpPresentation(Presentation):
    def __init__(self, mec: "MEC", audio: "Audio", video: "Video", subtitle: Union["Subtitle", None]) -> None:
        super().__init__(mec, audio, video, subtitle)
        self.seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
        self.id = self._id("episode", self.seq)

    def generate(self) -> ET.Element:
        self.rootelem.set("PresentationID", self.id)
        trackmeta_root = newelement("manifest", "TrackMetadata")
        trackmeta_root.append(str_to_element("manifest", "TrackSelectionNumber", "0"))

        videotrack_root = newelement("manifest", "VideoTrackReference")
        videotrack_root.append(str_to_element("manifest", "VideoTrackID", self.video.id))
        trackmeta_root.append(videotrack_root)

        audiotrack_root = newelement("manifest", "AudioTrackReference")
        audiotrack_root.append(str_to_element("manifest", "AudioTrackID", self.audio.id))
        trackmeta_root.append(audiotrack_root)

        if self.subtitle is not None:
            subtrack_root = newelement("manifest", "SubtitleTrackReference")
            subtrack_root.append(str_to_element("manifest", "SubtitleTrackID", self.subtitle.id))
            trackmeta_root.append(subtrack_root)

        self.rootelem.append(trackmeta_root)
        return self.rootelem