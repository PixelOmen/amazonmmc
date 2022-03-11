# import os
# from pathlib import Path

# dir = r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M\resources"

# allfiles = [f for f in Path(dir).iterdir() if f.is_file() and f.suffix == ".xml"]

# for f in allfiles:
#     splitname = f.name.split("_")
#     try:
#         epnum = splitname[2][2]
#     except IndexError:
#         continue
#     newfilename = f.name.replace(f"10{epnum}-spyglass-metadata-episode.{epnum}", f"S01E10{epnum}_MOS_16x9_25i_185")
#     newpath = f.parent / newfilename
#     os.rename(str(f), str(newpath))

import re

teststr = "S01fd"

result = re.search(r"S\d\d$", teststr, re.IGNORECASE)

print(result)