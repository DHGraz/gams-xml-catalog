"""Test uri resolution via catalog for the provides schemas.

This test checks if the uris provided in the data dir can be resolved to 
local files via the catalog.

The URIs to be tested are provided in text files in the data dir. 
Each line should contain one URI to be tested. 
Lines starting with '#' are ignored as comments.
"""

from pathlib import Path
from typing import Generator

import lxml
import pytest
from lxml import etree as ET

import gams_xml_catalog as xmlcatalog  # This is important!

from conftest import read_datafile

xmlcatalog.activate_catalog(debug=True)

# pylint: disable=c-extension-no-member



@pytest.mark.parametrize(
    "uri", read_datafile("dublincore/xsd_uris.txt", add_https=True)
)
def test_resolve_dublincore_xsds(uri, catalog_resolves):
    """Make sure all uris from dc_urls.txt are resoled by the catalog.

    dc uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)

@pytest.mark.parametrize(
    "uri", read_datafile("lido/lido_uris.txt", add_https=True)
)
def test_resolve_lido_xsds(uri, catalog_resolves):
    """Make sure all uris from lido_uris.txt are resoled by the catalog.

    lido uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)

@pytest.mark.parametrize("uri", read_datafile("loc/mets_xsd_uris.txt", add_https=True))
def test_resolve_loc_mets_xsds(uri, catalog_resolves):
    """Make sure all uris from mets_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("loc/mods_xsd_uris.txt", add_https=True))
def test_resolve_loc_mods_xsds(uri, catalog_resolves):
    """Make sure all uris from mods_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("loc/premis_xsd_uris.txt", add_https=True)
)
def test_resolve_loc_premis_xsds(uri, catalog_resolves):
    """Make sure all uris from premis_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("tei/p5_xsd_uris.txt", add_https=False))
def test_resolve_tei_xsds(uri, catalog_resolves):
    """Make sure all uris from tei/p4_xsd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("tei/p5_rng_uris.txt", add_https=False))
def test_resolve_tei_rngs(uri, catalog_resolves):
    """Make sure all uris from tei/_p5_rng_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("tei/p5_dtd_uris.txt", add_https=False))
def test_resolve_teip5_dtds(uri, catalog_resolves):
    """Make sure all uris from tei/p5_dtd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("tei/p4_dtd_uris.txt", add_https=False))
def test_resolve_teip4_dtds(uri, catalog_resolves):
    """Make sure all uris from tei/p4_dtd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/xinclude_xsd_uris.txt", add_https=False)
)
def test_resolve_w3c_xinclude_xsds(uri, catalog_resolves):
    """Make sure all uris from xinclude_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/xlink_xsd_uris.txt", add_https=False)
)
def test_resolve_w3c_xlink_xsds(uri, catalog_resolves):
    """Make sure all uris from xlink_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("w3c/xml_xsd_uris.txt", add_https=False))
def test_resolve_w3c_xml_xsds(uri, catalog_resolves):
    """Make sure all uris from xml_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/xmlschema_xsd_uris.txt", add_https=False)
)
def test_resolve_w3c_xmlschema_xsds(uri, catalog_resolves):
    """Make sure all uris from xmlschema_xsd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/xmlschema_dtd_uris.txt", add_https=False)
)
def test_resolve_w3c_xmlschema_dtds(uri, catalog_resolves):
    """Make sure all uris from xmlschema_dtd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/mathml_xsd_uris.txt", add_https=False)
)
def test_resolve_w3c_mathml_xsds(uri, catalog_resolves):
    """Make sure all uris from w3c/mathml_xsd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/mathml_dtd_uris.txt", add_https=False)
)
def test_resolve_w3c_mathml_dtds(uri, catalog_resolves):
    """Make sure all uris from w3c/mathml_dtd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)

@pytest.mark.parametrize(
    "uri", read_datafile("example/example.txt", add_https=False)
)
def test_resolve_example_com(uri, catalog_resolves):
    """Make sure all uris from the example dir (example.com) are resoled by the catalog.

    """
    assert catalog_resolves(uri)

@pytest.mark.parametrize(
    "uri", read_datafile("opengis/opengis_uris.txt", add_https=False)
)
def test_resolve_opengis_uris(uri, catalog_resolves):
    """Make sure all uris from the opengis dir are resoled by the catalog.

    """
    assert catalog_resolves(uri)
