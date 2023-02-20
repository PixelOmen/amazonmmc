import sys
from concurrent import futures
import subprocess as sub
from pathlib import Path

class MD5:
    def __init__(self, rootdir: Path) -> None:
        self.rootdir = rootdir

    def run(self, verbose: bool=True) -> dict[str, str]:
        if sys.platform != "darwin":
            raise OSError("Checksums currently only supported on MacOS")
        resourcedir = self.rootdir / "resources"
        files: list[Path] = []
        for item in resourcedir.iterdir():
            if not item.is_file() or item.name[0] == ".":
                continue
            files.append(item)
        output: list[tuple[str, str]] = []
        with futures.ThreadPoolExecutor() as executor:
            checksums = [executor.submit(self._runprocess, file, verbose) for file in files]
            for md5 in futures.as_completed(checksums):
                output.append(md5.result())
        hashdict: dict[str, str] = {}
        for path, hash in output:
            hash = hash.split(" ")[0]
            hashdict[path] = hash
        return hashdict

    def _runprocess(self, file: Path, verbose: bool=True) -> tuple[str, str]:
        if verbose:
            print(f"Running checksum: {file.name}...")
        proc = sub.run(f"md5 -r {str(file)}", stdout=sub.PIPE, stderr=sub.PIPE, shell=True)
        stdout = proc.stdout.decode("UTF-8").replace("\r\n", " ")
        stderr = proc.stderr.decode("UTF-8").replace("\r\n", " ")
        if stderr:
            raise RuntimeError(f"{file.name}: {stderr}")
        if verbose:
            print(f"Checksum complete: {file.name}")
        return file.name, stdout