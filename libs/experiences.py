from xml.etree import ElementTree as ET

from . import media

def create(root: ET.Element, ns: dict[str,str], delivery: media.Delivery) -> None:
    exp_root = ET.SubElement(root, ns["manifest"]+"Experiences")
    for c in delivery.content:
        if c.is_metadata_only():
            continue
        exp_elem = ET.SubElement(exp_root, ns["manifest"]+"Experience")
        exp_elem.set("ExperienceID", c.expid)
        exp_elem.set("version", "1.0")
        ET.SubElement(exp_elem, ns["manifest"]+"Language").text = c.resdict["video"][0].language
        ET.SubElement(exp_elem, ns["manifest"]+"ContentID").text = c.resdict["metadata"][0].id
        av_elem = ET.SubElement(exp_elem, ns["manifest"]+"AudioVisual")
        av_elem.set("ContentID", c.resdict["metadata"][0].id)
        ET.SubElement(av_elem, ns["manifest"]+"Type").text = "Main"
        ET.SubElement(av_elem, ns["manifest"]+"PresentationID").text = c.presid

    if delivery.type != "ep":
        return
        
    season_elem = ET.SubElement(exp_root, ns["manifest"]+"Experience")
    season_elem.set("ExperienceID", delivery.seasonmeta.expid)
    season_elem.set("version", "1.0")
    language = ""
    for c in delivery.content:
        if c.is_metadata_only():
            continue
        language = c.resdict["video"][0].language
        break
    if not language:
        raise LookupError("Unable to parse season language")
    ET.SubElement(season_elem, ns["manifest"]+"Language").text = language
    ET.SubElement(season_elem, ns["manifest"]+"ContentID").text = delivery.seasonmeta.resdict["metadata"][0].id
    epnum = 1
    for c in delivery.content:
        if c.is_metadata_only():
            continue
        expchild_elem = ET.SubElement(season_elem, ns["manifest"]+"ExperienceChild")
        ET.SubElement(expchild_elem, ns["manifest"]+"Relationship").text = "isepisodeof"
        seq_elem = ET.SubElement(expchild_elem, ns["manifest"]+"SequenceInfo")
        ET.SubElement(seq_elem, ns["md"]+"Number").text = str(epnum)
        ET.SubElement(expchild_elem, ns["manifest"]+"ExperienceID").text = c.expid
        epnum += 1

    series_elem = ET.SubElement(exp_root, ns["manifest"]+"Experience")
    series_elem.set("ExperienceID", delivery.seriesmeta.expid)
    ET.SubElement(series_elem, ns["manifest"]+"ContentID").text = delivery.seriesmeta.resdict["metadata"][0].id
    expchild_elem = ET.SubElement(series_elem, ns["manifest"]+"ExperienceChild")
    ET.SubElement(expchild_elem, ns["manifest"]+"Relationship").text = "isseasonof"
    seq_elem = ET.SubElement(expchild_elem, ns["manifest"]+"SequenceInfo")
    ET.SubElement(seq_elem, ns["md"]+"Number").text = str(int(delivery.seasonmeta.resdict["metadata"][0].descriptor[1:]))
    ET.SubElement(expchild_elem, ns["manifest"]+"ExperienceID").text = delivery.seasonmeta.resdict["metadata"][0].id


def create_maps(root: ET.Element, ns: dict[str,str], delivery: media.Delivery) -> None:
    pass