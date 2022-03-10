def manifest(csvdict, index=0):
    prefix = "md:manifestid:eidr-x:"
    return prefix + csvdict["eidr"][index]

def audiotrack(csvdict, index=0):
    pass

def extraversionref(csvdict, index=0):
    pass


idgenswitch = {
    "manifest": manifest,
    "audiotrack": audiotrack,
    "extraversionref": extraversionref,
}