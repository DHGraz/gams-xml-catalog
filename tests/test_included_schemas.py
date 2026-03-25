"""Tests if alle imported an included files can be resolved.

Some xsds import other schemas via 

<xs:include schemaLocation=
or <xs:import schemaLocation=...>. 

This test checks if all schemas contained in the catalog can be loaded.
"""

import os
from pathlib import Path

import pytest
from lxml import etree as ET

import gams_xml_catalog
gams_xml_catalog.activate_catalog(debug=True)


def get_xsd_included_schema_uris(schema_name: str="") -> list[str]:
    """Return the uris of all schemas referenced via <xs:include or <xs:import>.

    Returns a list of tuples (resolved_path, relative_resolved_path,referencing_file) where 

     - resolved_path ist the absolute path to the included schema,
     - relative_resolved_path is the path to the included schema relative to the catalog base dir, and
     - referencing_file is the file that includes it.

    As references are mostly relative, resolved_path is relative to the
    referencing file (and we expect the referenced file to be in the catalog)
    """
    catalog_base_dir = (Path(gams_xml_catalog.__file__).parent / "catalog").as_posix()
    if schema_name:
        catalog_base_dir = os.path.join(catalog_base_dir, schema_name)
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

def assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves):
    """Reusable assertion for included schema resolvability.

    Asserts if the included schema (identified by abs_path) is resolvable via the catalog, 
    providing a clear error message that includes the referencing file for context.
    """
    needed_parts = []
    parts = referencing_file.split('/')
    for part in reversed(parts):
        # not interested 'catalog' directories
        if part == 'catalog':
            break
        needed_parts.append(part)
    short_referencing_file = '/'.join(reversed(needed_parts))
    
    if abs_path.startswith(("http://", "https://")):
        assert catalog_resolves(abs_path), (
            f"URI '{abs_path}' does not resolve via catalog (referenced in {short_referencing_file})."
        )
    else:
        assert catalog_resolves(abs_path), (
            f"Relative reference '{abs_path}' does not resolve to a local file referenced in {short_referencing_file}."
        )


# Testing all included schemas at once became to convoluted
# So we test references fpr schemas in specific directories (like dublincore, tei etc).
xsd_references_to_test = get_xsd_included_schema_uris('dublincore')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_dublincore_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)
    

xsd_references_to_test = get_xsd_included_schema_uris('europeana')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_europeana_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)
    
    
xsd_references_to_test = get_xsd_included_schema_uris('isotc211')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_isotc211_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)


xsd_references_to_test = get_xsd_included_schema_uris('lido')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_isotc211_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)

xsd_references_to_test = get_xsd_included_schema_uris('loc')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_loc_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)

xsd_references_to_test = get_xsd_included_schema_uris('opengis/gml/3.1.1')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_opengis_gml_schemas_3_1_1(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)

xsd_references_to_test = get_xsd_included_schema_uris('opengis/gml/3.2.1')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_opengis_gml_schemas_3_2_1(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)

xsd_references_to_test = get_xsd_included_schema_uris('opengis/gml/3.3')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_opengis_gml_schemas_3_3(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)

xsd_references_to_test = get_xsd_included_schema_uris('opengis/iso')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_opengis_iso_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)


xsd_references_to_test = get_xsd_included_schema_uris('tei')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_tei_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)

xsd_references_to_test = get_xsd_included_schema_uris('w3c')
@pytest.mark.parametrize(
    "abs_path, rel_path, referencing_file", 
     xsd_references_to_test,
    ids=[tup[1] for tup in xsd_references_to_test]
)
def test_included_w3c_schemas(abs_path, rel_path, referencing_file, catalog_resolves):
    """Make sure all included schemas are resolvable by the catalog.
    
    abs_path can be a path to a local file or a url.
    """
    assert_included_schema_resolves(abs_path, referencing_file, catalog_resolves)


