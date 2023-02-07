from abc import ABC
from pathlib import Path
from typing import TYPE_CHECKING, cast

from .. import errors
from ..mec import MECEpisodic
from ..enums import WorkTypes
from ..xmlhelpers import newroot, newelement, str_to_element

from .presentations import EpPresentation
from .inventory import Audio, Video, Subtitle, Metadata
from .experiences import EpisodeExperience, SeasonExperience

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
        self.video: list[Video] = []
        self.audio: list[Audio] = []
        self.subtitle: list[Subtitle] = []
        self.metadata = Metadata(mec, checksums)

class Episode(MMCEntity):
    def __init__(self, mec: "MEC", ext: Extensions, checksums: list[str]) -> None:
        super().__init__(mec, ext, checksums)
        self.seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
        self._parse_resources()
        self._presentations: dict[str, EpPresentation] = {}
        self._experiences: dict[str, EpisodeExperience] = {}

    @property
    def presentations(self) -> dict[str, EpPresentation]:
        if not self._presentations:
            self._presentations = self._gen_presentations()
        return self._presentations

    @property
    def experiences(self) -> dict[str, EpisodeExperience]:
        if not self._experiences:
            self._experiences = self._gen_experiences()
        return self._experiences

    def _parse_resources(self) -> None:
        for res in self.mec.media.resources:
            if res.fullpath.suffix.lower() in self.extensions.av_exts:
                self.audio.append(Audio(self.mec, self.checksums, res))
                self.video.append(Video(self.mec, self.checksums, res))
            elif res.fullpath.suffix.lower() in self.extensions.sub_exts:
                self.subtitle.append(Subtitle(self.mec, self.checksums, res))

    def _gen_presentations(self) -> dict[str, EpPresentation]:
        """
        Can be extended to support custom groupings of video/audio/sub languages.
        For now, it has to have exactly 1 video/audio/sub in 1 language.
        Language is currently being pulled from video language.
        """
        presentations: list[list[str]] | None = self.mec.search_media("presentations", assertcurrent=True, assertexists=False)
        if presentations:
            raise NotImplementedError("Custom presentations not implemented yet")
        if (len(self.video) != 1 or
            len(self.audio) != 1 or
            len(self.subtitle) != 1):
            raise NotImplementedError(f"Currently only supports exactly 1 video/audio/subtitle file")
        pres_perlanguage: dict[str, EpPresentation] = {}
        try:
            sub = self.subtitle[0]
        except KeyError:
            sub = None
        pres = EpPresentation(self.mec, self.audio[0], self.video[0], sub, self.video[0].language)
        pres_perlanguage[self.video[0].language] = pres
        return pres_perlanguage

    def _gen_experiences(self) -> dict[str, EpisodeExperience]:
        exps: dict[str, EpisodeExperience] = {}
        for k,v in self.presentations.items():
            exps[k] = EpisodeExperience(v, self.metadata)
        return exps

class Season(MMCEntity):
    def __init__(self, mec: "MEC", episodes: list["MEC"], ext: Extensions, checksums: list[str]) -> None:
        super().__init__(mec, ext, checksums)
        self.episodes = [Episode(ep, ext, checksums) for ep in episodes]
        self.seq = self.mec.search_media("SequenceInfo", assertcurrent=True)
        self._experiences: list[SeasonExperience] = []

    @property
    def experiences(self) -> list[SeasonExperience]:
        if not self._experiences:
            self._experiences = self._gen_experiences()
        return self._experiences

    def _gen_experiences(self) -> list[SeasonExperience]:
        if len(self.episodes) < 1:
            raise RuntimeError(f"Season '{self.mec.id}' has no Episodes")
        exps: list[SeasonExperience] = []
        for lang in self.episodes[0].presentations.keys():
            exps.append(SeasonExperience(self, lang))
        return exps

class Series(MMCEntity):
    def __init__(self, rootdir: Path, mecgroup: "MECEpisodic") -> None:
        self.rootdir = rootdir
        self.mecgroup = mecgroup
        super().__init__(mecgroup.series, Extensions(mecgroup.series), self._readmd5())
        self.seasons = [Season(s, ep, self.extensions, self.checksums) for s, ep in mecgroup.seasons.items()]

    def inventory(self) -> "ET.Element":
        inventory_root = newelement("manifest", "Inventory")
        for season in self.seasons:
            for ep in season.episodes:
                for video in ep.video:
                    inventory_root.append(video.generate())
                for audio in ep.audio:
                    inventory_root.append(audio.generate())
                for sub in ep.subtitle:
                    inventory_root.append(sub.generate())
                inventory_root.append(ep.metadata.generate())
            inventory_root.append(season.metadata.generate())
        inventory_root.append(self.metadata.generate())
        return inventory_root

    def presentations(self) -> "ET.Element":
        presentations_root = newelement("manifest", "Presentations")
        for season in self.seasons:
            for ep in season.episodes:
                for pres in ep.presentations.values():
                    presentations_root.append(pres.generate())
        return presentations_root

    def experiences(self) -> "ET.Element":
        exp_root = newelement("manifest", "Experiences")
        for season in self.seasons:
            for ep in season.episodes:
                for exp in ep.experiences.values():
                    exp_root.append(exp.generate())
            for exp in season.experiences:
                exp_root.append(exp.generate())
        return exp_root

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