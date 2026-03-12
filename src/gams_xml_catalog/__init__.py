"""GAMS catalog

This module provides an XML Catalog for the most important XML Ressource.

The catalog is activated by calling `activate_catalog()`, which adds the catalog 
file to the environment variable `XML_CATALOG_FILES`. After activation, 
XML parsers that support XML Catalogs should be able to resolve DTDs and other 
resources defined in the catalog without needing to access the network.

Use `catalog.catalog_file` to get the path to the catalog file.
"""

from pathlib import Path
import os



def add_catalog_to_env(cat_file: Path|str) -> None:
    """Set the XML Catalog to the environment variable XML_CATALOG_FILES."""
    cat_file = Path(cat_file)
    old_values = set(os.environ.get("XML_CATALOG_FILES", "").split())
    old_values.add(str(cat_file.resolve()))
    os.environ["XML_CATALOG_FILES"] = " ".join(sorted(old_values))

def activate_catalog(debug=False) -> None:
    """Activate the catalog by adding it to the environment variable XML_CATALOG_FILES."""
    catalog_file = Path(__file__).parent / "catalog" / "catalog.xml"
    add_catalog_to_env(catalog_file)
    if debug:
        os.environ["XML_CATALOG_DEBUG"] = "1"
    else:
        os.environ["XML_CATALOG_DEBUG"] = "0"
