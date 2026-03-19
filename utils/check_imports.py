"""

This script analyzes an XSD and builds a dependency graph.

It identifies all imports and includes, resolves their URIs, and checks for
issues like circular dependencies and namespace conflicts.

Usage: check_imports.py <start-schema-uri>
"""

import argparse
import sys
import xml.etree.ElementTree as ET
from urllib.parse import urljoin

import requests


def parse_args():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Analyze XSD imports and includes.")
    parser.add_argument(
        "start_uri",
        help="The URI of the starting XSD schema (can be a local file path or an HTTP URL).",
    )
    return parser.parse_args()


def fetch_xsd(uri: str) -> bytes:
    """Read the XSD content from a URI or a local file.

    Return content as bytes.
    """
    if uri.startswith("http"):
        resp = requests.get(uri, timeout=10)
        resp.raise_for_status()
        data = resp.content
    else:
        with open(uri, "rb") as f:
            data = f.read()
    return data


def parse_imports(xsd_bytes: bytes, base_uri: str):
    """
    Parse the imports from the XSD bytes to a list of imports.

    Each entry in the list returne is a tuple consisting of targetNamespace and
    resolved_schemaLocation).
    """
    ns_xs = {"xs": "http://www.w3.org/2001/XMLSchema"}
    root = ET.fromstring(xsd_bytes)
    imports = []
    for im in root.findall(".//xs:import", ns_xs):
        ns_ = im.attrib.get("namespace", "").strip()
        loc_ = im.attrib.get("schemaLocation")
        if not loc_:
            # skip imports without location
            continue
        # relative to absolute
        real_loc = urljoin(base_uri, loc_)
        imports.append((ns_, real_loc))
    return imports


def build_import_graph(start_uri: str):
    """
    Recursively builds the import graph starting from 'start_uri'.
    Graph: Dict[uri, List[(namespace, schemaLocation_uri)]]
    """
    graph = {}
    visited = set()

    def _rec(uri):
        if uri in visited:
            print(
                "Detected cyclic import: {uri} has already been visited. "
                "Skipping further processing of this node.",
                file=sys.stderr,
            )
            return
        visited.add(uri)
        try:
            data = fetch_xsd(uri)
        except Exception as e:
            print(f"ERROR when loading {uri}: {e}", file=sys.stderr)
            graph[uri] = []
            return

        imports = parse_imports(data, uri)
        graph[uri] = imports
        for _, child_uri in imports:
            _rec(child_uri)

    _rec(start_uri)
    return graph


def collect_paths(graph, start_uri):
    """Detect all (simple) paths from start_uri to any other node."""
    paths = {}

    def _dfs(current, path, seen):
        # current: current node, path: list of nodes detected so far
        for _, nxt in graph.get(current, []):
            if nxt in seen:
                continue
            new_path = path + [nxt]
            paths.setdefault(nxt, []).append(new_path)
            _dfs(nxt, new_path, seen | {nxt})

    _dfs(start_uri, [start_uri], {start_uri})
    return paths


def canonical_cycle(cycle):
    """Returns a canonical tuple representation of a cycle [A,B,C,A].
    The canonical form is the lexicographically smallest tuple, such
    that rotations of the same cycle appear only once in the set.
    """
    # Remove the last element (repetition of the first)
    nodes = cycle[:-1]
    # create all rotations
    rots = [tuple(nodes[i:] + nodes[:i]) for i in range(len(nodes))]
    # select the lexicographically smallest rotation
    min_rot = min(rots)
    # append the start node at the end to close the cycle
    return min_rot + (min_rot[0],)


def find_circular_imports(graph):
    """
    Finds all directed cycles in the graph.
    The graph is represented as Dict[src_uri, List[(namespace, target_uri)] ].
    Return value: A list of cycles, where each cycle is a List[uri1, uri2, ..., uri1].
    """
    unique_cycles = set()

    def dfs(path):
        current = path[-1]
        for _, nxt in graph.get(current, []):
            if nxt in path:
                # Cycle found
                idx = path.index(nxt)
                cycle = path[idx:] + [nxt]
                unique_cycles.add(canonical_cycle(cycle))
            else:
                dfs(path + [nxt])

    # Start DFS of each node
    for node in graph:
        dfs([node])

    # cast tuples back to lists
    return [list(cyc) for cyc in unique_cycles]


def find_namespace_conflicts_with_sources(graph):
    """
    Collects all imported namespaces and checks whether there is more
    than one (different) schemaLocation for each one.

    Returns Dict[
               namespace,
               Dict[
                 schemaLocation_uri,
                 Set[src_schema_uri]
               ]
             ]
    """
    ns_map = {}
    for src_, imports in graph.items():
        for ns_, loc_ in imports:
            # create a dict for each namespace:  loc → set(src)
            ns_map.setdefault(ns_, {}).setdefault(loc_, set()).add(src_)

    # filter only namespaces that appear in multiple different locations
    return {ns: locs for ns, locs in ns_map.items() if len(locs) > 1}


if __name__ == "__main__":
    args = parse_args()
    print(f"Creating the import graph starting from {args.start_uri} ...")
    G = build_import_graph(args.start_uri)

    print("\nGraph (per source → list of imports):")
    for src, imps in G.items():
        print(f" {src}:")
        for ns, loc in imps:
            print(f"    ↳ namespace={ns!r}, location={loc}")

    print("\nAll reachable paths:")
    all_paths = collect_paths(G, args.start_uri)
    for target, pls in all_paths.items():
        for p in pls:
            print("  " + " → ".join(p))

    print("\nNamespace conflicts (same namespace, different locations):")
    conflicts = find_namespace_conflicts_with_sources(G)
    if not conflicts:
        print("  No conflicts found.")
    else:
        for ns, locs in conflicts.items():
            print(f"  Namespace {ns!r} imported from {len(locs)} different locations:")
            for loc, src_schemas in locs.items():
                print(
                    f"    - schemaLocation = {loc!r}, imported in {len(src_schemas)} schema(s):"
                )
                for src in src_schemas:
                    print(f"        • source: {src}")

    # Report circular imports
    print("\nCircular imports (cycles) in graph:")
    cycles = find_circular_imports(G)
    if not cycles:
        print("  No cycles found.")
    else:
        for cyc in cycles:
            print("  " + " → ".join(cyc))
