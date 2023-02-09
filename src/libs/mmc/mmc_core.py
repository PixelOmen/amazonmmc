from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, cast

from .. import errors
from ..mec import MECEpisodic
from ..enums import WorkTypes
from ..xmlhelpers import newroot, newelement, str_to_element

from .alids import ALID
from .presentations import EpPresentation
from .inventory import Audio, Video, Subtitle, Metadata
from .experiences import EpisodeExperience, SeasonExperience, SeriesExperience

if TYPE_CHECKING:
    from ..mec import MEC, MECGroup
    from xml.etree import ElementTree as ET

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
        self.video: Video
        self.audio: list[Audio] = []
        self.subtitles: list[Subtitle] = []
        self.metadata = Metadata(mec, checksums)

class Episode(MMCEntity):
    def __init__(self, mec: "MEC", ext: Extensions, checksums: list[str]) -> None:
        super().__init__(mec, ext, checksums)
        self.seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
        self._parse_resources()
        self._presentation: EpPresentation | None = None
        self._experience: EpisodeExperience | None = None
        self._alid: ALID | None = None

    @property
    def presentation(self) -> EpPresentation:
        if self._presentation is None:
            self._presentation = self._gen_presentation()
        return self._presentation

    @property
    def experience(self) -> EpisodeExperience:
        if self._experience is None:
            self._experience = self._gen_experience()
        return self._experience

    @property
    def alid(self) -> ALID:
        if self._alid is None:
            self._alid = self._gen_alid()
        return self._alid

    def _parse_resources(self) -> None:
        videofound = False
        for res in self.mec.media.resources:
            if res.fullpath.suffix.lower() in self.extensions.av_exts:
                self.audio.append(Audio(self.mec, self.checksums, res))
                if not videofound:
                    self.video = Video(self.mec, self.checksums, res)
                    videofound = True
            elif res.fullpath.suffix.lower() in self.extensions.sub_exts:
                self.subtitles.append(Subtitle(self.mec, self.checksums, res))
        if not videofound:
            raise FileNotFoundError(f"Unable to locate video file for {self.mec.id}")

    def _gen_presentation(self) -> EpPresentation:
        return EpPresentation(self.mec, self.audio, self.video, self.subtitles)

    def _gen_experience(self) -> EpisodeExperience:
        return EpisodeExperience(self.presentation, self.metadata)

    def _gen_alid(self) -> ALID:
        return ALID(self.experience, self.metadata)

class Season(MMCEntity):
    def __init__(self, mec: "MEC", episodes: list["MEC"], ext: Extensions, checksums: list[str]) -> None:
        super().__init__(mec, ext, checksums)
        self.episodes = [Episode(ep, ext, checksums) for ep in episodes]
        self.seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
        self._experience: SeasonExperience | None = None
        self._alid: ALID | None = None

    @property
    def experience(self) -> SeasonExperience:
        if self._experience is None:
            self._experience = self._gen_experience()
        return self._experience

    @property
    def alid(self) -> ALID:
        if self._alid is None:
            self._alid = self._gen_alid()
        return self._alid

    def _gen_experience(self) -> SeasonExperience:
        return SeasonExperience(self)

    def _gen_alid(self) -> ALID:
        return ALID(self.experience, self.metadata)

class Series(MMCEntity):
    def __init__(self, rootdir: Path, mecgroup: "MECEpisodic") -> None:
        self.rootdir = rootdir
        self.mecgroup = mecgroup
        super().__init__(mecgroup.series, Extensions(mecgroup.series), self._readmd5())
        self.seasons = [Season(s, ep, self.extensions, self.checksums) for s, ep in mecgroup.seasons.items()]
        self._experience: SeriesExperience | None = None

    @property
    def experience(self) -> SeriesExperience:
        if self._experience is None:
            self._experience = self._gen_experience()
        return self._experience

    def inventory(self) -> "ET.Element":
        inventory_root = newelement("manifest", "Inventory")
        for season in self.seasons:
            for ep in season.episodes:
                inventory_root.append(ep.video.generate())
                for audio in ep.audio:
                    inventory_root.append(audio.generate())
                for sub in ep.subtitles:
                    inventory_root.append(sub.generate())
                inventory_root.append(ep.metadata.generate())
            inventory_root.append(season.metadata.generate())
        inventory_root.append(self.metadata.generate())
        return inventory_root

    def presentations(self) -> "ET.Element":
        presentations_root = newelement("manifest", "Presentations")
        for season in self.seasons:
            for ep in season.episodes:
                presentations_root.append(ep.presentation.generate())
        return presentations_root

    def experiences(self) -> "ET.Element":
        exp_root = newelement("manifest", "Experiences")
        for season in self.seasons:
            for ep in season.episodes:
                exp_root.append(ep.experience.generate())
            exp_root.append(season.experience.generate())
        exp_root.append(self.experience.generate())
        return exp_root

    def alids(self) -> "ET.Element":
        alid_root = newelement("manifest", "ALIDExperienceMaps")
        for season in self.seasons:
            for ep in season.episodes:
                alid_root.append(ep.alid.generate())
            alid_root.append(season.alid.generate())
        return alid_root

    def _readmd5(self) -> list[str]:
        checksums = self.rootdir / "data" / "checksums.md5"
        lines = []
        with open(checksums, "r", encoding="UTF-8") as fp:
            for line in fp.readlines():
                lines.append(line.strip())
        return lines

    def _gen_experience(self) -> SeriesExperience:
        return SeriesExperience(self)


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

    def generate(self) -> "ET.Element":
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

    def episodic(self, mecgroup: MECEpisodic) -> "ET.Element":
        self._validate_resources(mecgroup)
        self.worktype = WorkTypes.EPISODIC
        seriesid = mecgroup.series.search_media("id", assertcurrent=True)
        self._outputname = f"{seriesid}_MMC.xml"
        self.rootelem.append(self._compatibility())
        series = Series(self.rootdir, mecgroup)
        self.rootelem.append(series.inventory())
        self.rootelem.append(series.presentations())
        self.rootelem.append(series.experiences())
        self.rootelem.append(series.alids())
        return self.rootelem

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

    def _compatibility(self) -> "ET.Element":
        compat_root = newelement("manifest", "Compatibility")
        specver = str_to_element("manifest", "SpecVersion", "1.5")
        profile = str_to_element("manifest", "Profile", "MMC-1")
        compat_root.append(specver)
        compat_root.append(profile)
        return compat_root