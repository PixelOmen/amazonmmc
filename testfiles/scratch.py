# import os
# from pathlib import Path

# dir = r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M\resources"

# allfiles = [f for f in Path(dir).iterdir() if f.is_file() and f.name[0] != "." and f.suffix != ".mov"]

# for f in allfiles:
#     splitname = f.name.split("_")
#     try:
#         epnum = splitname[2][2]
#     except IndexError:
#         continue
#     newfilename = f.name.replace(f"_MOS1920x1080NA_", f"_MOS_NA_")
#     newpath = f.parent / newfilename
#     os.rename(str(f), str(newpath))


class Someclass:
    def __init__(self, takeinput):
        self.random = takeinput


x = Someclass(10)

match x:
    case Someclass():
        print("still yup")