import os
import sys
import time
import tkinter
from tkinter import filedialog
from pathlib import Path

from libs import media

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
    input("MECs generated. Press enter to generate MMC once checksums are ready...")
    deliv.output_mmc()

if __name__ == "__main__":
    main()