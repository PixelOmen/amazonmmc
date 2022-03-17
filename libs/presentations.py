from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from .media import ResourceGroup

def presentation(presentations_root: ET.Element, ns: dict[str,str], group: "ResourceGroup") -> str:
    presid = f"md:presentationid:{group.coredata.id}"
    pres_elem = ET.SubElement(presentations_root, ns["manifest"]+"Presentation")
    pres_elem.set("PresentationID", presid)
    track_elem = ET.SubElement(pres_elem, ns["manifest"]+"TrackMetadata")
    ET.SubElement(track_elem, ns["manifest"]+"TrackSelectionNumber").text = "0"
    for res in group.resources:
        trackref = res.type.capitalize()+"TrackReference"
        trackid = res.type.capitalize()+"TrackID"
        trackref_elem = ET.SubElement(track_elem, ns["manifest"]+trackref)
        ET.SubElement(trackref_elem, ns["manifest"]+trackid).text = res.resourceid
    return presid

def create(root: ET.Element, ns: dict[str,str], toplevel: "ResourceGroup") -> None:
    presentations_root = ET.SubElement(root, ns["manifest"]+"Presentations")
    if toplevel.coredata.type == "feature" or toplevel.coredata.type == "episode":
        toplevel.presid = presentation(presentations_root, ns, toplevel)
    else:
        for child in toplevel.children:
            if child.coredata.type == "season":
                for epchild in child.children:
                    epchild.presid = presentation(presentations_root, ns, epchild)
            else:
                child.presid = presentation(presentations_root, ns, child)