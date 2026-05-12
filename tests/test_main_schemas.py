"""Test if catalog allows to create lxml schema objects.

This is a variant of the test_included_schemas.py. It is different, because it
additionally makes sure, that the main schema can be converted into a lxml schema object. 

This is not really a test for this package, as creating a schema object is not a function 
of the catalog, but as the creation of some schemas failed, this is the most simple place to 
test why things fail.
"""

import lxml.etree as ET
import pytest

import gams_xml_catalog as xmlcatalog  # This is important!
xmlcatalog.activate_catalog(debug=True)  # activate the catalog for the tests

@pytest.mark.parametrize(
    "schema_uri", [
        "http://www.tei-c.org/release/xml/tei/custom/schema/xsd/tei_all.xsd",
        "http://dublincore.org/schemas/xmls/simpledc20021212.xsd",
        "http://www.europeana.eu/schemas/edm/EDM.xsd",
        "http://www.lido-schema.org/schema/v1.0/lido-v1.0.xsd",
        "http://www.lido-schema.org/schema/v1.1/lido-v1.1.xsd",
        "http://www.loc.gov/mets/mets.xsd",
        "http://www.loc.gov/premis/v2/premis-v2-3.xsd",
        "http://www.loc.gov/premis/v3/premis-v3-0.xsd",
        "http://www.opengis.net/gml/3.2.1/gml.xsd",
        "http://www.opengis.net/gml/3.1.1/base/gml.xsd",
        "https://schema.datacite.org/meta/kernel-4/metadata.xsd",
    ]
)
def test_create_xmlschema_objects(schema_uri):
    """Test if we can create a schema object for the given uri."""
    try:
        ET.XMLSchema(ET.parse(schema_uri))
    except Exception as e:
        pytest.fail(f"Failed to create XMLSchema object for {schema_uri}: {e}")


