"""Check if the module is initualized correctly.

The module should modify the environment variable XML_CATALOG_FILES
to include the root catalog file of gams_xml_catalog.
"""

import os

import gams_xml_catalog as xmlcatalog
xmlcatalog.activate_catalog(debug=True)  # activate the catalog for the tests


def test_activate_catalog():
    """Test the activate_catalog function.
    """
    # patch the local environment to avoid side effects on the real environment
    os.environ = os.environ.copy()
    os.environ["XML_CATALOG_FILES"] = ""
    xmlcatalog.activate_catalog()
    assert os.environ["XML_CATALOG_FILES"].endswith(
        "gams_xml_catalog/catalog/catalog.xml"
    )
    assert os.environ["XML_CATALOG_DEBUG"] == "0"  # debug should be off by default

    # test that debug can be turned on
    xmlcatalog.activate_catalog(debug=True)
    assert os.environ["XML_CATALOG_DEBUG"] == "1"

    # test that debug can be turned off    xmlcatalog.activate_catalog(debug=False)
    xmlcatalog.activate_catalog(debug=False)
    assert os.environ["XML_CATALOG_DEBUG"] == "0"



def test_add_catalog_to_env():
    """Test the add_catalog_to_env function."""
    # patch the local environment to avoid side effects on the real environment
    os.environ = os.environ.copy()
    os.environ["XML_CATALOG_FILES"] = ""

    xmlcatalog.add_catalog_to_env("/foo/bar/test.xml")
    catalog_paths = os.environ["XML_CATALOG_FILES"].split()
    assert "/foo/bar/test.xml" in catalog_paths



