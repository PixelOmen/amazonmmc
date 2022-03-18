from re import M
from typing import cast
from xml.etree import ElementTree as ET

from . import dataio

XMLNSPACES = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "md": "http://www.movielabs.com/schema/md/v2.9/md",
    "mdmec": "http://www.movielabs.com/schema/mdmec/v2.9",
}

NS = {key:"{"+value+"}" for key,value in XMLNSPACES.items()}

def newroot() -> ET.Element:
    for ns in XMLNSPACES:
        ET.register_namespace(ns, XMLNSPACES[ns])
    root = ET.Element(NS["mdmec"]+"CoreMetadata")
    root.set(NS["xsi"]+"schemaLocation", "http://www.movielabs.com/schema/mdmec/v2.9 mdmec-v2.9.xsd")
    return root

def create(data: dataio.MECData) -> ET.Element:
    root = newroot()
    basic_elem = ET.SubElement(root, NS["mdmec"]+"Basic")
    basic_elem.set("ContentID", f"md:cid:org:{data.orgid.upper()}:{data.id}")
    localinfo_elements = []
    for region in data.localizedinfo:
        localinfo_elem = ET.SubElement(basic_elem, NS["md"]+"LocalizedInfo")
        localinfo_elem.set("language", region["language"])
        ET.SubElement(localinfo_elem, NS["md"]+"TitleDisplayUnlimited").text = region["titledisplay"]
        ET.SubElement(localinfo_elem, NS["md"]+"TitleSort")
        ET.SubElement(localinfo_elem, NS["md"]+"Summary190")
        ET.SubElement(localinfo_elem, NS["md"]+"Summary400").text = region["summary"]
        localinfo_elements.append(localinfo_elem)

    for g in data.genres:
        if g == "":
            continue
        genre_elem = ET.SubElement(localinfo_elements[0], NS["md"]+"Genre")
        genre_elem.set("id", g)

    ET.SubElement(basic_elem, NS["md"]+"ReleaseYear").text = data.releaseyear
    if data.type == "episode":
        epdata = cast(dataio.EpisodeData, data)
        ET.SubElement(basic_elem, NS["md"]+"ReleaseDate").text = epdata.releasedate
        for history in epdata.releasehistory:
            history_elem = ET.SubElement(basic_elem, NS["md"]+"ReleaseHistory")
            ET.SubElement(history_elem, NS["md"]+"ReleaseType").text = history["type"]
            territory_elem = ET.SubElement(history_elem, NS["md"]+"DistrTerritory")
            ET.SubElement(territory_elem, NS["md"]+"country").text = history["territory"]
            ET.SubElement(history_elem, NS["md"]+"Date").text = history["date"]

    ET.SubElement(basic_elem, NS["md"]+"WorkType").text = data.type.lower()
    for alt in data.altids:
        alt_elem = ET.SubElement(basic_elem, NS["md"]+"AltIdentifier")
        ET.SubElement(alt_elem, NS["md"]+"Namespace").text = alt["namespace"]
        ET.SubElement(alt_elem, NS["md"]+"Identifier").text = alt["identifier"]

    ratset_elem = ET.SubElement(basic_elem, NS["md"]+"RatingSet")
    for rat in data.ratings:
        subrat_elem = ET.SubElement(ratset_elem, NS["md"]+"Rating")
        region_elem = ET.SubElement(subrat_elem, NS["md"]+"Region")
        ET.SubElement(region_elem, NS["md"]+"country").text = rat["country"]
        ET.SubElement(subrat_elem, NS["md"]+"System").text = rat["system"]
        ET.SubElement(subrat_elem, NS["md"]+"Value").text = rat["value"]

    if data.type != "series":
        peopledata = cast(dataio.FeatureData, data)
        for person in peopledata.people:
            people_elem = ET.SubElement(basic_elem, NS["md"]+"People")
            job_elem = ET.SubElement(people_elem, NS["md"]+"Job")
            ET.SubElement(job_elem, NS["md"]+"JobFunction").text = person["job"]
            ET.SubElement(job_elem, NS["md"]+"BillingBlockOrder").text = person["billingorder"]
            name_elem = ET.SubElement(people_elem, NS["md"]+"Name")
            for regionnames in person["names"]:
                if regionnames == "":
                    continue
                splitname = regionnames.split(",")
                region = splitname[0]
                name = splitname[1]
                displayname_elem = ET.SubElement(name_elem, NS["md"]+"DisplayName")
                displayname_elem.set("language", region)
                displayname_elem.text = name

    
    ET.SubElement(basic_elem, NS["md"]+"OriginalLanguage").text = data.origlanguage
    assorg_elem = ET.SubElement(basic_elem, NS["md"]+"AssociatedOrg")
    assorg_elem.set("organizationID", data.orgid)
    assorg_elem.set("role", "licensor")

    if data.type == "episode" or data.type == "season":
        seqdata = cast(dataio.EpisodeData, data) if data.type == "episode" else cast(dataio.SeasonData, data)
        relationship = "isepisodeof" if data.type == "episode" else "isseasonof"
        seq_elem = ET.SubElement(basic_elem, NS["md"]+"SequenceInfo")
        ET.SubElement(seq_elem, NS["md"]+"Number").text = seqdata.sequence
        parent_elem = ET.SubElement(basic_elem, NS["md"]+"Parent")
        parent_elem.set("relationshipType", relationship)
        ET.SubElement(parent_elem, NS["md"]+"ParentContentID").text = seqdata.parentid

    compcredit_elem = ET.SubElement(root, NS["mdmec"]+"CompanyDisplayCredit")
    for comp in data.companycredits:
        display_elem = ET.SubElement(compcredit_elem, NS["md"]+"DisplayString")
        display_elem.set("language", comp["language"])
        display_elem.text = comp["credit"]

    return root