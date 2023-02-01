from xml.etree import ElementTree as ET

NS_RESIGESTER = {
    "xsi": "http://www.w3.org/2001/XMLSchema-instance",
    "md": "http://www.movielabs.com/schema/md/v2.9/md",
    "mdmec": "http://www.movielabs.com/schema/mdmec/v2.9",
}

NS = {key:"{"+value+"}" for key,value in NS_RESIGESTER.items()}


def newroot(nskey: str, tag: str) -> ET.Element:
    for ns in NS_RESIGESTER:
        ET.register_namespace(ns, NS_RESIGESTER[ns])
    return newelement(nskey, tag, {NS["xsi"]+"schemaLocation": "http://www.movielabs.com/schema/mdmec/v2.9 mdmec-v2.9.xsd"})

def newelement(nskey: str, tag: str, attr: dict[str, str]=...) -> ET.Element:
    root = ET.Element(NS[nskey]+tag)
    if attr is not ...:
        for k,v in attr.items():
            root.set(k,v)
    return root

def key_to_element(nskey: str, dictkey: str, datadict: dict, assertexists: bool=False, tag: str=...) -> ET.Element:
    if tag is ...:
        ns = NS[nskey]+dictkey
    else:
        ns = NS[nskey]+tag
    root = ET.Element(ns)
    value = datadict.get(dictkey)
    if assertexists and value is None:
        raise KeyError(f"Unable to locate key: {dictkey}")
    if value is not None:
        root.text = value
    return root

def str_to_element(nskey: str, tag: str, text: str) -> ET.Element:
    ns = NS[nskey]+tag
    root = ET.Element(ns)
    root.text = text
    return root