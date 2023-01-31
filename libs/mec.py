from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

from libs.enums import MediaTypes

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

    def _simple_element_dict(self, nsprefix: str, key: str, datadict: dict, assertexists: bool=False, otherns: str=...) -> ET.Element:
        if otherns is ...:
            ns = NS[nsprefix]+key
        else:
            ns = NS[nsprefix]+otherns
        root = ET.Element(ns)
        if assertexists:
            value = self._get_value(key, datadict)
        else:
            value = datadict.get(key)
        if value is not None:
            root.text = value
        return root

    def _simple_element_str(self, nskey: str, nsname: str, text: str) -> ET.Element:
        ns = NS[nskey]+nsname
        root = ET.Element(ns)
        root.text = text
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
        for info in localizedinfo:
            basicroot.append(info)

        releaseinfo = self._releaseinfo()
        for info in releaseinfo:
            basicroot.append(info)

        worktype = self._search_media("mediatype", assertcurrent=True)
        worktype_root = self._simple_element_str("md", "WorkType", worktype)
        basicroot.append(worktype_root)

        altids = self._altids()
        for altid in altids:
            basicroot.append(altid)

        basicroot.append(self._ratingset())

        people = self._people()
        for person in people:
            basicroot.append(person)

        countryorigin_root = ET.Element(NS["md"]+"CountryOfOrigin")
        country: str = self._search_media("CountryOfOrigin")
        countryorigin_root.append(self._simple_element_str("md", "country", country))
        basicroot.append(countryorigin_root)

        og_lang = self._search_media("OriginalLanguage")
        og_lang_root = self._simple_element_str("md", "OriginalLanguage", og_lang)
        basicroot.append(og_lang_root)

        associatedorg = self._search_media("AssociatedOrg")
        associatedorg_root = ET.Element(NS["md"]+"AssociatedOrg")
        associatedorg_root.set("organizationID", self._get_value("organizationID", associatedorg))
        associatedorg_root.set("role", self._get_value("role", associatedorg))
        basicroot.append(associatedorg_root)

        mediatype: str = self._search_media("mediatype")
        mediatype_enum = MediaTypes.get_int(mediatype)
        if (mediatype_enum == MediaTypes.SEASON or
            mediatype_enum == MediaTypes.EPISODE):
            for elem in self._seqinfo():
                basicroot.append(elem)

        return basicroot

    def _localized(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        allinfo: list[dict] = self._search_media("LocalizedInfo")
        for group in allinfo:
            locroot = ET.Element(NS["md"]+"LocalizedInfo")
            locroot.set("language", self._get_value("language", group))
            locroot.append(self._simple_element_dict("md", "TitleDisplayUnlimited", group, True))
            locroot.append(self._simple_element_dict("md", "TitleSort", group))
            for artref in self._get_value("ArtReference", group):
                art = ET.Element(NS["md"]+"ArtReference")
                art.set("resolution", self._get_value("resolution", artref))
                art.set("purpose", self._get_value("purpose", artref))
                art.text = self._get_value("filename", artref)
                locroot.append(art)
            locroot.append(self._simple_element_dict("md", "Summary190", group))
            locroot.append(self._simple_element_dict("md", "Summary400", group))
            for genre in self._get_value("Genres", group):
                genreroot = ET.Element(NS["md"]+"Genre")
                genreroot.set("id", genre)
                locroot.append(genreroot)
            locroot.append(self._simple_element_dict("md", "CopyrightLine", group))       
            allelem.append(locroot)
        return allelem

    def _releaseinfo(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        relyear: str = self._search_media("ReleaseYear")
        relyear_root = ET.Element(NS["md"]+"ReleaseYear")
        relyear_root.text = relyear
        allelem.append(relyear_root)

        reldate: str = self._search_media("ReleaseDate")
        reldate_root = ET.Element(NS["md"]+"ReleaseDate")
        reldate_root.text = reldate
        allelem.append(reldate_root)

        history: list[dict] = self._search_media("ReleaseHistory")
        for hist in history:
            history_root = ET.Element(NS["md"]+"ReleaseHistory")
            reltype = self._simple_element_dict("md", "ReleaseType", hist)
            history_root.append(reltype)
            territory_root = ET.Element(NS["md"]+"DistrTerritory")
            country = self._simple_element_dict("md", "country", hist)
            territory_root.append(country)
            history_root.append(territory_root)
            date = self._simple_element_dict("md", "Date", hist)
            history_root.append(date)
            allelem.append(history_root)
        return allelem

    def _altids(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        altids = self._search_media("AltIdentifier")
        for altid in altids:
            root = ET.Element(NS["md"]+"AltIdentifier")
            root.append(self._simple_element_dict("md", "Namespace", altid))
            root.append(self._simple_element_dict("md", "Identifier", altid))
            allelem.append(root)
        return allelem

    def _ratingset(self) -> ET.Element:
        ratings: list[dict] = self._search_media("RatingSet")
        ratingset_root = ET.Element(NS["md"]+"RatingSet")
        for rating in ratings:
            rating_root = ET.Element(NS["md"]+"Rating")
            region_root = ET.Element(NS["md"]+"Region")
            country_root = self._simple_element_dict("md", "country", rating)
            region_root.append(country_root)
            rating_root.append(region_root)
            rating_root.append(self._simple_element_dict("md", "System", rating))
            rating_root.append(self._simple_element_dict("md", "Value", rating))
            reason = rating.get("Reason")
            if reason:
                rating_root.append(self._simple_element_dict("md", "Reason", rating))
            ratingset_root.append(rating_root)
        return ratingset_root

    def _people(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        people_groups: list[list[dict]] = self._search_media("People")
        for group in people_groups:
            for person in group:
                person_root = ET.Element(NS["md"]+"People")
                job_root = ET.Element(NS["md"]+"Job")
                job_root.append(self._simple_element_dict("md", "JobFunction", person))
                job_root.append(self._simple_element_dict("md", "BillingBlockOrder", person))
                person_root.append(job_root)
                name_root = ET.Element(NS["md"]+"Name")
                person_root.append(name_root)
                character = person.get("Character")
                if character:
                    job_root.append(self._simple_element_dict("md", "Character", person))
                for name in self._get_value("names", person):
                    displayname = self._simple_element_dict("md", "DisplayName", name)
                    displayname.set("language", self._get_value("language", name))
                    displayname.text = self._get_value("name", name)
                    name_root.append(displayname)
                allelem.append(person_root)
        return allelem

    def _seqinfo(self) -> list[ET.Element]:
        seq_num = self._search_media("SequenceInfo", assertcurrent=True)
        seq_root = ET.Element(NS["md"]+"SequenceInfo")
        seq_root.append(self._simple_element_str("md", "Number", seq_num))

        mediatype = self._search_media("mediatype", assertcurrent=True)
        mediatype_enum = MediaTypes.get_int(mediatype)
        if mediatype_enum == MediaTypes.EPISODE:
            relationship = "isepisodeof"
        elif mediatype_enum == MediaTypes.SEASON:
            relationship = "isseasonof"
        else:
            raise RuntimeError(f"MEC._seqinfo called on mediatype '{mediatype}'")
        parent_root = ET.Element(NS["md"]+"Parent")
        parent_root.set("relationshipType", relationship)

        prefix = self._search_media("orgprefix")
        org = self._search_media("AssociatedOrg")
        orgid = self._get_value("organizationID", org)
        currentid = self._search_media("id", assertcurrent=True)
        if self.media.parent is None:
            raise RuntimeError(f"MEC._eqinfo called with no parent media: {currentid}")
        parentid = self.media.parent.find("id", assertcurrent=True)
        fullid = f"{prefix}{orgid}:{parentid}"
        parent_root.append(self._simple_element_str("md", "ParentContentID", fullid))

        return [seq_root, parent_root]
        
