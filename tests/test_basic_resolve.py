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

xmlcatalog.set_debug(True)

# pylint: disable=c-extension-no-member

def catalog_resolves_dtd(uri: str) -> bool:
    """Check if a DTD URI resolves to a local file.

    Returns True if catalog returns a file.
    """
    parser = ET.XMLParser(load_dtd=True, dtd_validation=False, no_network=True)
    xml_input = f'<!DOCTYPE root SYSTEM "{uri}"><root/>'
    root = ET.fromstring(
        xml_input, parser=parser
    )  # , base_url="http://test-context.local")
    try:
        root.getroottree().docinfo  # pylint: disable=expression-not-assigned
        # if we can access info, parse was successful
        return True
    except Exception:  # pylint: disable=broad-except
        return False


def catalog_resolves_rnc(uri: str) -> bool:
    """Check if a RNC URI resolves to a local file.

    Returns True if catalog returns a file.
    """
    # this is hacky, but all we want to test is that we can get a file via catalog:
    # rnc of cause is not parsable as xml, but if we get an XMLSyntaxException,
    # we should have received a file via catalog
    try:
        parser = ET.XMLParser(load_dtd=True, dtd_validation=False, no_network=True)
        ET.parse(uri, parser)
        return True
    except lxml.etree.XMLSyntaxError:
        # except ET.XMLSyntaxException:
        return True
    except Exception as e:  # pylint: disable=broad-except
        # any other exceptions are unexpected
        print(f"Resolving problem: {e}")
        return False


def catalog_resolves(uri: str) -> bool:
    """Check if a URI resolves to a local file.

    Returns True if catalog returns a file.
    """
    if uri.endswith(".dtd"):
        return catalog_resolves_dtd(uri)
    if uri.endswith(".rnc"):
        return catalog_resolves_rnc(uri)
    # Parser erstellen und unseren Debugger registrieren
    parser = ET.XMLParser(no_network=True)
    # parser.resolvers.add(CatalogDebugger())
    try:
        doc = ET.parse(uri, parser)
        if Path(doc.docinfo.URL).is_file():
            return True
        print(f"Local file {doc.docinfo.URL} does not exists.")
        return False
    except Exception as e:  # pylint: disable=broad-except
        print(f"Resolving problem: {e}")
        return False


def read_datafile(filename: str, add_https: bool = False) -> Generator[str, None, None]:
    """Read a file from data dir and yield each line.

    If the add_https flag is True, we duplicate each line with https
    lines starting with '#' are ignored
    """
    data_dir = Path(__file__).parent / "data"
    data_file = data_dir / Path(filename)
    for line in data_file.read_text().splitlines():
        clean_line = line.strip()
        if clean_line.startswith("#") or clean_line == "":
            continue
        yield clean_line
        if add_https:
            yield clean_line.replace("http://", "https://")


@pytest.mark.parametrize(
    "uri", read_datafile("dublincore/xsd_uris.txt", add_https=True)
)
def test_resolve_dublincore_xsds(uri):
    """Make sure all uris from dc_urls.txt are resoled by the catalog.

    dc uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("loc/mets_xsd_uris.txt", add_https=True))
def test_resolve_loc_mets_xsds(uri):
    """Make sure all uris from mets_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("loc/mods_xsd_uris.txt", add_https=True))
def test_resolve_loc_mods_xsds(uri):
    """Make sure all uris from mods_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("loc/premis_xsd_uris.txt", add_https=True)
)
def test_resolve_loc_premis_xsds(uri):
    """Make sure all uris from premis_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("tei/p5_xsd_uris.txt", add_https=False))
def test_resolve_tei_xsds(uri):
    """Make sure all uris from tei/p4_xsd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("tei/p5_rng_uris.txt", add_https=False))
def test_resolve_tei_rngs(uri):
    """Make sure all uris from tei/_p5_rng_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("tei/p5_dtd_uris.txt", add_https=False))
def test_resolve_teip5_dtds(uri):
    """Make sure all uris from tei/p5_dtd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves_dtd(uri)


@pytest.mark.parametrize("uri", read_datafile("tei/p4_dtd_uris.txt", add_https=False))
def test_resolve_teip4_dtds(uri):
    """Make sure all uris from tei/p4_dtd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves_dtd(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/xinclude_xsd_uris.txt", add_https=False)
)
def test_resolve_w3c_xinclude_xsds(uri):
    """Make sure all uris from xinclude_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/xlink_xsd_uris.txt", add_https=False)
)
def test_resolve_w3c_xlink_xsds(uri):
    """Make sure all uris from xlink_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize("uri", read_datafile("w3c/xml_xsd_uris.txt", add_https=False))
def test_resolve_w3c_xml_xsds(uri):
    """Make sure all uris from xml_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/xmlschema_xsd_uris.txt", add_https=False)
)
def test_resolve_w3c_xmlschema_xsds(uri):
    """Make sure all uris from xmlschema_xsd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/xmlschema_dtd_uris.txt", add_https=False)
)
def test_resolve_w3c_xmlschema_dtds(uri):
    """Make sure all uris from xmlschema_dtd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/mathml_xsd_uris.txt", add_https=False)
)
def test_resolve_w3c_mathml_xsds(uri):
    """Make sure all uris from w3c/mathml_xsd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)


@pytest.mark.parametrize(
    "uri", read_datafile("w3c/mathml_dtd_uris.txt", add_https=False)
)
def test_resolve_w3c_mathml_dtds(uri):
    """Make sure all uris from w3c/mathml_dtd_uris.txt are resoled by the catalog.

    mets uris sometimes use https instead of http, so this test checks both
    """
    assert catalog_resolves(uri)

@pytest.mark.parametrize(
    "uri", read_datafile("example/example.txt", add_https=False)
)
def test_resolve_example_com(uri):
    """Make sure all uris from the example dir (example.com) are resoled by the catalog.

    """
    assert catalog_resolves(uri)
