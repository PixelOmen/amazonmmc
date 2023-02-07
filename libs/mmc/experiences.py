from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from ..xmlhelpers import newelement, str_to_element

if TYPE_CHECKING:
    from xml.etree import ElementTree as ET

    from .inventory import Metadata
    from .presentations import EpPresentation

class Experience(ABC):
    @abstractmethod
    def generate(self) -> "ET.Element":...

class EpisodeExperience(Experience):
    def __init__(self, presentation: "EpPresentation", metadata: "Metadata") -> None:
        self.presentation = presentation
        self.metadata = metadata
        self.id = self._exp_id()
        self.rootelem = newelement("manifest", "Experience")

    def generate(self) -> "ET.Element":
        self.rootelem.set("ExperienceID", self.id)
        self.rootelem.set("version", "1.0")

        self.rootelem.append(str_to_element("manifest", "ContentID", self.metadata.id))

        av_root = newelement("manifest", "Audiovisual")
        av_root.set("ContentID", self._av_id())
        av_root.append(str_to_element("manifest", "Type", "Main"))
        av_root.append(str_to_element("manifest", "SubType", "Episode"))
        av_root.append(str_to_element("manifest", "PresentationID", self.presentation.id))
        self.rootelem.append(av_root)

        expchild_root = newelement("manifest", "ExperienceChild")
        expchild_root.append(str_to_element("manifest", "Relationship", "isepisodeof"))
        seq_root = newelement("manifest", "SequenceInfo")
        seq_root.append(str_to_element("md", "Number", self.presentation.seq))
        expchild_root.append(seq_root)
        expchild_root.append(str_to_element("manifest", "ExperienceID", self.id))
        self.rootelem.append(expchild_root)
        return self.rootelem
    
    def _exp_id(self) -> str:
        # "md:experienceid:org:amazonkids:HELLO_KITTY_INTL_S1_106:episode.6.en"
        org = self.presentation.mec.org
        id = self.presentation.mec.id
        seq = self.presentation.seq
        language = self.presentation.language
        return f"md:experienceid:org:{org}:{id}:episode.{seq}.{language}"

    def _av_id(self) -> str:
        # md:cid:org:amazonkids:HELLO_KITTY_INTL_S1_106:av.episode.6
        org = self.presentation.mec.org
        id = self.presentation.mec.id
        seq = self.presentation.seq
        return f"md:cid:org:{org}:{id}:av.episode.{seq}"

class SeasonExperience(Experience):
    pass

class SeriesExperience(Experience):
    pass