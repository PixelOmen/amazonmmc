import argparse
from pathlib import Path
from dataclasses import dataclass


@dataclass
class MMCArgs:
    rootdir: Path
    mecs: bool
    mmc: bool
    sample: bool

def parse_args() -> MMCArgs:
    parser = argparse.ArgumentParser(description=
        """
        AmazonMMC is a tool for creating Amazon MEC, MMC, and running checksums
        """
    )
    parser.add_argument("-r", "--rootdir", required=True, type=lambda x: Path(x), help="""
        (Required) Specify the root path of the Amazon delivery.    
    """)
    parser.add_argument("-version", "--version", action="version", version="0.0.1")

    args = parser.parse_args()
    return MMCArgs(
        rootdir=args.rootdir,
        mecs=True,
        mmc=True,
        sample=True
    )