def manifest(csvdict, index=0):
    prefix = "md:manifestid:eidr-x:"
    return prefix + csvdict["eidr"][index]

def audiotrack(csvdict, index=0):
    pass

def extraversionref(csvdict, index=0):
    title = csvdict["series_title"][index]
    seasonnum = csvdict["season_number"][index]
    eptitle = csvdict["episode_title"][index]
    return title+": "+"Season "+seasonnum+": "+eptitle


idgenswitch = {
    "manifest": manifest,
    "audiotrack": audiotrack,
    "extraversionref": extraversionref,
}