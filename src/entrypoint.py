import logging
from pathlib import Path

from .libs.args import parse_args
from .libs.delivery import Delivery


def setlogging(rootdir: Path) -> None:
    logpath = rootdir / "log.txt"
    logging.basicConfig(level=logging.INFO, filename=str(logpath),
        format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
    )

def copy_samples(rootdir: Path) -> None:
    pass

def main():
    try:
        args = parse_args()
        setlogging(args.rootdir)
        deliv = Delivery(args.rootdir)
        if args.sample:
            copy_samples(args.rootdir)
            exit()
        if args.mec:
            deliv.write_mecs()
        if args.md5:
            deliv.checksums()
        if args.mmc:
            deliv.write_mmc()
        logging.info("Job completed successfully")
    except Exception as e:
        name = type(e).__name__
        print(f"{name}: {e}")
        logging.exception(e)
        exit()

if __name__ == "__main__":
    main()