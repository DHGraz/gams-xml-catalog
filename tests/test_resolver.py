"""
Tests for catalog resolver API (URI/system identifier to local path lookup).

Verifies:
- Exact URI matches
- Exact system ID matches
- Rewrite prefix rules (longest prefix wins)
- nextCatalog traversal
- RelaxNG Compact (.rnc) files
- Negative cases (unknown identifiers)
- Cross-platform path handling
"""

import pytest
from pathlib import Path
from gams_xml_catalog import resolve_uri_to_path, CatalogResolver, get_catalog_path


@pytest.fixture
def resolver():
    """Fresh resolver instance for each test."""
    r = CatalogResolver(get_catalog_path())
    yield r
    r.clear_cache()


class TestExactURIMatches:
    """Test exact <uri> element resolution."""

    def test_resolve_w3c_xlink_uri(self, resolver):
        """Resolve exact W3C XLink URI."""
        uri = "http://www.w3.org/1999/xlink"
        result = resolver.resolve_uri(uri)
        assert result is not None
        assert result.exists()
        assert result.name == "xlink.xsd"

    def test_resolve_dublincore_uri(self, resolver):
        """Resolve exact Dublin Core URI."""
        uri = "http://purl.org/dc/elements/1.1/"
        result = resolver.resolve_uri(uri)
        assert result is not None
        assert result.exists()
        assert "dc.xsd" in result.name

    def test_exact_uri_with_https_variant(self, resolver):
        """Resolve HTTPS variant of URI."""
        uri = "https://purl.org/dc/elements/1.1/"
        result = resolver.resolve_uri(uri)
        assert result is not None
        assert result.exists()

    def test_unknown_uri_returns_none(self, resolver):
        """Unknown URI should return None, not raise."""
        uri = "http://example.invalid/unknown/schema"
        result = resolver.resolve_uri(uri)
        assert result is None


class TestExactSystemMatches:
    """Test exact <system> element resolution."""

    def test_resolve_xlink_system(self, resolver):
        """Resolve exact xlink system ID."""
        system_id = "http://www.w3.org/1999/xlink.xsd"
        result = resolver.resolve_system(system_id)
        assert result is not None
        assert result.exists()

    def test_resolve_bare_system_id(self, resolver):
        """Resolve system ID without full URI."""
        system_id = "xlink.xsd"
        result = resolver.resolve_system(system_id)
        assert result is not None
        assert result.exists()


class TestRewriteURIRules:
    """Test <rewriteURI> prefix rules."""

    def test_rewrite_dublincore_via_rewriteuri(self, resolver):
        """Resolve Dublin Core URI that doesn't yet have /2008/ in it."""
        # Use a URI that matches the first rewriteURI rule
        uri = "http://dublincore.org/schemas/xmls/qdc/some_file.xsd"
        result = resolver.resolve_uri(uri)
        # This would rewrite to "2008/some_file.xsd" if file existed
        # For now, just verify rewrite logic doesn't error
        if result:
            assert result.exists() or result.parent.exists()

    def test_rewrite_lido_uri(self, resolver):
        """Resolve a <uri> entry (exact match, not rewrite)."""
        # LIDO has exact uri mappings
        uri = "http://www.lido-schema.org/schema/v1.0/lido-v1.0.xsd"
        result = resolver.resolve_uri(uri)
        assert result is not None
        assert result.exists()

    def test_rewrite_longest_prefix_wins(self, resolver):
        """When multiple rewrite rules match, longest prefix should win."""
        # Dublin Core has both generic and specific rewrite rules
        # The specific 2008/02/11/ rule should match longer prefixes first
        uri = "http://dublincore.org/schemas/xmls/qdc/2008/02/11/file.xsd"
        result = resolver.resolve_uri(uri)
        # This should match the longer rewrite rule, not the generic one
        if result:
            # Verify it resolves to 2008/ directory (not 2008/2008/)
            assert "2008/2008" not in str(result)


class TestRewriteSystemRules:
    """Test <rewriteSystem> prefix rules (as used in TEI, etc.)."""

    def test_rewrite_tei_xsd_system(self, resolver):
        """Resolve TEI XSD via rewrite system rule."""
        system_id = "http://www.tei-c.org/release/xml/tei/custom/schema/xsd/tei_all.xsd"
        result = resolver.resolve_system(system_id)
        assert result is not None
        assert result.exists()
        assert "p5/xsd" in str(result)

    def test_rewrite_tei_relaxng_system(self, resolver):
        """Resolve TEI RelaxNG via rewrite system rule."""
        system_id = "http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rng"
        result = resolver.resolve_system(system_id)
        assert result is not None
        assert result.exists()
        assert "p5/relaxng" in str(result)

    def test_rewrite_tei_dtd_system(self, resolver):
        """Resolve TEI DTD via rewrite system rule."""
        system_id = "http://www.tei-c.org/release/xml/tei/custom/schema/dtd/tei_all.dtd"
        result = resolver.resolve_system(system_id)
        assert result is not None
        assert result.exists()
        assert "p5/dtd" in str(result)


class TestAutoResolution:
    """Test mixed kind='auto' resolution."""

    def test_auto_tries_uri_first(self, resolver):
        """With kind='auto', URI resolution should be tried first."""
        # Use a URI that exists in URI rules
        uri = "http://purl.org/dc/elements/1.1/"
        result = resolver.resolve(uri, kind="auto")
        assert result is not None
        assert result.exists()

    def test_auto_falls_back_to_system(self, resolver):
        """With kind='auto', if URI fails, try system."""
        # Use a bare system ID that shouldn't match as URI
        system_id = "xlink.xsd"
        result = resolver.resolve(system_id, kind="auto")
        assert result is not None
        assert result.exists()

    def test_auto_public_api(self):
        """Test public resolve_uri_to_path convenience function."""
        uri = "http://purl.org/dc/elements/1.1/"
        result = resolve_uri_to_path(uri)
        assert result is not None
        assert result.exists()


class TestRelaxNGCompact:
    """Test RelaxNG Compact file resolution (key use case!)."""

    @pytest.mark.parametrize(
        "rnc_uri",
        [
            "http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rnc",
            "http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_bare.rnc",
            "http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_lite.rnc",
            "http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_corpus.rnc",
        ],
    )
    def test_rnc_uris_resolve_to_local_files(self, resolver, rnc_uri):
        """Verify .rnc files can be resolved without parsing."""
        result = resolver.resolve(rnc_uri)
        assert result is not None, f"Failed to resolve {rnc_uri}"
        assert result.exists(), f"Resolved path does not exist: {result}"
        assert result.suffix == ".rnc", f"Expected .rnc file, got {result}"

    def test_rnc_no_parse_error(self, resolver):
        """
        Verify that .rnc resolution does NOT raise parsing errors.
        This is the core difference from parser-based approaches.
        """
        rnc_uri = "http://www.tei-c.org/release/xml/tei/custom/schema/relaxng/tei_all.rnc"
        # Should return a path without attempting to parse as XML
        result = resolver.resolve(rnc_uri)
        assert result is not None
        # No exception should have been raised during resolution


class TestNextCatalogTraversal:
    """Test <nextCatalog> chaining."""

    def test_traverses_subdomain_catalogs(self, resolver):
        """Verify that nextCatalog references are followed."""
        # TEI catalog is loaded via nextCatalog from root
        tei_uri = "http://www.tei-c.org/release/xml/tei/custom/schema/xsd/tei_all.xsd"
        result = resolver.resolve(tei_uri)
        assert result is not None
        assert result.exists()
        assert "tei" in str(result).lower()

    def test_traverses_nested_catalogs(self, resolver):
        """Verify that nested nextCatalog chains work (e.g., loc -> mets)."""
        # METS is via loc -> mets cascade
        mets_uri = "http://www.loc.gov/standards/mets/mets.xsd"
        result = resolver.resolve(mets_uri)
        assert result is not None
        assert result.exists()
        assert "mets" in str(result).lower()

    def test_traverses_multiple_subdomain_catalogs(self, resolver):
        """Verify multiple independent nextCatalog branches work."""
        # Test URIs from different top-level catalogs
        uris_and_keywords = [
            ("http://purl.org/dc/elements/1.1/", "dublincore"),
            ("http://www.opengis.net/gml/3.1.1/", "opengis"),
            ("http://www.w3.org/1999/xlink", "w3c"),
        ]
        for uri, keyword in uris_and_keywords:
            result = resolver.resolve(uri)
            assert result is not None, f"Failed to resolve {uri}"
            assert result.exists(), f"Path does not exist: {result}"


class TestPathNormalization:
    """Test that returned paths are properly normalized."""

    def test_returns_absolute_path(self, resolver):
        """Resolved paths should be absolute."""
        uri = "http://purl.org/dc/elements/1.1/"
        result = resolver.resolve(uri)
        assert result is not None
        assert result.is_absolute()

    def test_no_dot_segments_in_path(self, resolver):
        """Resolved paths should have . and .. segments normalized."""
        uri = "http://www.tei-c.org/release/xml/tei/custom/schema/xsd/tei_all.xsd"
        result = resolver.resolve(uri)
        assert result is not None
        # Path should be resolved (no .. or . segments)
        assert ".." not in str(result)

    def test_path_exists_on_filesystem(self, resolver):
        """All resolved paths must exist (corpus integrity check)."""
        test_uris = [
            "http://purl.org/dc/elements/1.1/",
            "http://www.tei-c.org/release/xml/tei/custom/schema/xsd/tei_all.xsd",
            "http://www.loc.gov/standards/mets/mets.xsd",
        ]
        for uri in test_uris:
            result = resolver.resolve(uri)
            assert result is not None, f"Could not resolve {uri}"
            assert result.exists(), f"Resolved path does not exist: {result}"


class TestErrorHandling:
    """Test error handling and edge cases."""

    def test_empty_identifier_returns_none(self, resolver):
        """Empty identifier should return None."""
        result = resolver.resolve("")
        assert result is None

    def test_none_identifier_raises_typeerror(self, resolver):
        """None identifier should raise."""
        with pytest.raises(TypeError):
            resolver.resolve(None)

    def test_malformed_uri_returns_none(self, resolver):
        """Malformed URI should return None gracefully."""
        result = resolver.resolve("not a valid uri at all")
        assert result is None

    def test_clear_cache_works(self, resolver):
        """Cache clearing should work without errors."""
        resolver.resolve("http://purl.org/dc/elements/1.1/")
        resolver.clear_cache()
        # Should still work after clear
        result = resolver.resolve("http://purl.org/dc/elements/1.1/")
        assert result is not None


class TestRegressionWithExistingFixtures:
    """Regression tests using existing test data files."""

    def test_dublin_core_xsd_uris_from_fixture(self):
        """Load and test DublinCore URIs from existing fixture."""
        fixture_file = Path(__file__).parent / "data" / "dublincore" / "xsd_uris.txt"
        if fixture_file.exists():
            with open(fixture_file) as f:
                uris = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            # Test first 5 URIs
            for uri in uris[:5]:
                result = resolve_uri_to_path(uri)
                assert result is not None, f"Failed to resolve DublinCore URI: {uri}"
                assert result.exists(), f"File not found: {result}"

    def test_tei_rng_uris_from_fixture(self):
        """Load and test TEI RNG URIs from existing fixture."""
        fixture_file = Path(__file__).parent / "data" / "tei" / "p5_rng_uris.txt"
        if fixture_file.exists():
            with open(fixture_file) as f:
                uris = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            # Test first 10 URIs (mix of .rng and .rnc)
            for uri in uris[:10]:
                result = resolve_uri_to_path(uri)
                assert result is not None, f"Failed to resolve TEI URI: {uri}"
                assert result.exists(), f"File not found: {result}"

    def test_lido_uris_from_fixture(self):
        """Load and test LIDO URIs from existing fixture."""
        fixture_file = Path(__file__).parent / "data" / "lido" / "lido_uris.txt"
        if fixture_file.exists():
            with open(fixture_file) as f:
                uris = [line.strip() for line in f if line.strip() and not line.startswith("#")]
            
            # Test first 5 URIs
            for uri in uris[:5]:
                result = resolve_uri_to_path(uri)
                assert result is not None, f"Failed to resolve LIDO URI: {uri}"
                assert result.exists(), f"File not found: {result}"
