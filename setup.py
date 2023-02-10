from pathlib import Path
from setuptools import setup, find_packages

HERE = Path(__file__).parent
SAMPLEDIR = HERE / "amazonmmc" / "samples"
def sample_paths(dir: Path, dirlist: list[str]):
    for item in dir.iterdir():
        if item.is_file():
            dirlist.append(str(item))
        elif item.is_dir():
            sample_paths(item, dirlist)

sample_files = []
sample_paths(SAMPLEDIR, sample_files)

setup(
    name='amazonmmc',
    version='0.0.7',
    packages=find_packages(),
    include_package_data=True,
    package_data={"amazonmmc": sample_files},
    entry_points={
        'console_scripts': [
            'amazonmmc = amazonmmc:main',
        ]
    }
)
