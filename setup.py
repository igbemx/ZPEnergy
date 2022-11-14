#!/usr/bin/env python

from setuptools import setup, find_packages


setup(
    name="tangods-softimax-zpenergy",
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    description="Device server for ZPEnergy motor at Softimax",
    url="https://gitlab.maxiv.lu.se/softimax/tangods-softimax-zpenergy",
    packages=find_packages(exclude=["tests", "*.tests.*", "tests.*", "scripts"]),
    install_requires=['pytango', 'scipy'],
    include_package_data=True,
    entry_points={"console_scripts": ["SoftiZPEnergy = SoftiZPEnergy.SoftiZPEnergy:main", ]},
)
