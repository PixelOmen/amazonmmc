from typing import TYPE_CHECKING
from abc import ABC, abstractmethod

from ..xmlhelpers import newelement, str_to_element

if TYPE_CHECKING:
    from xml.etree import ElementTree as ET

    from .inventory import Metadata
    from .mmc_core import Season, Episode
    from .presentations import EpPresentation

class Experience(ABC):
    def __init__(self, metadata: "Metadata") -> None:
        self.metadata = metadata
        self.id = self._exp_id()
        self.rootelem = newelement("manifest", "Experience")
        
    @abstractmethod
    def generate(self) -> "ET.Element":...

    @abstractmethod
    def _exp_id(self) -> str:...

class EpisodeExperience(Experience):
    def __init__(self, presentation: "EpPresentation", metadata: "Metadata") -> None:
        self.presentation = presentation
        super().__init__(metadata)

    def generate(self) -> "ET.Element":
        self.rootelem.set("ExperienceID", self.id)
        self.rootelem.set("version", "1.0")

        self.rootelem.append(str_to_element("manifest", "ContentID", self.metadata.id))

        av_root = newelement("manifest", "Audiovisual")
        av_root.set("ContentID", self._exp_id(is_av=True))
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
    
    def _exp_id(self, is_av: bool=False) -> str:
        # "md:experienceid:org:amazonkids:HELLO_KITTY_INTL_S1_106:episode.6.en"
        org = self.presentation.mec.org
        id = self.presentation.mec.id
        seq = self.presentation.seq
        language = self.presentation
        av = "av." if is_av else ""
        return f"md:experienceid:org:{org}:{id}:{av}episode.{seq}"

class SeasonExperience(Experience):
    def __init__(self, season: "Season") -> None:
        self.season = season
        super().__init__(season.metadata)

    def generate(self) -> "ET.Element":
        self.rootelem.set("ExperienceID", self.id)
        self.rootelem.append(str_to_element("manifest", "ContentID", self.metadata.id))

        for ep in self.season.episodes:
            expchild_root = newelement("manifest", "ExperienceChild")
            expchild_root.append(str_to_element("manifest", "Relationship", "isepisodeof"))

            seq_root = newelement("manifest", "SequenceInfo")
            seq_root.append(str_to_element("md", "Number", ep.seq))
            expchild_root.append(seq_root)

            expchild_root.append(str_to_element("manifest", "ExperienceID", ep.experience.id))
            self.rootelem.append(expchild_root)
            
        return self.rootelem

    def _exp_id(self) -> str:
        # "md:experienceid:org:amazonkids:HELLO_KITTY_INTL_S1_106:season.6.en"
        org = self.season.mec.org
        id = self.season.mec.id
        seq = self.season.seq
        return f"md:experienceid:org:{org}:{id}:season.{seq}"

class SeriesExperience(Experience):
    pass