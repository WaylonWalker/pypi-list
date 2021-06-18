"""
pypi-list

Listing python packages from pypi, and finding available single word packages.


## Run the Pipeline

``` bash
# Run with existing package data
python pypi-list.py

# Full run
python pypi-list.py --full
```
"""
import logging

import requests
from kedro.extras.datasets.json import JSONDataSet

import requests

import logging
from kedro.extras.datasets.pickle.pickle_dataset import PickleDataSet
from kedro.io import DataCatalog
from kedro.pipeline import Pipeline, node
from kedro.runner.sequential_runner import SequentialRunner

logger = logging.getLogger(__name__)

__version__ = "0.2.0"


def get_body(packages):

    tag = "<body>\n"
    index = packages.find(tag) + len(tag)
    packages = packages[index:]
    packages = packages[: packages.find(tag)]
    return packages


def remove_html_tags(text):
    """Remove html tags from a string"""
    import re

    clean = re.compile("<.*?>")
    return re.sub(clean, "", text).lower().split()


pipeline = Pipeline(
    nodes=[
        node(
            lambda: requests.get(
                "https://raw.githubusercontent.com/dwyl/english-words/master/words_alpha.txt"
            ).text,
            inputs=None,
            outputs="raw_words_alpha",
            name="raw_words_alpha",
        ),
        node(
            lambda: requests.get("https://pypi.org/simple/").text,
            inputs=None,
            outputs="raw_packages",
            name="raw_packages",
        ),
        node(
            get_body,
            inputs="raw_packages",
            outputs="package_body",
            name="package_body",
        ),
        node(
            remove_html_tags,
            inputs="package_body",
            outputs="packages",
            name="packages",
        ),
        node(
            lambda words: words.split(),
            inputs="raw_words_alpha",
            outputs="words",
            name="words",
        ),
        node(
            lambda words, packages: list(set(words) - set(packages)),
            inputs=["words", "packages"],
            outputs="available",
            name="available",
        ),
        node(
            lambda words, packages: list(set(words) & set(packages)),
            inputs=["words", "packages"],
            outputs="unavailable",
            name="unavailable",
        ),
        node(
            lambda x: x,
            inputs="packages",
            outputs="packages_json",
            name="packages_json",
            tags=["json"],
        ),
        node(
            lambda x: x,
            inputs="available",
            outputs="available_json",
            name="available_json",
            tags=["json"],
        ),
        node(
            lambda x: x,
            inputs="unavailable",
            outputs="unavailable_json",
            name="unavailable_json",
            tags=["json"],
        ),
    ]
)

default_entries = {
    name: PickleDataSet(filepath=f"data/{name}.pkl") for name in pipeline.all_outputs()
}

json_outputs = {
    name: JSONDataSet(filepath=f"data/{name.replace('_json', '')}.json")
    for name in pipeline.only_nodes_with_tags("json").outputs()
}


catalog = DataCatalog(
    {
        **default_entries,
        **json_outputs,
    }
)

runner = SequentialRunner()


def main():
    import sys

    if "--full" in sys.argv:
        runner.run(pipeline, catalog)
    else:
        runner.run(
            Pipeline([node for node in pipeline.nodes if "raw" not in node.name]),
            catalog,
        )


if __name__ == "__main__":
    main()
