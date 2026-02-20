"""GAMS catalog

This module provides an XML Catalog for the most important XML Ressource.

When this module is imorted, it will register the XML catalog automatically, so that
lxml will use it.

Use `catalog.catalog_file` to get the path to the catalog file.
"""

from pathlib import Path
import os


def set_debug(activate: bool) -> None:
    "Use this function to activate or deactivate debugging of the catalog."
    os.environ["XML_CATALOG_DEBUG"] = "1" if activate else "0"

def add_catalog_to_env(cat_file: Path|str) -> None:
    """Set the XML Catalog to the environment variable XML_CATALOG_FILES."""
    cat_file = Path(cat_file)
    old_values = set(os.environ.get("XML_CATALOG_FILES", "").split())
    old_values.add(str(cat_file.resolve()))
    os.environ["XML_CATALOG_FILES"] = " ".join(sorted(old_values))

catalog_file = Path(__file__).parent / "catalog" / "catalog.xml"
add_catalog_to_env(catalog_file)
