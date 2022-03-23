from typing import TYPE_CHECKING
from xml.etree import ElementTree as ET

if TYPE_CHECKING:
    from .media import ResourceGroup, Resource

ID_PREFIX = {
    "audio": "md:audtrackid",
    "video": "md:vidtrackid",
    "subtitle": "md:subtrackid",
    "metadata": "md:cid"
}

def video(inventory: ET.Element, ns: dict[str,str], resource: "Resource", parentid: str) -> str:
    resourceid = f'{ID_PREFIX["video"]}:{parentid}:video'
    video_elem = ET.SubElement(inventory, ns["manifest"]+"Video")
    video_elem.set("VideoTrackID", resourceid)
    ET.SubElement(video_elem, ns["md"]+"Type").text = "primary"
    encoding = ET.SubElement(video_elem, ns["md"]+"Encoding")
    ET.SubElement(encoding, ns["md"]+"Codec").text = resource.codec
    picture = ET.SubElement(video_elem, ns["md"]+"Picture")
    ET.SubElement(picture, ns["md"]+"AspectRatio").text = resource.aspect
    ET.SubElement(picture, ns["md"]+"WidthPixels").text = resource.resolution[0]
    ET.SubElement(picture, ns["md"]+"HeightPixels").text = resource.resolution[1]
    language = ET.SubElement(video_elem, ns["md"]+"Language")
    language.text = resource.language
    container = ET.SubElement(video_elem, ns["manifest"]+"ContainerReference")
    ET.SubElement(container, ns["manifest"]+"ContainerLocation").text = f"file://resources/{resource.srcpath.name}"
    hash = ET.SubElement(container, ns["manifest"]+"Hash")
    hash.set("method", "MD5")
    hash.text = resource.hash
    return resourceid

def audio(inventory: ET.Element, ns: dict[str,str], resource: "Resource", parentid: str) -> str:
    resourceid = f'{ID_PREFIX["audio"]}:{parentid}:audio_{resource.language.split("-")[0]}'
    audio_elem = ET.SubElement(inventory, ns["manifest"]+"Audio")
    audio_elem.set("AudioTrackID", resourceid)
    ET.SubElement(audio_elem, ns["md"]+"Type").text = "primary"
    encoding = ET.SubElement(audio_elem, ns["md"]+"Encoding")
    ET.SubElement(encoding, ns["md"]+"Codec").text = resource.codec
    language = ET.SubElement(audio_elem, ns["md"]+"Language")
    language.set("dubbed", "true")
    language.text = resource.language
    container = ET.SubElement(audio_elem, ns["manifest"]+"ContainerReference")
    ET.SubElement(container, ns["manifest"]+"ContainerLocation").text = f"file://resources/{resource.srcpath.name}"
    hash = ET.SubElement(container, ns["manifest"]+"Hash")
    hash.set("method", "MD5")
    hash.text = resource.hash
    return resourceid

def subtitle(inventory: ET.Element, ns: dict[str,str], resource: "Resource", parentid: str) -> str:
    resourceid = f'{ID_PREFIX["subtitle"]}:{parentid}:subtitle_{resource.language.split("-")[0]}'
    if "df" in resource.framerate.lower():
        framerate = resource.framerate[:-2]
        dropframe = True
    else:
        framerate = resource.framerate
        dropframe = False
    dropframe = "Drop" if dropframe else "Non-Drop"
    multiplier = "1000/1001" if "9" in resource.framerate else "1/1"
    sub_elem = ET.SubElement(inventory, ns["manifest"]+"Subtitle")
    sub_elem.set("SubtitleTrackID", resourceid)
    ET.SubElement(sub_elem, ns["md"]+"Format").text = "SCC"
    ET.SubElement(sub_elem, ns["md"]+"Type").text = resource.codec
    ET.SubElement(sub_elem, ns["md"]+"Language").text = resource.language
    encoding = ET.SubElement(sub_elem, ns["md"]+"Encoding")
    fps_elem = ET.SubElement(encoding, ns["md"]+"FrameRate")
    fps_elem.set("multiplier", multiplier)
    fps_elem.set("timecode", dropframe)
    fps_elem.text = framerate
    container = ET.SubElement(sub_elem, ns["manifest"]+"ContainerReference")
    ET.SubElement(container, ns["manifest"]+"ContainerLocation").text = f"file://resources/{resource.srcpath.name}"
    hash = ET.SubElement(container, ns["manifest"]+"Hash")
    hash.set("method", "MD5")
    hash.text = resource.hash
    return resourceid

def metadata(inventory: ET.Element, ns: dict[str,str], resource: "Resource", parentid: str) -> str:
    resourceid = f'{ID_PREFIX["metadata"]}:{parentid}:metadata'
    meta_elem = ET.SubElement(inventory, ns["manifest"]+"Metadata")
    meta_elem.set("ContentID", resourceid)
    container = ET.SubElement(meta_elem, ns["manifest"]+"ContainerReference")
    container.set("type", "common")
    ET.SubElement(container, ns["manifest"]+"ContainerLocation").text = f"file://resources/{resource.srcpath.name}"
    hash = ET.SubElement(container, ns["manifest"]+"Hash")
    hash.set("method", "MD5")
    hash.text = resource.hash
    return resourceid

FACTORIES = {
    "audio": audio,
    "video": video,
    "subtitle": subtitle,
    "metadata": metadata
}

def create(root: ET.Element, ns: dict[str,str], toplevel: "ResourceGroup") -> None:
    inventory = ET.SubElement(root, ns["manifest"]+"Inventory")
    if toplevel.coredata.type == "feature" or toplevel.coredata.type == "episode":
        for res in toplevel.resources:
            res.resourceid = FACTORIES[res.type](inventory, ns, res, toplevel.coredata.id)
    else:
        for child in toplevel.children:
            if child.coredata.type == "season":
                for ep in child.children:
                    for epres in ep.resources:
                        epres.resourceid = FACTORIES[epres.type](inventory, ns, epres, ep.coredata.id)
            for res in child.resources:
                res.resourceid = FACTORIES[res.type](inventory, ns, res, child.coredata.id)
                
        for res in toplevel.resources:
            res.resourceid = FACTORIES[res.type](inventory, ns, res, toplevel.coredata.id)