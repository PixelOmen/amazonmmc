from xml.etree import ElementTree as ET

from . import media

def create(root: ET.Element, ns: dict[str,str], delivery: media.Delivery) -> None:
    presentations = ET.SubElement(root, ns["manifest"]+"Presentations")
    for content in delivery.content:
        if content.is_metadata_only():
            continue
        pres_elem = ET.SubElement(presentations, ns["manifest"]+"Presentation")
        pres_elem.set("PresentationID", content.presid)
        track_elem = ET.SubElement(pres_elem, ns["manifest"]+"TrackMetadata")
        ET.SubElement(track_elem, ns["manifest"]+"TrackSelectionNumber").text = "0"
        for key, resourcelist in content.resdict.items():
            if key == "metadata":
                continue
            for resource in resourcelist:
                trackref = resource.type.capitalize()+"TrackReference"
                trackid = resource.type.capitalize()+"TrackID"
                trackref_elem = ET.SubElement(track_elem, ns["manifest"]+trackref)
                ET.SubElement(trackref_elem, ns["manifest"]+trackid).text = resource.id