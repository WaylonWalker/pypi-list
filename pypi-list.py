from kedro.pipeline import Pipeline, node
from kedro.io import DataCatalog
from kedro.runner.sequential_runner import SequentialRunner

from kedro.extras.datasets.pickle.pickle_dataset import PickleDataSet
from kedro.extras.datasets.json import JSONDataSet

import requests

import logging

logger = logging.getLogger(__name__)


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
            lambda packages: [package for package in packages if len(package) == 4],
            inputs="packages",
            outputs="four_letter_packages",
            name="four_letter_packages",
        ),
        node(
            lambda words: words.split(),
            inputs="raw_words_alpha",
            outputs="words",
            name="words",
        ),
        node(
            lambda words: [word for word in words if len(word) == 4],
            inputs="words",
            outputs="four_letter_words",
            name="four_letter_words",
        ),
        node(
            lambda words, packages: list(set(words) - set(packages)),
            inputs=["words", "packages"],
            outputs="available",
            name="available",
        ),
        node(
            lambda x: x,
            inputs="packages",
            outputs="packages_json",
            name="packages_json",
        ),
        node(
            lambda x: x,
            inputs="available",
            outputs="available_json",
            name="available_json",
        ),
    ]
)

default_entries = {
    name: PickleDataSet(filepath=f"data/{name}.pkl") for name in pipeline.all_outputs()
}
json_outputs = {
    "packages_json": JSONDataSet(filepath=f"data/packages.json"),
    "available_json": JSONDataSet(filepath=f"data/available.json"),
}


catalog = DataCatalog(
    {
        **default_entries,
        **json_outputs,
    }
)

runner = SequentialRunner()

if __name__ == "__main__":
    import sys

    if "--full" in sys.argv:
        runner.run(pipeline, catalog)
    else:
        runner.run(
            Pipeline([node for node in pipeline.nodes if "raw" not in node.name]),
            catalog,
        )
