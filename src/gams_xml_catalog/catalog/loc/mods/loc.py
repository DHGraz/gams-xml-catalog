import re
import sys
from collections import Counter
from pathlib import Path
from typing import Generator
from lxml import etree as ET


def extract_schemalocations(file: Path) -> Generator[tuple[str, str, str], None, None]:
    """Yield all schema locations found in all xml imports in file.

    Each yielded tuple contains:
    (schemalLocation, namespace, filepath as str) 
    """
    tree = ET.parse(file)
    root = tree.getroot()
    ns = {
        "catalog": "urn:oasis:names:tc:entity:xmlns:xml:catalog",
        "xsd": "http://www.w3.org/2001/XMLSchema",
    }
    # find all uri elements in document
    for el in root.findall(".//xsd:import", ns):
        yield(el.attrib["schemaLocation"], el.attrib["namespace"], file.as_posix())


def collect_uris_from_xsds(root) -> list[tuple[str, str, Path]]:
    "Iterate over all xsd files and collect alls URIs references via schemLocation."
    result = set()
    for file in Path(root).rglob("*.xsd"):
        for ref in extract_schemalocations(file):
            result.add(ref)
    return sorted(result)


def extract_names_from_catalog_uris(
    file: Path,
) -> Generator[tuple[str, str, str], None, None]:
    """Yield all URIs referenced by name attribute found in a file.

    Return tuple (name, uri, filepath as str)
    """
    tree = ET.parse(file)
    root = tree.getroot()
    ns = {"catalog": "urn:oasis:names:tc:entity:xmlns:xml:catalog"}
    for el in root.findall(".//catalog:uri", ns):
        yield (el.attrib["name"], el.attrib["uri"], file)


def collect_registered_uris(root: str) -> list[tuple[str, Path]]:
    "Iterate over all catalog.xml files and collect all URIs references."
    uris_found = set()
    for file in Path(root).rglob("catalog.xml"):
        for catalog_uri in extract_names_from_catalog_uris(file):
            uris_found.add(catalog_uri)
    return sorted(uris_found)


def check_for_duplicates(entries: list[str]):
    "Search for uris which appear more than once."
    names = [uri[0] for uri in entries]
    duplicate_names = {}
    # find names which appear more than once
    counter = Counter(names)
    for uri, count in counter.items():
        if count > 1:
            duplicate_names[uri] = []
    # for each duplicate name, collect data about context (uri, catalog)
    for name, uri, catalog_file in entries:
        if name in duplicate_names:
            duplicate_names[name].append((uri, catalog_file))

    # generate report
    for name, context_data in duplicate_names.items():  
        print(f"Duplicate name: '{name} is referenced in:")
        for uri, file in context_data:
            print(f"    '{Path(uri).resolve().as_posix()}' referenced in {file}")   
    # maybe check for identical files?

def find_missing_references(
    referenced_uris_: list[tuple[str, Path]], registered_uris_: list[tuple[str, Path]]
) -> list[tuple[str, Path]]:
    """Return URIs referenced in an xsd but unknown in catalog."""
    result = []
    reg_uris = [entry[0] for entry in registered_uris_]
    for uri, file in referenced_uris_:
        if uri not in reg_uris:
            result.append((uri, file))

    return result


if __name__ == "__main__":
    referenced_uris = collect_uris_from_xsds(".")
    registered_uris = collect_registered_uris('.')
    check_for_duplicates(registered_uris)
    # #unregistered_uris = {entry[0] for entry in referenced_uris} - {entry[0] for entry in registered_uris}
    # missing_refs = find_missing_references(referenced_uris, registered_uris)
    # for missing_ref in missing_refs:
    #     print(missing_ref)

# for uri in uris:
# print(uri)
