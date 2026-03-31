# gams-xml-catalog

A Python library which provides an XML catalog for GAMS projects.

Since lxml version 6 upgraded the lxml2 library, fetching resources from 
the internet is now disallowed by default. 

To keep things working, we created this library, which provides local copies of
some ressources frequently used in GAMS projects. These resources a made
accessible via the standard XML Catalog mechanism (https://xmlcatalogs.org/).

Additionally it provides a  resolve_uri_to_path function, which returns the local
path for a catalog resource. For most cases using the default catalog mechanism
should be preferred (this is to use the gams_xml_catalog.activate_catalog() function 
an rely on the catalog resolving provided by tools like lxml or saxonche).

## Installation

The library can be installed using pip:

```
pip install gams-xml-catalog
``` 

## Usage

To use the catalog in your python code all you have to do is to import 
the library and activate it:

```python
import gams_xml_catalog
gams_xml_catalog_activate()
```

This will temporarily add the Path to the catalog to the environment variable
`XML_CATALOG_FILES`, so that lxml will use the locally 
installed copies when they are requested via internet URIs.
As XML catalogs are not restricted to libxml2, this will also work for
other XML-libraries and programs as long as they have support for XML Catalogs.

### Direct URI to Path Resolution

For non-XML file types (RelaxNG Compact, Schematron, etc.) or when you need to resolve
a URI to a local file path without triggering XML parsing, use the `resolve_uri_to_path()` function:

```python
import gams_xml_catalog 

# Resolve a RelaxNG Compact file (no XML parsing required)
path = gams_xml_catalog.resolve_uri_to_path("http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rnc")
print(f"Local file: {path}")  
# Output: /path/to/catalog/tei/p5/relaxng/tei_all.rnc

# Alternatively, for advanced use cases, create a resolver instance:
from gams_xml_catalog import CatalogResolver, get_catalog_path

resolver = CatalogResolver(get_catalog_path())
path = resolver.resolve("http://purl.org/dc/elements/1.1/")  # auto-detect URI or system ID
path = resolver.resolve_uri("http://www.w3.org/1999/xlink")  # explicit URI resolution
path = resolver.resolve_system("http://www.tei-c.org/release/xml/tei/custom/schema/xsd/tei_all.xsd")  # system ID
```

This is especially useful when:
- Processing RelaxNG Compact (`.rnc`) or other Compact syntax formats
- Pre-resolving URIs before passing to tools that don't support XML catalogs
- Building dependency graphs across schemas without triggering parsing errors

## License

The code of this library is distributed under the MIT license. See `LICENSE`
for details. The XML resources (schemas) included in the catalog are 
mostly in the public domain. For some resources I could not find any 
licensing information.

