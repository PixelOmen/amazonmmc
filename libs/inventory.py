from xml.etree import ElementTree as ET

from . import media

def video(inventory: ET.Element, ns: dict[str,str], resources: list[media.Resource]) -> None:
    for v in resources:
        video_elem = ET.SubElement(inventory, ns["manifest"]+"Video")
        video_elem.set("VideoTrackID", v.id)
        ET.SubElement(video_elem, ns["md"]+"Type").text = "primary"
        encoding = ET.SubElement(video_elem, ns["md"]+"Encoding")
        ET.SubElement(encoding, ns["md"]+"Codec").text = "PRORESHQ"
        picture = ET.SubElement(video_elem, ns["md"]+"Picture")
        ET.SubElement(picture, ns["md"]+"AspectRatio").text = v.aspectratio.replace("x", ":")
        ET.SubElement(picture, ns["md"]+"WidthPixels").text = v.resolution[0]
        ET.SubElement(picture, ns["md"]+"HeightPixels").text = v.resolution[1]
        language = ET.SubElement(video_elem, ns["md"]+"Language")
        language.text = v.language
        container = ET.SubElement(video_elem, ns["manifest"]+"ContainerReference")
        ET.SubElement(container, ns["manifest"]+"ContainerLocation").text = f"file://resources/{v.srcpath.name}"
        hash = ET.SubElement(container, ns["manifest"]+"Hash")
        hash.set("method", "MD5")
        hash.text = "hash"

def audio(inventory: ET.Element, ns: dict[str,str], resources: list[media.Resource]) -> None:
    for a in resources:
        audio_elem = ET.SubElement(inventory, ns["manifest"]+"Audio")
        audio_elem.set("AudioTrackID", a.id)
        ET.SubElement(audio_elem, ns["md"]+"Type").text = "primary"
        encoding = ET.SubElement(audio_elem, ns["md"]+"Encoding")
        ET.SubElement(encoding, ns["md"]+"Codec").text = "PCM"
        language = ET.SubElement(audio_elem, ns["md"]+"Language")
        language.set("dubbed", "true")
        language.text = a.language
        container = ET.SubElement(audio_elem, ns["manifest"]+"ContainerReference")
        ET.SubElement(container, ns["manifest"]+"ContainerLocation").text = f"file://resources/{a.srcpath.name}"
        hash = ET.SubElement(container, ns["manifest"]+"Hash")
        hash.set("method", "MD5")
        hash.text = "hash"

def subtitle(inventory: ET.Element, ns: dict[str,str], resources: list[media.Resource]) -> None:
    for s in resources:
        framerate = s.framerate[:-1]
        multiplier = "1/1" if len(framerate) == 2 else "1000/1001"
        sub_elem = ET.SubElement(inventory, ns["manifest"]+"Subtitle")
        sub_elem.set("SubtitleTrackID", s.id)
        ET.SubElement(sub_elem, ns["md"]+"Format").text = s.srcpath.suffix[1:].upper()
        ET.SubElement(sub_elem, ns["md"]+"Type").text = "SDH"
        ET.SubElement(sub_elem, ns["md"]+"Language").text = s.language
        encoding = ET.SubElement(sub_elem, ns["md"]+"Encoding")
        fps_elem = ET.SubElement(encoding, ns["md"]+"FrameRate")
        fps_elem.set("multiplier", multiplier)
        fps_elem.set("timecode", "Non-Drop")
        fps_elem.text = framerate
        container = ET.SubElement(sub_elem, ns["manifest"]+"ContainerReference")
        ET.SubElement(container, ns["manifest"]+"ContainerLocation").text = f"file://resources/{s.srcpath.name}"
        hash = ET.SubElement(container, ns["manifest"]+"Hash")
        hash.set("method", "MD5")
        hash.text = "hash"

def metadata(inventory: ET.Element, ns: dict[str,str], resources: list[media.Resource]) -> None:
    for m in resources:
        meta_elem = ET.SubElement(inventory, ns["manifest"]+"Metadata")
        meta_elem.set("ContentID", m.id)
        container = ET.SubElement(meta_elem, ns["manifest"]+"ContainerReference")
        container.set("type", "common")
        ET.SubElement(container, ns["manifest"]+"ContainerLocation").text = f"file://resources/{m.srcpath.name}"

FACTORIES = {
    "audio": audio,
    "video": video,
    "subtitle": subtitle,
    "metadata": metadata
}

def create(root: ET.Element, ns: dict[str,str], delivery: media.Delivery) -> None:
    inventory = ET.SubElement(root, ns["manifest"]+"Inventory")
    for content in delivery.content:
        for key,value in content.resdict.items():
            FACTORIES[key](inventory, ns, value)
