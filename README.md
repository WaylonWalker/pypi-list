# pypi-list

Live on [pypi-list.waylonwalker.com](https://pypi-list.waylonwalker.com/)

Listing python packages from pypi, and finding available single word packages.

## Install

``` bash
pip install -r requirements.txt
```

## Run the Pipeline

``` bash
# Run with existing package data
python pypi-list.py

# Full run
python pypi-list.py --full
```

## Scheduled on GitHub actions

This pipeline run daily at `0:0` to generate a `packages.json`,
`unavailable.json`, `avalilable.json`.

## Development


``` bash
pip install -e ".[dev]"
```
