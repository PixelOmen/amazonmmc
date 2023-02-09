import logging
from typing import TYPE_CHECKING

from .libs.args import parse_args
from .libs.delivery import Delivery

if TYPE_CHECKING:
    from libs.args import MMCArgs

logging.basicConfig(level=logging.INFO, filename="log.txt",
    format='%(asctime)s.%(msecs)03d - %(levelname)s - %(message)s', datefmt='%Y-%m-%d %H:%M:%S'
)

def main():
    try:
        args = parse_args()
        deliv = Delivery(args.rootdir)
        deliv.write_mecs()
    except Exception as e:
        name = type(e).__name__
        print(f"{name}: {e}")
        logging.exception(e)
        exit()

if __name__ == "__main__":
    main()