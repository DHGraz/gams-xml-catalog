"""Some xsds import other schemas via <xs:include schemaLocation="""

import os
from pathlib import Path

import pytest
from lxml import etree as ET

import gams_xml_catalog


def get_xsd_included_schema_uris() -> list[str]:
    """Return the uris of all schemas referenced via <xs:include or <xs:import>.

    Returns a list of tuples (resolved_path, relative_resolved_path,referencing_file) where 

     - resolved_path ist the absolute path to the included schema,
     - relative_resolved_path is the path to the included schema relative to the catalog base dir, and
     - referencing_file is the file that includes it.

    As references are mostly relative, resolved_path is relative to the
    referencing file (and we expect the referenced file to be in the catalog)
    """
    catalog_base_dir = (Path(gams_xml_catalog.__file__).parent / "catalog").as_posix()
    uris = set()
    for root, _, files in os.walk(catalog_base_dir):
        for file in files:
            if file.endswith(".xsd"):
                file_path = os.path.join(root, file)
                tree = ET.parse(file_path)
                root_element = tree.getroot()
                for include in root_element.findall(
                    ".//{http://www.w3.org/2001/XMLSchema}include"
                ):
                    schema_location = include.get("schemaLocation")
                    if schema_location:
                        uris.add((schema_location, file_path))
                for import_ in root_element.findall(
                    ".//{http://www.w3.org/2001/XMLSchema}import"
                ):
                    schema_location = import_.get("schemaLocation")
                    if schema_location:
                        uris.add((schema_location, file_path))
    resolved_uris = []
    # referenced via path ist relative to referencing file, so we need to resolve it to 
    # get the correct path for catalog lookup
    for uri, referencing_file in uris:
        if uri.startswith(("http://", "https://")):
            resolved_uris.append((uri, uri, referencing_file))
        else:
            # make a path which makes uri relative to referending_file
            root = os.path.dirname(referencing_file)
            resolved_path = os.path.normpath(os.path.join(root, uri))
            resolved_relative_path = os.path.relpath(resolved_path, catalog_base_dir)
            resolved_uris.append((resolved_path, resolved_relative_path, referencing_file)) 
    return sorted(resolved_uris)


xsd_references_to_test = get_xsd_included_schema_uris()
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    needed_parts = []
    parts = referencing_file.split('/')
    for part in reversed(parts):
        if part == 'catalog':
            break
        needed_parts.append(part)
    short_referencing_file = '/'.join(reversed(needed_parts))
    
    if abs_path.startswith(("http://", "https://")):
        assert catalog_resolves(abs_path), (
            f"URI {abs_path} does not resolve via catalog (referenced in {short_referencing_file})."
        )
    else:
        assert catalog_resolves(abs_path), (
            f"Relative reference {abs_path} does not resolve to a local file referenced in {short_referencing_file}."
        )
    

# if __name__ == "__main__":
#     # for debugging, run the test directly and print the uris:
#     for abs_path, rel_path, referencing_file in get_xsd_included_schema_uris():
#         print(f"{abs_path}\n{rel_path}\n{referencing_file}")
#         print("")