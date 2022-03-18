import os
import sys
import time
import tkinter
import subprocess as sub
from pathlib import Path
from tkinter import filedialog
from tracemalloc import start

def clear() -> None:
    if sys.platform == "darwin":
        os.system("clear")

def getfiles() -> list[Path]:
    clear()
    root = tkinter.Tk()
    root.withdraw()
    rootdir = filedialog.askdirectory()
    clear()
    time.sleep(1)
    root.update()
    if not rootdir:
        return []
    return [f for f in Path(rootdir).iterdir() if f.is_file() and f.name[0] != "."]

def startmd5(filelist: list[Path]) -> list[tuple[str,sub.Popen]]:
    checksum_subs: list[tuple[str,sub.Popen]] = []
    for file in filelist:
        checksum_subs.append((file.name, sub.Popen(f"md5 {str(file)}", stdin=sub.PIPE, stdout=sub.PIPE, stderr=sub.PIPE, shell=True)))
    return checksum_subs

def wait_for_output(processes: list[tuple[str, sub.Popen]], printcomplete: bool=True) -> list[tuple[str,str]]:
    completed = []
    outputs: list[tuple[str,str]] = []
    while True:
        for filename, checksub in processes:
            if checksub.poll() == None or filename in completed:
                continue
            line: bytes = checksub.stdout.read() #type:ignore
            if printcomplete:
                print(f"Checksum complete: {filename}")
            linestr = line.decode("utf-8")
            md5 = linestr.split("=")[1].strip("\n")[1:]
            outputs.append((filename, md5))
            completed.append(filename)
        if len(completed) == len(processes):
            break
        time.sleep(1)
    return outputs

def output_md5(md5info: list[tuple[str, str]], rootdir: Path) -> None:
    outputpath = rootdir.parent / "data" / "checksums.txt"
    with open(str(outputpath), "w") as fp:
        for filename, md5 in md5info:
            fp.write(f"{filename}={md5}\n")

def main():
    allfiles = getfiles()
    if not allfiles:
        print("No files selected")
        exit()
    rootdir = allfiles[0].parent
    print("Running checksums on the following files:")
    for f in allfiles:
        print(f.name)
    print("")
    processes = startmd5(allfiles)
    output = wait_for_output(processes)
    output_md5(output, rootdir)

if __name__ == "__main__":
    main()