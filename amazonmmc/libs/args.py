import argparse
from pathlib import Path
from dataclasses import dataclass


@dataclass
class MMCArgs:
    rootdir: Path
    mec: bool
    mmc: bool
    md5: bool
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
    parser.add_argument("-mec", "--mec", default=False, action="store_true", help="""
        (Optional) Create MEC xmls
    """)
    parser.add_argument("-mmc", "--mmc", default=False, action="store_true", help="""
        (Optional) Create MMC xml
    """)
    parser.add_argument("-md5", "--md5", default=False, action="store_true", help="""
        (Optional) Create MD5 checksums
    """)
    parser.add_argument("-s", "--sample", default=False, action="store_true", help="""
        (Optional) Create completed and starting sample directories
    """)
    parser.add_argument("-version", "--version", action="version", version="0.0.5")

    args = parser.parse_args()
    return MMCArgs(
        rootdir=args.rootdir,
        mec=args.mec,
        mmc=args.mmc,
        md5=args.md5,
        sample=args.sample
    )

if __name__ == "__main__":
    print(parse_args())