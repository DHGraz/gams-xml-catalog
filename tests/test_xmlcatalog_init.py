"""Check if the module is initualized correctly.

The module should modify the environment variable XML_CATALOG_FILES
to include the root catalog file of gams_xml_catalog.
"""

import os

import gams_xml_catalog as xmlcatalog


def test_env_value_init():
    """Test the catalog initializer.

    When the package is imported, the initializer should modify
    the XML_CATALOG_FILES environment variable to  include the root
    catalog file of gams_xml_catalog.
    """
    assert os.environ["XML_CATALOG_FILES"].endswith(
        "gams_xml_catalog/catalog/catalog.xml"
    )


def test_add_catalog_to_env(monkeypatch):
    """Test the add_catalog_to_env function."""
    # patch the local environment to avoid side effects on the real environment
    monkeypatch.setattr(os, "environ", os.environ.copy())

    xmlcatalog.add_catalog_to_env("/foo/bar/test.xml")
    catalog_paths = os.environ["XML_CATALOG_FILES"].split()
    assert "/foo/bar/test.xml" in catalog_paths


def test_set_debug(monkeypatch):
    """Test the set_debug function."""
    # patch the local environment to avoid side effects on the real environment
    monkeypatch.setattr(os, "environ", os.environ.copy())

    xmlcatalog.set_debug(True)
    assert os.environ["XML_CATALOG_DEBUG"] == "1"

    xmlcatalog.set_debug(False)
    assert os.environ["XML_CATALOG_DEBUG"] == "0"
