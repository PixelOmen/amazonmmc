from setuptools import setup, find_packages

setup(
    name='amazonmmc',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    package_data={"amazonmmc": ["samples"]},
    entry_points={
        'console_scripts': [
            'amazonmmc = src:main',
        ]
    }
)
