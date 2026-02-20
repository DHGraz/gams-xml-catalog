# gams-xml-catalog

A Python library which provides an XML catalog for GAMS projects.

Since lxml version 6 upgraded the lxml2 library, fetching resources from 
the internet is now disallowed by default. 

To keep things working, we created this library, which provides local copies of
some ressources frequently used in GAMS projects. These resources a made
accessible via the standard XML Catalog mechanism (https://xmlcatalogs.org/).

## Installation

The library can be installed using pip:

```
pip install gams-xml-catalog
``` 

## Usage

To use the catalog in your python code all you have to do is to import 
the library:

```
import gams_xml_catalog
```

This will temporarily add the Path to the catalog to the environment variable
`XML_CATALOG_FILES`, so that lxml will used the locally installed copies when
they are requested via internet URIs.

As XML catalogs are not restricted to libxml2, this will also work for
other XML-libraries and programs as long as they have support for XML Catalogs.

## License

The code of this library is distributed under the MIT license. See `LICENSE`
for details. The XML resources (schemas) included in the catalog are 
mostly in the public domain. For some resources I could not find any 
licensing information.

