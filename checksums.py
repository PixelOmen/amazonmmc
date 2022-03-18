import os
import sys
import tkinter
import subprocess as sub
from pathlib import Path
from tkinter import filedialog

def clear():
    if sys.platform == "darwin":
        os.system("clear")

clear()
root = tkinter.Tk()
root.withdraw()

rootdir = filedialog.askdirectory()
clear()
if not rootdir:
    print("No files selected")
    exit()

allfiles = [f for f in Path(rootdir).iterdir() if f.is_file() and f.name[0] != "."]
checksum_subs: list[tuple[str,sub.Popen]] = []
for file in allfiles:
    checksum_subs.append((file.name, sub.Popen(f"md5 {str(file)}", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)))

outputs: list[tuple[str,str]] = []
for filename, checksub in checksum_subs:
    line: bytes = checksub.stdout.read() #type:ignore
    linestr = line.decode("utf-8")
    md5 = linestr.split("=")[1].strip("\n")[1:]
    outputs.append((filename, md5))

with open("checksum_test.txt", "w") as fp:
    for filename, md5 in outputs:
        fp.write(f"{filename}:{md5}\n")
