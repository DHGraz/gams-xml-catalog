from pathlib import Path
from typing import Generator

from lxml import etree as ET
import lxml
import pytest

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


@pytest.fixture(name="catalog_resolves")
def catalog_resolves_fixture() -> bool:
    """Return a callable that checks if a URI resolves to a local file. 

    Returns True if catalog returns a file.
    """
    def resolves(uri: str) -> bool:
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
    return resolves


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