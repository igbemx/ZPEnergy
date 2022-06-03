#!/usr/bin/env python3 
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="ZPEnergy",
    version="1.0.0",
    description="Device server for ZPEnergy motor at Softimax",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Igor Beinik",
    author_email="igor.beinik@maxiv.lu.se",
    license="GPLv3",
    url="https://gitlab.maxiv.lu.se/softimax/tangods-softimax-zpenergy",
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['pytango', ],
    entry_points={
        'console_scripts': [
            'SoftiZPEnergy = ZPEnergy.ZPEnergy:main',
        ],
    },
)
