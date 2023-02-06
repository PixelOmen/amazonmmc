import json
from pathlib import Path
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

from .mmc import MMC
from .media import Media
from .enums import WorkTypes
from .mec import MEC, MECEpisodic

if TYPE_CHECKING:
    from .mec import MECGroup

class Delivery:
    def __init__(self, rootpath: str|Path) -> None:
        self.rootdir = Path(rootpath)
        self.resourcedir = self.rootdir / "resources"
        self.data: dict = self._scandir()
        self.worktype = WorkTypes.UNKNOWN
        self._mecgroup: "MECGroup" | None = None
        self._mmc: MMC | None = None

    @property
    def mecs(self) -> "MECGroup":
        if self._mecgroup is None:
            self._mecgroup = self._build_mecs()
        return self._mecgroup

    @property
    def mmc(self) -> MMC:
        if self._mmc is None:
            self._mmc = self._build_mmc()
        return self._mmc

    def write_mecs(self) -> None:
        self.mecs.generate()
        for m in self.mecs.all:
            fullpath = self.resourcedir / m.outputname
            self.write_xml(m.rootelem, fullpath)

    def write_mmc(self) -> None:
        self.mmc.generate()
        fullpath = self.rootdir / self.mmc.outputname
        self.write_xml(self.mmc.rootelem, fullpath)

    def indent(self, elem: ET.Element, level: int=0, spaces: int=4) -> None:
        '''
        Adds newlines and tabs to xml so it's not all on 1 line.
        Pass the root element into 'elem'
        '''
        i = "\n" + level*(" "*spaces)
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + (" "*spaces)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for elem in elem:
                self.indent(elem, level+1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i

    def write_xml(self, root: ET.Element, outputpath, encodingtype="UTF-8", xmldecl=True) -> None:
        self.indent(root)
        tree = ET.ElementTree(root)
        tree.write(outputpath, encoding=encodingtype, xml_declaration=xmldecl)

    def _build_mecs(self) -> "MECGroup":
        general: dict = self._assertexists(self.data, "general")
        worktype_str: str = self._assertexists(general, "worktype")
        worktype = WorkTypes.get_int(worktype_str)
        if worktype == WorkTypes.EPISODIC:
            self.worktype = WorkTypes.EPISODIC
            return self._mec_episodic()
        else:
            raise NotImplementedError("Only episodic workflows are currently supported")

    def _build_mmc(self) -> MMC:
        if self._mecgroup is None:
            self._mecgroup = self._build_mecs()
        if self.worktype == WorkTypes.EPISODIC:
            mmc = MMC(self.worktype, self.rootdir, self._mecgroup)
            return mmc
        else:
            raise NotImplementedError("Only episodic workflows are currently supported")

    def _mec_episodic(self) -> MECEpisodic:
        general_data: dict = self._assertexists(self.data, "general")
        series_data: dict = self._assertexists(self.data, "series")
        general_media = Media(self.resourcedir, general_data)
        series_media = Media(self.resourcedir, series_data, general_media)
        series_mec = MEC(series_media)

        allmec: list[MEC] = [series_mec]
        allseasons_mec: dict[MEC, list[MEC]] = {}
        allepisodes_mec: list[MEC] = []

        season_data: list[dict] = self._assertexists(series_data, "seasons")
        for season in season_data:
            season_media = Media(self.resourcedir, season, series_media)
            season_mec = MEC(season_media)
            allmec.append(season_mec)
            allseasons_mec[season_mec] = []

            episode_data = self._assertexists(season, "episodes")
            for ep in episode_data:
                ep_media = Media(self.resourcedir, ep, season_media)
                ep_mec = MEC(ep_media)
                allmec.append(ep_mec)
                allseasons_mec[season_mec].append(ep_mec)
                allepisodes_mec.append(ep_mec)

        return MECEpisodic(
            worktype=WorkTypes.EPISODIC,
            generalmedia=general_media,
            all=allmec,
            series=series_mec,
            seasons=allseasons_mec,
            episodes=allepisodes_mec
        )

    def _scandir(self) -> dict:
        datadir = self.rootdir / "data"
        if not datadir.is_dir():
            raise FileNotFoundError("Unable to locate data folder")
        datapath = datadir / "data.json"
        if not datapath.is_file():
            raise FileNotFoundError("Unable to locate data.json")
        if not self.resourcedir.is_dir():
            raise FileNotFoundError("Unable to locate resources folder")
        with open(datapath, "rb") as fp:
            data = json.load(fp)
        return data

    def _assertexists(self, somedict: dict, key: str, context: str=...) -> Any:
        value = somedict.get(key)
        if value is None:
            msg = f"Missing key '{key}'"
            if context is not ...:
                msg += f" in {context}"
            raise LookupError(msg)
        return value