# gams-xml-catalog

A Python package that provides an XML catalog containing schema files commonly needed in GAMS projects.

Starting with lxml version 6, the underlying libxml2 library disables fetching resources from the internet by default for security reasons. This library solves that problem by providing local copies of frequently used XML schemas and resources, making them accessible through the standard XML Catalog mechanism (https://xmlcatalogs.org/).

Additionally, it provides a `resolve_uri_to_path()` function to retrieve the local file path for any catalog resource. In most cases, using the default catalog mechanism is preferred—simply call `gams_xml_catalog.activate_catalog()` and let tools like lxml or saxonche handle URI resolution automatically.

## Installation

Install the package from PyPI using pip:

```
pip install gams-xml-catalog
``` 

## Usage

To use the catalog, simply import and activate it:

```python
import gams_xml_catalog
gams_xml_catalog.activate_catalog()
```

This temporarily adds the catalog path to the `XML_CATALOG_FILES` environment variable, enabling lxml and other XML-aware tools to use local copies instead of fetching resources from the internet. Any tool with XML Catalog support will automatically benefit from this setup.

### Direct URI to Path Resolution

For non-XML formats (such as RelaxNG Compact) or when you need to resolve URIs without triggering XML parsing, use the `resolve_uri_to_path()` function:

```python
import gams_xml_catalog 

# Resolve a RelaxNG Compact file (no XML parsing)
path = gams_xml_catalog.resolve_uri_to_path("http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rnc")
print(f"Local file: {path}")
# Output: /path/to/catalog/tei/p5/relaxng/tei_all.rnc

# For advanced use cases, create a CatalogResolver instance:
from gams_xml_catalog import CatalogResolver, get_catalog_path

resolver = CatalogResolver(get_catalog_path())
path = resolver.resolve("http://purl.org/dc/elements/1.1/")  # auto-detect URI or system ID
path = resolver.resolve_uri("http://www.w3.org/1999/xlink")  # resolve as URI
path = resolver.resolve_system("http://www.tei-c.org/release/xml/tei/custom/schema/xsd/tei_all.xsd")  # resolve as system ID
```

This approach is useful for:
- Processing non-XML formats like RelaxNG Compact (`.rnc`)
- Pre-resolving URIs for tools without XML Catalog support
- Building schema dependency graphs without triggering parse errors

## Contributing

The Github repository is ment to be a read only mirror of the work repository
hosted on our institutional private Github server. You can use the bug tracker
on Github, but everything else should happen in the Zimlab Github repo.


## License

The package code is distributed under the MIT license (see `LICENSE` for details). The XML schemas and resources included in the catalog are primarily in the public domain. For some resources, explicit licensing information was not available.

