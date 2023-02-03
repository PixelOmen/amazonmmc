from dataclasses import dataclass
from typing import TYPE_CHECKING, Any
from xml.etree import ElementTree as ET

from .enums import MediaTypes
from .xmlhelpers import newroot, newelement, key_to_element, str_to_element

if TYPE_CHECKING:
    from .media import Media

@dataclass
class MECGroup:
    worktype: int
    all: list["MEC"]

@dataclass
class MECEpisodic(MECGroup):
    series: "MEC"
    seasons: dict["MEC", list["MEC"]]
    episodes: list["MEC"]

class MEC:
    def __init__(self, media: "Media") -> None:
        self.media = media
        self.root = newroot("mdmec", "CoreMetadata")
        self.outputname = f'{self.search_media("id", assertcurrent=True)}_metadata.xml'

    def episodic(self) -> ET.Element:
        self.root.append(self._basic())
        companycredits = self._companycredits()
        for credit in companycredits:
            self.root.append(credit)
        return self.root

    def search_media(self, key: str, assertcurrent: bool=False, assertexists: bool=True) -> Any:
        value = self.media.find(key, assertcurrent)
        if value is None and assertexists:
            raise KeyError(f"Unable to locate '{key}' in {self.media.mediatype}")
        return value

    def _get_value(self, key: str, datadict: dict) -> Any:
        value = datadict.get(key)
        if value is None:
            raise KeyError(f"Unable to locate '{key}' in {self.media.mediatype}")
        return value

    def _basic(self) -> ET.Element:
        basicroot = newelement("mdmec", "Basic")

        localizedinfo = self._localized()
        for info in localizedinfo:
            basicroot.append(info)

        releaseinfo = self._releaseinfo()
        for info in releaseinfo:
            basicroot.append(info)

        worktype = self.search_media("mediatype", assertcurrent=True)
        worktype_root = str_to_element("md", "WorkType", worktype)
        basicroot.append(worktype_root)

        altids = self._altids()
        for altid in altids:
            basicroot.append(altid)

        basicroot.append(self._ratingset())

        people = self._people()
        for person in people:
            basicroot.append(person)

        countryorigin_root = newelement("md", "CountryOfOrigin")
        country: str = self.search_media("CountryOfOrigin")
        countryorigin_root.append(str_to_element("md", "country", country))
        basicroot.append(countryorigin_root)

        og_lang = self.search_media("OriginalLanguage")
        og_lang_root = str_to_element("md", "OriginalLanguage", og_lang)
        basicroot.append(og_lang_root)

        associatedorg = self.search_media("AssociatedOrg")
        associatedorg_root = newelement("md", "AssociatedOrg")
        associatedorg_root.set("organizationID", self._get_value("organizationID", associatedorg))
        associatedorg_root.set("role", self._get_value("role", associatedorg))
        basicroot.append(associatedorg_root)

        mediatype: str = self.search_media("mediatype")
        mediatype_enum = MediaTypes.get_int(mediatype)
        if (mediatype_enum == MediaTypes.SEASON or
            mediatype_enum == MediaTypes.EPISODE):
            for elem in self._seqinfo():
                basicroot.append(elem)

        return basicroot

    def _companycredits(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        companycreds = self.search_media("CompanyDisplayCredit")
        for cred in companycreds:
            lang = self._get_value("language", cred)
            credit = self._get_value("DisplayString", cred)
            root = newelement("mdmec", "CompanyDisplayCredit")
            displaystr_root = str_to_element("mdmec", "DisplayString", credit)
            displaystr_root.set("language", lang)
            root.append(displaystr_root)
            allelem.append(root)
        return allelem

    def _localized(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        allinfo: list[dict] = self.search_media("LocalizedInfo")
        for group in allinfo:
            locroot = newelement("md", "LocalizedInfo")
            locroot.set("language", self._get_value("language", group))
            locroot.append(key_to_element("md", "TitleDisplayUnlimited", group, True))
            locroot.append(key_to_element("md", "TitleSort", group))
            for artref in self._get_value("ArtReference", group):
                art = newelement("md", "ArtReference")
                art.set("resolution", self._get_value("resolution", artref))
                art.set("purpose", self._get_value("purpose", artref))
                art.text = self._get_value("filename", artref)
                locroot.append(art)
            locroot.append(key_to_element("md", "Summary190", group))
            locroot.append(key_to_element("md", "Summary400", group))
            for genre in self._get_value("Genres", group):
                genreroot = newelement("md", "Genre")
                genreroot.set("id", genre)
                locroot.append(genreroot)
            locroot.append(key_to_element("md", "CopyrightLine", group))       
            allelem.append(locroot)
        return allelem

    def _releaseinfo(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        relyear: str = self.search_media("ReleaseYear")
        relyear_root = newelement("md", "ReleaseYear")
        relyear_root.text = relyear
        allelem.append(relyear_root)

        reldate: str = self.search_media("ReleaseDate")
        reldate_root = newelement("md", "ReleaseDate")
        reldate_root.text = reldate
        allelem.append(reldate_root)

        history: list[dict] = self.search_media("ReleaseHistory")
        for hist in history:
            history_root = newelement("md", "ReleaseHistory")
            reltype = key_to_element("md", "ReleaseType", hist)
            history_root.append(reltype)
            territory_root = newelement("md", "DistrTerritory")
            country = key_to_element("md", "country", hist)
            territory_root.append(country)
            history_root.append(territory_root)
            date = key_to_element("md", "Date", hist)
            history_root.append(date)
            allelem.append(history_root)
        return allelem

    def _altids(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        altids = self.search_media("AltIdentifier")
        for altid in altids:
            root = newelement("md", "AltIdentifier")
            root.append(key_to_element("md", "Namespace", altid))
            root.append(key_to_element("md", "Identifier", altid))
            allelem.append(root)
        return allelem

    def _ratingset(self) -> ET.Element:
        ratings: list[dict] = self.search_media("RatingSet")
        ratingset_root = newelement("md", "RatingSet")
        for rating in ratings:
            rating_root = newelement("md", "Rating")
            region_root = newelement("md", "Region")
            country_root = key_to_element("md", "country", rating)
            region_root.append(country_root)
            rating_root.append(region_root)
            rating_root.append(key_to_element("md", "System", rating))
            rating_root.append(key_to_element("md", "Value", rating))
            reason = rating.get("Reason")
            if reason:
                rating_root.append(key_to_element("md", "Reason", rating))
            ratingset_root.append(rating_root)
        return ratingset_root

    def _people(self) -> list[ET.Element]:
        allelem: list[ET.Element] = []
        people_groups: list[list[dict]] = self.search_media("People")
        for group in people_groups:
            for person in group:
                person_root = newelement("md", "People")
                job_root = newelement("md", "Job")
                job_root.append(key_to_element("md", "JobFunction", person))
                job_root.append(key_to_element("md", "BillingBlockOrder", person))
                person_root.append(job_root)
                name_root = newelement("md", "Name")
                person_root.append(name_root)
                character = person.get("Character")
                if character:
                    job_root.append(key_to_element("md", "Character", person))
                for name in self._get_value("names", person):
                    displayname = key_to_element("md", "DisplayName", name)
                    displayname.set("language", self._get_value("language", name))
                    displayname.text = self._get_value("name", name)
                    name_root.append(displayname)
                allelem.append(person_root)
        return allelem

    def _seqinfo(self) -> list[ET.Element]:
        seq_num = self.search_media("SequenceInfo", assertcurrent=True)
        seq_root = newelement("md", "SequenceInfo")
        seq_root.append(str_to_element("md", "Number", seq_num))

        mediatype = self.search_media("mediatype", assertcurrent=True)
        mediatype_enum = MediaTypes.get_int(mediatype)
        if mediatype_enum == MediaTypes.EPISODE:
            relationship = "isepisodeof"
        elif mediatype_enum == MediaTypes.SEASON:
            relationship = "isseasonof"
        else:
            raise RuntimeError(f"MEC._seqinfo called on mediatype '{mediatype}'")
        parent_root = newelement("md", "Parent")
        parent_root.set("relationshipType", relationship)

        prefix = self.search_media("orgprefix")
        org = self.search_media("AssociatedOrg")
        orgid = self._get_value("organizationID", org)
        currentid = self.search_media("id", assertcurrent=True)
        if self.media.parent is None:
            raise RuntimeError(f"MEC._eqinfo called with no parent media: {currentid}")
        parentid = self.media.parent.find("id", assertcurrent=True)
        fullid = f"{prefix}{orgid}:{parentid}"
        parent_root.append(str_to_element("md", "ParentContentID", fullid))

        return [seq_root, parent_root]