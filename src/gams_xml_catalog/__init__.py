"""GAMS catalog

This module provides an XML Catalog for the most important XML Ressource.

The catalog is activated by calling `activate_catalog()`, which adds the catalog 
file to the environment variable `XML_CATALOG_FILES`. After activation, 
XML parsers that support XML Catalogs should be able to resolve DTDs and other 
resources defined in the catalog without needing to access the network.

Use `catalog.catalog_file` to get the path to the catalog file.

For direct URI/system identifier to local path resolution (without XML parsing),
use `resolve_uri_to_path()` or instantiate `CatalogResolver.` This is especially
useful for non-XML file types like RelaxNG Compact (.rnc) and Schematron (.sch).
"""

from pathlib import Path
import os
from .resolver import CatalogResolver

def get_catalog_path() -> Path:
    """Get the path to the catalog file.
    
    This path is relative to this __init__.py file, so it will work regardless of the 
    current working directory.
    """
    return Path(__file__).parent / "catalog" / "catalog.xml"

def add_catalog_to_env(cat_file: Path|str) -> None:
    """Set the XML Catalog to the environment variable XML_CATALOG_FILES.
    
    In most cases you should use activate_catalog() instead, which calls this function internally.
    """
    cat_file = Path(cat_file)
    old_values = set(os.environ.get("XML_CATALOG_FILES", "").split())
    old_values.add(str(cat_file.resolve()))
    os.environ["XML_CATALOG_FILES"] = " ".join(sorted(old_values))

def activate_catalog(debug=False) -> None:
    """Activate the catalog.
     
      
    Activating means, that the catalog is added to the environment variable XML_CATALOG_FILES.
    This enables XML parsers that support XML Catalogs to resolve DTDs and other resources defined 
    in the catalog without needing to access the network.
    """
    catalog_file = get_catalog_path()
    add_catalog_to_env(catalog_file)
    if debug:
        os.environ["XML_CATALOG_DEBUG"] = "1"
    else:
        os.environ["XML_CATALOG_DEBUG"] = "0"


# Global resolver instance (lazy-loaded)
_resolver: CatalogResolver | None = None


def _get_resolver() -> CatalogResolver:
    """Get or create the singleton resolver instance."""
    global _resolver
    if _resolver is None:
        _resolver = CatalogResolver(get_catalog_path())
    return _resolver


def resolve_uri_to_path(
    identifier: str, kind: str = "auto"
) -> Path | None:
    """
    Resolve a URI or system identifier to a local file path.

    This function uses catalog rules to map URIs and system identifiers to local
    file paths without requiring XML parsing. It is safe for non-XML file types
    like RelaxNG Compact (.rnc) and Schematron (.sch).

    For xml based resource resolution, it is recommended to use an XML parser with 
    catalog support instead, which will automatically use the activated catalog.

    Args:
        identifier: URI or system identifier to resolve.
        kind: Resolution strategy:
              - "auto" (default): Try URI resolution first, then system.
              - "uri": Treat as URI identifier only.
              - "system": Treat as system identifier only.

    Returns:
        Absolute Path to the resolved local file, or None if not found in catalog.

    Example:
        >>> from gams_xml_catalog import resolve_uri_to_path
        >>> path = resolve_uri_to_path("http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rnc")
        >>> print(path)
        /path/to/package/catalog/tei/p5/relaxng/tei_all.rnc
    """
    resolver = _get_resolver()
    return resolver.resolve(identifier, kind)


# Public API
__all__ = [
    # Catalog path and activation (existing API)
    "get_catalog_path",
    "add_catalog_to_env",
    "activate_catalog",
    # URI resolution (new API)
    "resolve_uri_to_path",
    "CatalogResolver",
]
