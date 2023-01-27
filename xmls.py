import os
import sys
import time
import tkinter
import logging
from pathlib import Path
from tkinter import filedialog

from libs import media

logging.basicConfig(level=logging.INFO, filename="log.txt",
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

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
    try:
        rootdir = getroot()
        if not rootdir:
            print("No directory selected")
            exit()
        deliv = media.Delivery(Path(rootdir))
        deliv.output_mec()
        input("MECs generated. Press enter to generate MMC once checksums are ready...")
        deliv.output_mmc()
    except Exception as e:
        clear()
        name = type(e).__name__
        print(f"{name}: {e}")
        logging.exception(e)
        exit()

if __name__ == "__main__":
    main()