#!/usr/bin/env python3 

from setuptools import setup, find_packages

setup(
    name="tangods-softimax-zpenergy",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Device server for ZPEnergy motor at Softimax",
    author="Igor Beinik",
    author_email="igor.beinik@maxiv.lu.se",
    license="GPLv3",
    url="https://gitlab.maxiv.lu.se/softimax/tangods-softimax-zpenergy",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=['pytango', 'scipy'],
    entry_points={
        'console_scripts': [
            'SoftiZPEnergy = ZPEnergy.ZPEnergy:main',
        ],
    },
)
