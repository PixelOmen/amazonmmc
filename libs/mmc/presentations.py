from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from ..xmlhelpers import newelement, str_to_element

if TYPE_CHECKING:
    from ..mec import MEC
    from xml.etree import ElementTree as ET
    from .inventory import Audio, Video, Subtitle

class Presentation(ABC):
    def __init__(self, mec: "MEC", audio: list["Audio"], video: "Video", subtitles: list["Subtitle"]) -> None:
        self.mec = mec
        self.audio = audio
        self.video = video
        self.subtitles = subtitles
        self.rootelem = newelement("manifest", "Presentation")

    def _id(self, idtype: str, seq: str=...) -> str:
        mecid = self.mec.id
        trackid = f"md:presentationid:org:{self.mec.org}:{mecid}:{idtype}"
        if seq is not ...:
            trackid += f".{seq}"
        return trackid

    @abstractmethod
    def generate(self) -> "ET.Element":...

class EpPresentation(Presentation):
    def __init__(self, mec: "MEC", audio: list["Audio"], video: "Video", subtitles: list["Subtitle"]) -> None:
        super().__init__(mec, audio, video, subtitles)
        self.seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
        self.id = self._id("episode", self.seq)

    def generate(self) -> "ET.Element":
        self.rootelem.set("PresentationID", self.id)
        trackmeta_root = newelement("manifest", "TrackMetadata")
        trackmeta_root.append(str_to_element("manifest", "TrackSelectionNumber", "0"))

        videotrack_root = newelement("manifest", "VideoTrackReference")
        videotrack_root.append(str_to_element("manifest", "VideoTrackID", self.video.id))
        trackmeta_root.append(videotrack_root)

        for audio in self.audio:
            audiotrack_root = newelement("manifest", "AudioTrackReference")
            audiotrack_root.append(str_to_element("manifest", "AudioTrackID", audio.id))
            trackmeta_root.append(audiotrack_root)

        for sub in self.subtitles:
            subtrack_root = newelement("manifest", "SubtitleTrackReference")
            subtrack_root.append(str_to_element("manifest", "SubtitleTrackID", sub.id))
            trackmeta_root.append(subtrack_root)

        self.rootelem.append(trackmeta_root)
        return self.rootelem