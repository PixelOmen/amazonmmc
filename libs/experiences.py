from typing import TYPE_CHECKING, cast
from xml.etree import ElementTree as ET

from .dataio import SeasonData

if TYPE_CHECKING:
    from .media import ResourceGroup

def exp_single(exp_root: ET.Element, ns: dict[str,str], group: "ResourceGroup") -> str:
    expid = f"md:experienceid:{group.coredata.id}"
    exp_elem = ET.SubElement(exp_root, ns["manifest"]+"Experience")
    exp_elem.set("ExperienceID", expid)
    exp_elem.set("version", "1.0")
    ET.SubElement(exp_elem, ns["manifest"]+"Language").text = group.coredata.origlanguage
    ET.SubElement(exp_elem, ns["manifest"]+"ContentID").text = group.mec.resourceid
    av_elem = ET.SubElement(exp_elem, ns["manifest"]+"AudioVisual")
    av_elem.set("ContentID", group.mec.resourceid)
    ET.SubElement(av_elem, ns["manifest"]+"Type").text = "Main"
    ET.SubElement(av_elem, ns["manifest"]+"PresentationID").text = group.presid
    return expid

def exp_children(exp_root: ET.Element, ns: dict[str,str], group: "ResourceGroup") -> str:
    expid = f"md:experienceid:{group.coredata.id}"
    relationship = "isseasonof" if group.coredata.type == "series" else "isepisodeof"
    top_elem = ET.SubElement(exp_root, ns["manifest"]+"Experience")
    top_elem.set("ExperienceID", expid)
    top_elem.set("version", "1.0")
    ET.SubElement(top_elem, ns["manifest"]+"Language").text = group.coredata.origlanguage
    ET.SubElement(top_elem, ns["manifest"]+"ContentID").text = group.mec.resourceid
    for child in group.children:
        expchild_elem = ET.SubElement(top_elem, ns["manifest"]+"ExperienceChild")
        ET.SubElement(expchild_elem, ns["manifest"]+"Relationship").text = relationship
        seq_elem = ET.SubElement(expchild_elem, ns["manifest"]+"SequenceInfo")
        ET.SubElement(seq_elem, ns["md"]+"Number").text = cast(SeasonData, child.coredata).sequence
        ET.SubElement(expchild_elem, ns["manifest"]+"ExperienceID").text = child.expid
    return expid

def alidexpmaps(maps_root: ET.Element, ns: dict[str,str], group: "ResourceGroup") -> None:
    map_elem = ET.SubElement(maps_root, ns["manifest"]+"ALIDExperienceMap")
    ET.SubElement(map_elem, ns["manifest"]+"ALID").text = f"md:alid:{group.expid[16:]}"
    expid_elem = ET.SubElement(map_elem, ns["manifest"]+"ExperienceID")
    expid_elem.set("condition", "For-sale")
    expid_elem.text = group.expid

def create(root: ET.Element, ns: dict[str,str], toplevel: "ResourceGroup") -> None:
    exp_root = ET.SubElement(root, ns["manifest"]+"Experiences")
    maps_root = ET.SubElement(root, ns["manifest"]+"ALIDExperienceMaps")
    if toplevel.coredata.type == "feature" or toplevel.coredata.type == "episode":
        toplevel.expid = exp_single(exp_root, ns, toplevel)
        alidexpmaps(maps_root, ns, toplevel)
    else:
        if toplevel.coredata.type == "series":
            for season in toplevel.children:
                for ep in season.children:
                    ep.expid = exp_single(exp_root, ns, ep)
                    alidexpmaps(maps_root, ns, ep)
                season.expid = exp_children(exp_root, ns, season)
                alidexpmaps(maps_root, ns, season)
        else:
            for ep in toplevel.children:
                ep.expid = exp_single(exp_root, ns, ep)
                alidexpmaps(maps_root, ns, ep)
        toplevel.expid = exp_children(exp_root, ns, toplevel)
        alidexpmaps(maps_root, ns, toplevel)



