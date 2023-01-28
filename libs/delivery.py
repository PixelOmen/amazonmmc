import json
from pathlib import Path
from typing import TYPE_CHECKING, Any

from .mec import MEC
from .mmc import MMC
from .enums import WorkTypes
from xml.etree import ElementTree as ET

class Delivery:
    def __init__(self, rootpath: str|Path) -> None:
        self.rootpath = Path(rootpath)
        self.data: dict = self._scandir()
        self._mecs: list[MEC] = []
        self._mmc: MMC | None = None

    @property
    def mecs(self) -> list[MEC]:
        if not self._mecs:
            raise RuntimeError("MECs must be built before read")
        return self._mecs

    @property
    def mmc(self) -> MMC:
        if self._mmc is None:
            raise RuntimeError("MMC must be built before read")
        return self._mmc

    def build_mecs(self) -> list[MEC]:
        general: dict = self._shouldexist(self.data, "general")
        worktype_str: str = self._shouldexist(general, "worktype")
        worktype = WorkTypes.get_int(worktype_str)
        if worktype != WorkTypes.EPISODIC:
            raise NotImplementedError("Only episodic workflows are currently supported")
        series: dict = self._shouldexist(self.data, "series")
        mec = MEC(series)
        self._mecs = [mec]
        return [mec]

    # def build_mmc(self) -> MMC:
    #     pass

    def write_mecs(self) -> None:
        for m in self.mecs:
            self.output_xml(m.root, "test.xml")

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

    def output_xml(self, root, outputpath, encodingtype="UTF-8", xmldecl=True) -> None:
        self.indent(root)
        tree = ET.ElementTree(root)
        tree.write(outputpath, encoding=encodingtype, xml_declaration=xmldecl)

    def _scandir(self) -> dict:
        datadir = self.rootpath / "data"
        if not datadir.is_dir():
            raise FileNotFoundError("Unable to locate data folder")
        datapath = datadir / "data.json"
        if not datapath.is_file():
            raise FileNotFoundError("Unable to locate data.json")
        resourcepath = self.rootpath / "resources"
        if not resourcepath.is_dir():
            raise FileNotFoundError("Unable to locate resources folder")
        with open(datapath, "r", encoding="UTF-8") as fp:
            data = json.loads(fp.read())
        return data

    def _shouldexist(self, somedict: dict, key: str, context: str=...) -> Any:
        value = somedict.get(key)
        if value is None:
            msg = f"Missing key '{key}'"
            if context is not ...:
                msg += f" in {context}"
            raise LookupError(msg)
        return value