from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from .media import Media

NS_RESIGESTER = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "md": "http://www.movielabs.com/schema/md/v2.9/md",
    "mdmec": "http://www.movielabs.com/schema/mdmec/v2.9",
}

NS = {key:"{"+value+"}" for key,value in NS_RESIGESTER.items()}


class MEC:
    def __init__(self, media: "Media") -> None:
        self.media = media
        self.root = self._newroot()
        self.outputname = f'{self._search_media("id", assertcurrent=True)}_metadata.xml'

    def episodic(self) -> ET.Element:
        basic_elem = self._basic()
        self.root.append(basic_elem)
        return self.root

    def _search_media(self, key: str, assertcurrent: bool=False, assertexists: bool=True) -> Any:
        value = self.media.find(key, assertcurrent)
        if value is None and assertexists:
            raise KeyError(f"Unable to locate '{key}' in {self.media.mediatype}")
        return value

    def _get_value(self, key: str, datadict: dict) -> Any:
        value = datadict.get(key)
        if value is None:
            raise KeyError(f"Unable to locate '{key}' in {self.media.mediatype}")
        return value

    def _simple_element(self, ns: str, key: str, datadict: dict, assertexists: bool=False) -> ET.Element:
        root = ET.Element(ns)
        if assertexists:
            value = self._get_value(key, datadict)
        else:
            value = datadict.get(key)
        if value is not None:
            root.text = value
        return root

    def _newroot(self) -> ET.Element:
        for ns in NS_RESIGESTER:
            ET.register_namespace(ns, NS_RESIGESTER[ns])
        root = ET.Element(NS["mdmec"]+"CoreMetadata")
        root.set(NS["xsi"]+"schemaLocation", "http://www.movielabs.com/schema/mdmec/v2.9 mdmec-v2.9.xsd")
        return root

    def _basic(self) -> ET.Element:
        basicroot = ET.Element(NS["mdmec"]+"Basic")
        localizedinfo = self._localized()
        releaseinfo = self._releaseinfo()
        for info in localizedinfo:
            basicroot.append(info)
        for info in releaseinfo:
            basicroot.append(info)
        return basicroot

    def _localized(self) -> list[ET.Element]:
        all: list[ET.Element] = []
        allinfo: list[dict] = self._search_media("LocalizedInfo")
        for group in allinfo:
            locroot = ET.Element(NS["md"]+"LocalizedInfo")
            locroot.set("language", self._get_value("language", group))
            locroot.append(self._simple_element(NS["md"]+"TitleDisplayUnlimited", "TitleDisplayUnlimited", group, True))
            locroot.append(self._simple_element(NS["md"]+"TitleSort", "TitleSort", group))
            for artref in self._get_value("ArtReference", group):
                art = ET.Element(NS["md"]+"ArtReference")
                art.set("resolution", self._get_value("resolution", artref))
                art.set("purpose", self._get_value("purpose", artref))
                art.text = self._get_value("filename", artref)
                locroot.append(art)
            locroot.append(self._simple_element(NS["md"]+"Summary190", "Summary190", group))
            locroot.append(self._simple_element(NS["md"]+"Summary400", "Summary400", group))
            for genre in self._get_value("Genres", group):
                genreroot = ET.Element(NS["md"]+"Genre")
                genreroot.set("id", genre)
                locroot.append(genreroot)
            locroot.append(self._simple_element(NS["md"]+"CopyrightLine", "CopyrightLine", group))       
            all.append(locroot)
        return all

    def _releaseinfo(self) -> list[ET.Element]:
        all: list[ET.Element] = []
        relyear: str = self._search_media("ReleaseYear")
        relyear_root = ET.Element(NS["md"]+"ReleaseYear")
        relyear_root.text = relyear
        all.append(relyear_root)

        reldate: str = self._search_media("ReleaseDate")
        reldate_root = ET.Element(NS["md"]+"ReleaseDate")
        reldate_root.text = reldate
        all.append(reldate_root)

        history: list[dict] = self._search_media("ReleaseHistory")
        for hist in history:
            history_root = ET.Element(NS["md"]+"ReleaseHistory")
            reltype = self._simple_element(NS["md"]+"ReleaseType", "ReleaseType", hist)
            history_root.append(reltype)
            territory_root = ET.Element(NS["md"]+"DistrTerritory")
            country = self._simple_element(NS["md"]+"country", "country", hist)
            territory_root.append(country)
            history_root.append(territory_root)
            date = self._simple_element(NS["md"]+"Date", "Date", hist)
            history_root.append(date)
            all.append(history_root)
        return all