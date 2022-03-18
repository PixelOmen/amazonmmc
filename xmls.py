import os
import sys
import time
import tkinter
from tkinter import filedialog
from pathlib import Path

from libs import media

currentdir = Path(__file__).parent
test_mmc_output = currentdir / "testfiles" / "test_mmc_output.xml"
test_mec_output = currentdir / "testfiles" / "test_mec_output.xml"

ep_test_dir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M\resources")
ftr_test_dir = Path(r"\\10.0.20.175\rex07\Packaging\_Packaging\AMZN_WP\6E13-51FE-EB00-6BC6-153L-M_feature\resources")

def clear() -> None:
    if sys.platform == "darwin":
        os.system("clear")

def getroot() -> str:
    clear()
    root = tkinter.Tk()
    root.withdraw()
    rootdir = filedialog.askdirectory()
    clear()
    time.sleep(1)
    root.update()
    if not rootdir:
        return ""
    return rootdir

def main():
    rootdir = getroot()
    if not rootdir:
        print("No directory selected")
        exit()
    rootdir = Path(rootdir)
    deliv = media.Delivery(rootdir)
    deliv.output_mec()
    input("Press enter to generate MMC once checksums are ready...")
    deliv.output_mmc()

def test():
    deliv = media.Delivery(ep_test_dir.parent)
    deliv.output_mec()
    deliv.output_mmc()

if __name__ == "__main__":
    main()