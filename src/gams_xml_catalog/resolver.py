"""
Pure-Python OASIS XML Catalog resolver for URI/system identifier to local path lookup.

Supports:
- <nextCatalog> chaining
- <uri name="..." uri="..."/>
- <system systemId="..." uri="..."/>
- <rewriteURI uriStartString="..." rewritePrefix="..."/>
- <rewriteSystem systemIdStartString="..." rewritePrefix="..."/>

No lxml, libxml2, or ctypes dependencies. Safe for non-XML file types (.rnc, .sch, etc.)
across macOS, Linux, Windows.
"""

from pathlib import Path
from xml.etree import ElementTree as ET
from typing import Dict, List, Optional
from dataclasses import dataclass


@dataclass(frozen=True)
class CatalogRule:
    """Single exact URI or system mapping."""
    identifier: str  # URI name or system systemId
    local_path: str  # relative path to local file


@dataclass(frozen=True)
class RewriteRule:
    """Single rewrite prefix rule, normalized for longest-match precedence."""
    prefix: str
    replacement: str
    rule_type: str  # "uri" or "system"

    def match(self, identifier: str) -> Optional[str]:
        """If identifier starts with prefix, return rewritten path; else None."""
        if identifier.startswith(self.prefix):
            # Replace prefix with replacement, keeping the rest of identifier
            remainder = identifier[len(self.prefix) :]
            # Ensure replacement ends with '/' if it's a directory prefix
            if not self.replacement.endswith("/") and remainder and not remainder.startswith("/"):
                return self.replacement + "/" + remainder
            return self.replacement + remainder
        return None


class CatalogGraph:
    """Loaded and normalized OASIS catalog structure."""

    def __init__(self, catalog_root: Path):
        self.catalog_root = Path(catalog_root).resolve()
        # Map of URI name -> local relative path
        self.uri_map: Dict[str, str] = {}
        # Map of system systemId -> local relative path
        self.system_map: Dict[str, str] = {}
        # Rewrite rules sorted by descending prefix length (longest first)
        self.rewrite_uri: List[RewriteRule] = []
        self.rewrite_system: List[RewriteRule] = []
        # Tracking for cycle detection
        self._loading_catalogs: set = set()
        
    def resolve_uri(self, uri: str) -> Optional[Path]:
        """Resolve URI identifier to absolute local path or None."""
        # 1. Check exact URI map
        if uri in self.uri_map:
            rel = self.uri_map[uri]
            return self._normalize_path(rel)
        
        # 2. Check rewrite URI rules (longest prefix first)
        for rule in self.rewrite_uri:
            rewritten = rule.match(uri)
            if rewritten is not None:
                return self._normalize_path(rewritten)
        
        return None

    def resolve_system(self, system_id: str) -> Optional[Path]:
        """Resolve system identifier to absolute local path or None."""
        # 1. Check exact system map
        if system_id in self.system_map:
            rel = self.system_map[system_id]
            return self._normalize_path(rel)
        
        # 2. Check rewrite system rules (longest prefix first)
        for rule in self.rewrite_system:
            rewritten = rule.match(system_id)
            if rewritten is not None:
                return self._normalize_path(rewritten)
        
        return None

    def resolve(
        self, identifier: str, kind: str = "auto"
    ) -> Optional[Path]:
        """
        Resolve identifier to local path.

        Args:
            identifier: URI or system identifier to resolve.
            kind: "uri", "system", or "auto".
                  auto tries URI first, then system.

        Returns:
            Absolute Path to resolved file, or None if not found.
        """
        if not isinstance(identifier, str):
            raise TypeError(f"identifier must be str, not {type(identifier).__name__}")
        
        if kind in ("uri", "auto"):
            result = self.resolve_uri(identifier)
            if result:
                return result
        
        if kind in ("system", "auto"):
            result = self.resolve_system(identifier)
            if result:
                return result
        
        return None

    def _normalize_path(self, relative: str) -> Path:
        """
        Normalize relative path from catalog to absolute, rooted at catalog_root.
        """
        resolved = (self.catalog_root / relative).resolve()
        return resolved

    def add_uri_rule(self, uri: str, local_path: str) -> None:
        """Add exact URI rule."""
        self.uri_map[uri] = local_path

    def add_system_rule(self, system_id: str, local_path: str) -> None:
        """Add exact system rule."""
        self.system_map[system_id] = local_path

    def add_rewrite_uri_rule(self, prefix: str, replacement: str) -> None:
        """Add rewrite URI rule (will be sorted by prefix length)."""
        self.rewrite_uri.append(RewriteRule(prefix, replacement, "uri"))
        # Sort by descending prefix length (longest first for correct precedence)
        self.rewrite_uri.sort(key=lambda r: len(r.prefix), reverse=True)

    def add_rewrite_system_rule(self, prefix: str, replacement: str) -> None:
        """Add rewrite system rule (will be sorted by prefix length)."""
        self.rewrite_system.append(RewriteRule(prefix, replacement, "system"))
        # Sort by descending prefix length
        self.rewrite_system.sort(key=lambda r: len(r.prefix), reverse=True)

    def load_from_file(self, catalog_file: Path) -> None:
        """
        Load catalog from XML file, following nextCatalog references.
        Detects cycles to prevent infinite recursion.
        """
        catalog_file = Path(catalog_file).resolve()
        
        # Cycle detection
        if str(catalog_file) in self._loading_catalogs:
            return  # Already loading or loaded
        
        if not catalog_file.exists():
            raise FileNotFoundError(f"Catalog file not found: {catalog_file}")
        
        self._loading_catalogs.add(str(catalog_file))
        
        try:
            tree = ET.parse(str(catalog_file))
            root = tree.getroot()
            
            # Parse elements in document order
            for elem in root:
                # Trim namespace if present (e.g., '{...}uri' -> 'uri')
                tag = elem.tag.split("}")[-1] if "}" in elem.tag else elem.tag
                
                if tag == "uri":
                    self._parse_uri_element(elem, catalog_file.parent)
                elif tag == "system":
                    self._parse_system_element(elem, catalog_file.parent)
                elif tag == "rewriteURI":
                    self._parse_rewrite_uri_element(elem, catalog_file.parent)
                elif tag == "rewriteSystem":
                    self._parse_rewrite_system_element(elem, catalog_file.parent)
                elif tag == "nextCatalog":
                    self._parse_next_catalog_element(elem, catalog_file.parent)
        finally:
            self._loading_catalogs.discard(str(catalog_file))

    def _parse_uri_element(self, elem, base_dir: Path) -> None:
        """Parse <uri name="..." uri="..."/> element."""
        name = elem.get("name")
        uri = elem.get("uri")
        if name and uri:
            # Resolve relative uri against base_dir
            resolved = self._resolve_relative(uri, base_dir)
            self.add_uri_rule(name, resolved)

    def _parse_system_element(self, elem, base_dir: Path) -> None:
        """Parse <system systemId="..." uri="..."/> element."""
        system_id = elem.get("systemId")
        uri = elem.get("uri")
        if system_id and uri:
            resolved = self._resolve_relative(uri, base_dir)
            self.add_system_rule(system_id, resolved)

    def _parse_rewrite_uri_element(self, elem, base_dir: Path) -> None:
        """Parse <rewriteURI uriStartString="..." rewritePrefix="..."/> element."""
        uri_prefix = elem.get("uriStartString")
        rewrite = elem.get("rewritePrefix")
        if uri_prefix and rewrite:
            resolved = self._resolve_relative(rewrite, base_dir)
            self.add_rewrite_uri_rule(uri_prefix, resolved)

    def _parse_rewrite_system_element(self, elem, base_dir: Path) -> None:
        """Parse <rewriteSystem systemIdStartString="..." rewritePrefix="..."/> element."""
        sys_prefix = elem.get("systemIdStartString")
        rewrite = elem.get("rewritePrefix")
        if sys_prefix and rewrite:
            resolved = self._resolve_relative(rewrite, base_dir)
            self.add_rewrite_system_rule(sys_prefix, resolved)

    def _parse_next_catalog_element(self, elem, base_dir: Path) -> None:
        """Parse <nextCatalog catalog="..."/> element and recursively load."""
        catalog_rel = elem.get("catalog")
        if catalog_rel:
            next_file = base_dir / catalog_rel
            if next_file.exists():
                self.load_from_file(next_file)

    def _resolve_relative(self, path_str: str, base_dir: Path) -> str:
        """
        Resolve relative paths to be relative to catalog_root (not base_dir).
        This ensures all internal references scale correctly when catalog moves.
        """
        # If absolute, return as-is (rare in catalogs)
        if path_str.startswith("/"):
            return path_str
        
        # Convert base_dir-relative to catalog_root-relative
        target = (base_dir / path_str).resolve()
        try:
            rel_to_root = target.relative_to(self.catalog_root)
            return str(rel_to_root)
        except ValueError:
            # Target is outside catalog_root; return absolute path
            return str(target)


class CatalogResolver:
    """
    High-level resolver API. Manages loading and caching of catalog graphs.
    """

    def __init__(self, root_catalog: Path):
        """
        Initialize resolver with root catalog file.

        Args:
            root_catalog: Path to the root OASIS catalog XML file.
        """
        self.root_catalog = Path(root_catalog).resolve()
        self._graph: Optional[CatalogGraph] = None

    @property
    def graph(self) -> CatalogGraph:
        """Lazily load and cache the catalog graph."""
        if self._graph is None:
            self._graph = CatalogGraph(self.root_catalog.parent)
            self._graph.load_from_file(self.root_catalog)
        return self._graph

    def resolve(
        self, identifier: str, kind: str = "auto"
    ) -> Optional[Path]:
        """
        Resolve identifier to local path.

        Args:
            identifier: URI or system identifier.
            kind: "uri", "system", or "auto" (tries uri, then system).

        Returns:
            Absolute Path to resolved local file, or None if not found.
        """
        return self.graph.resolve(identifier, kind)

    def resolve_uri(self, uri: str) -> Optional[Path]:
        """Resolve as URI identifier."""
        return self.graph.resolve_uri(uri)

    def resolve_system(self, system_id: str) -> Optional[Path]:
        """Resolve as system identifier."""
        return self.graph.resolve_system(system_id)

    def clear_cache(self) -> None:
        """Clear internal catalog graph cache (for testing/reloading)."""
        self._graph = None
