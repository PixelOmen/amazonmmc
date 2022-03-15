from xml.etree import ElementTree as ET
from typing import cast

from . import dataio

XMLNSPACES = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "md": "http://www.movielabs.com/schema/md/v2.6/md",
    "mdmec": "http://www.movielabs.com/schema/mdmec/v2.9",
}

NS = {key:"{"+value+"}" for key,value in XMLNSPACES.items()}

def newroot() -> ET.Element:
    for ns in XMLNSPACES:
        ET.register_namespace(ns, XMLNSPACES[ns])
    root = ET.Element(NS["mdmec"]+"CoreMetadata")
    root.set(NS["xsi"]+"schemaLocation", "http://www.movielabs.com/schema/mdmec/v2.8 mdmec-v2.8.xsd")
    return root

def create(data: dataio.MECData) -> ET.Element:
    root = newroot()
    basic_elem = ET.SubElement(root, NS["mdmec"]+"Basic")
    basic_elem.set("ContentID", f"md:cid:org:{data.orgid.upper()}:{data.id}")
    localinfo_elements = []
    for region in data.localizedinfo:
        localinfo_elem = ET.SubElement(basic_elem, NS["md"]+"LocalizedInfo")
        localinfo_elem.set("languange", region["language"])
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
    
    ET.SubElement(basic_elem, NS["md"]+"OriginalLanguage").text = data.origlanguage
    assorg_elem = ET.SubElement(basic_elem, NS["md"]+"AssociateOrg")
    assorg_elem.set("organizationID", data.orgid)
    assorg_elem.set("role", "licensor")

    compcredit_elem = ET.SubElement(root, NS["mdmec"]+"CompanyDisplayCredit")
    for comp in data.companycredits:
        display_elem = ET.SubElement(compcredit_elem, NS["md"]+"DisplayString")
        display_elem.set("language", comp["language"])
        display_elem.text = comp["credit"]
        
    return root