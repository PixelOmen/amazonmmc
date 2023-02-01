import json
from typing import Any
from pathlib import Path
from xml.etree import ElementTree as ET

from .mmc import MMC
from .media import Media
from .enums import WorkTypes
from .mec import MEC, MECGroup, MECEpisodic


class Delivery:
    def __init__(self, rootpath: str|Path) -> None:
        self.rootpath = Path(rootpath)
        self.resourcepath = self.rootpath / "resources"
        self.data: dict = self._scandir()
        self.worktype = WorkTypes.UNKNOWN
        self._mecs: MECGroup | None = None
        self._mmc: MMC | None = None

    @property
    def mecs(self) -> list[MEC]:
        if self._mecs is None:
            self._mecs = self.build_mecs()
        return self._mecs.all

    @property
    def mmc(self) -> MMC:
        if self._mmc is None:
            self._mmc = self.build_mmc()
        return self._mmc

    def build_mecs(self) -> MECGroup:
        general: dict = self._assertexists(self.data, "general")
        worktype_str: str = self._assertexists(general, "worktype")
        worktype = WorkTypes.get_int(worktype_str)
        if worktype != WorkTypes.EPISODIC:
            raise NotImplementedError("Only episodic workflows are currently supported")
        self.worktype = WorkTypes.EPISODIC
        return self._episodic()

    def build_mmc(self) -> MMC:
        if self._mecs is None:
            self._mecs = self.build_mecs()
        mmc = MMC(self._mecs)
        if self.worktype != WorkTypes.EPISODIC:
            raise NotImplementedError("Only episodic workflows are currently supported")
        mmc.episodic()
        return mmc

    def write_mecs(self) -> None:
        for m in self.mecs:
            fulloutput = self.resourcepath / m.outputname
            self.output_xml(m.root, fulloutput)

    # def write_mmc(self) -> None:
    #     pass

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

    def output_xml(self, root: ET.Element, outputpath, encodingtype="UTF-8", xmldecl=True) -> None:
        self.indent(root)
        tree = ET.ElementTree(root)
        tree.write(outputpath, encoding=encodingtype, xml_declaration=xmldecl)

    def _episodic(self) -> MECEpisodic:
        general_data: dict = self._assertexists(self.data, "general")
        general_media = Media(general_data)
        series_data: dict = self._assertexists(self.data, "series")
        series_media = Media(series_data, general_media)
        series_mec = MEC(series_media)
        series_mec.episodic()

        allmec: list[MEC] = [series_mec]
        allseasons_mec: list[MEC] = []
        allepisodes_mec: list[MEC] = []

        season_data: list[dict] = self._assertexists(series_data, "seasons")
        for season in season_data:
            season_media = Media(season, series_media)
            season_mec = MEC(season_media)
            season_mec.episodic()
            allmec.append(season_mec)
            allseasons_mec.append(season_mec)

            episode_data = self._assertexists(season, "episodes")
            for ep in episode_data:
                ep_media = Media(ep, season_media)
                ep_mec = MEC(ep_media)
                ep_mec.episodic()
                allmec.append(ep_mec)
                allepisodes_mec.append(ep_mec)

        return MECEpisodic(allmec, series_mec, allseasons_mec, allepisodes_mec)

    def _scandir(self) -> dict:
        datadir = self.rootpath / "data"
        if not datadir.is_dir():
            raise FileNotFoundError("Unable to locate data folder")
        datapath = datadir / "data.json"
        if not datapath.is_file():
            raise FileNotFoundError("Unable to locate data.json")
        if not self.resourcepath.is_dir():
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