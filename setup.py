from setuptools import setup, find_packages
from pathlib import Path

requires = Path("requirements.txt").read_text().split()
dev_requires = Path("requirements_dev.txt").read_text().split()

setup(
    name="pypi_list",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requires,
    extras_require={
        "all": [*requires, *dev_requires],
        "dev": dev_requires,
        "prod": requires,
    },
    entry_points={"console_scripts": ["pypi-list = pypi_list:main"]},
)
