"""
pypi-list uses setup tools for packaging.

To Build pypi-list as a Python package

    $ python setup.py sdist bdist_wheel

Regular install

    $ pip install -e .

To setup local Development

    $ pip install -e ".[dev]"
"""
from pathlib import Path

from setuptools import find_packages, setup

requires = Path("requirements.txt").read_text().split()
dev_requires = Path("requirements_dev.txt").read_text().split()

setup(
    name="pypi_list",
    version="0.2.0",
    packages=find_packages(),
    install_requires=requires,
    extras_require={
        "all": [*requires, *dev_requires],
        "dev": dev_requires,
        "prod": requires,
    },
    entry_points={"console_scripts": ["pypi-list = pypi_list:main"]},
)
