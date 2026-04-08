"""
Graph Analytics Engine — Sprint 73.

All functions operate on pre-fetched edge data (list of tuples) to keep
DB access in the caller and analytics logic pure and testable.

Public API
----------
fetch_edges(db)                   → list[tuple[int, int, str, float]]
degree_centrality(entity_id, edges) → dict
pagerank(edges, damping, max_iter, tol) → dict[int, float]
connected_components(edges)       → dict[int, int]  (node → component_id)
component_sizes(components)       → dict[int, int]  (component_id → size)
detect_communities(edges)         → dict[int, int]  (node → community_id)
community_summaries(edges, communities) → list[dict]
shortest_path(source, target, edges) → dict | None
"""
from __future__ import annotations
from collections import defaultdict, deque
from sqlalchemy.orm import Session
from backend import models
from backend.tenant_access import scope_query_to_org


EdgeList = list[tuple[int, int, str, float]]  # (source_id, target_id, relation_type, weight)


# ── Data fetching ─────────────────────────────────────────────────────────────

def fetch_edges(db: Session, org_id: int | None = None) -> EdgeList:
    """Load all edges from DB as a flat list of (src, dst, rel_type, weight)."""
    rows = scope_query_to_org(
        db.query(
            models.EntityRelationship.source_id,
            models.EntityRelationship.target_id,
            models.EntityRelationship.relation_type,
            models.EntityRelationship.weight,
        ),
        models.EntityRelationship,
        org_id,
    ).all()
    return [(r[0], r[1], r[2], r[3]) for r in rows]


# ── Degree Centrality ────────────────────────────────────────────────────────

def degree_centrality(entity_id: int, edges: EdgeList) -> dict:
    """
    Return in-degree, out-degree, and per-relation-type breakdown for one entity.
    """
    out_by_type: dict[str, int] = defaultdict(int)
    in_by_type:  dict[str, int] = defaultdict(int)

    for src, dst, rel, _ in edges:
        if src == entity_id:
            out_by_type[rel] += 1
        if dst == entity_id:
            in_by_type[rel] += 1

    out_degree = sum(out_by_type.values())
    in_degree  = sum(in_by_type.values())

    return {
        "in_degree":       in_degree,
        "out_degree":      out_degree,
        "total_degree":    in_degree + out_degree,
        "in_by_type":      dict(in_by_type),
        "out_by_type":     dict(out_by_type),
    }


# ── PageRank ────────────────────────────────────────────────────────────────

def pagerank(
    edges: EdgeList,
    damping: float = 0.85,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> dict[int, float]:
    """
    Simplified PageRank (directed).
    Returns {node_id: score} normalised so scores sum to 1.0.
    Returns {} when the graph is empty.
    """
    nodes: set[int] = set()
    out_neighbors: dict[int, list[int]] = defaultdict(list)
    in_neighbors:  dict[int, list[int]] = defaultdict(list)

    for src, dst, _, _ in edges:
        nodes.add(src)
        nodes.add(dst)
        out_neighbors[src].append(dst)
        in_neighbors[dst].append(src)

    N = len(nodes)
    if N == 0:
        return {}

    rank: dict[int, float] = {n: 1.0 / N for n in nodes}

    for _ in range(max_iter):
        new_rank: dict[int, float] = {}
        for n in nodes:
            r = (1.0 - damping) / N
            for pred in in_neighbors.get(n, []):
                out_deg = len(out_neighbors.get(pred, []))
                if out_deg > 0:
                    r += damping * rank[pred] / out_deg
            new_rank[n] = r

        diff = sum(abs(new_rank[n] - rank[n]) for n in nodes)
        rank = new_rank
        if diff < tol:
            break

    # Normalise
    total = sum(rank.values()) or 1.0
    return {n: round(v / total, 6) for n, v in rank.items()}


# ── Connected Components (weakly connected, treats edges as undirected) ───────

def connected_components(edges: EdgeList) -> dict[int, int]:
    """
    Return {node_id: component_id} for weakly connected components.
    Uses iterative BFS to avoid Python recursion limits on large graphs.
    """
    adj: dict[int, set[int]] = defaultdict(set)
    nodes: set[int] = set()

    for src, dst, _, _ in edges:
        adj[src].add(dst)
        adj[dst].add(src)
        nodes.add(src)
        nodes.add(dst)

    visited: dict[int, int] = {}
    comp_id = 0

    for node in nodes:
        if node in visited:
            continue
        queue: deque[int] = deque([node])
        while queue:
            curr = queue.popleft()
            if curr in visited:
                continue
            visited[curr] = comp_id
            for neighbor in adj[curr]:
                if neighbor not in visited:
                    queue.append(neighbor)
        comp_id += 1

    return visited


def component_sizes(components: dict[int, int]) -> dict[int, int]:
    """Return {component_id: size} from the components mapping."""
    sizes: dict[int, int] = defaultdict(int)
    for comp_id in components.values():
        sizes[comp_id] += 1
    return dict(sizes)


def detect_communities(
    edges: EdgeList,
    max_iter: int = 25,
) -> dict[int, int]:
    """
    Lightweight deterministic label-propagation over an undirected projection.
    Good enough for medium subgraphs without extra dependencies.
    """
    adj: dict[int, dict[int, float]] = defaultdict(dict)
    nodes: set[int] = set()

    for src, dst, _, weight in edges:
        w = float(weight or 1.0)
        adj[src][dst] = adj[src].get(dst, 0.0) + w
        adj[dst][src] = adj[dst].get(src, 0.0) + w
        nodes.add(src)
        nodes.add(dst)

    if not nodes:
        return {}

    labels = {node: node for node in nodes}

    for _ in range(max_iter):
        changed = False
        for node in sorted(nodes):
            neighbor_weights = adj.get(node, {})
            if not neighbor_weights:
                continue

            scores: dict[int, float] = defaultdict(float)
            for neighbor, weight in neighbor_weights.items():
                scores[labels[neighbor]] += weight

            best_label = min(
                (label for label, score in scores.items() if score == max(scores.values())),
                default=labels[node],
            )
            if best_label != labels[node]:
                labels[node] = best_label
                changed = True
        if not changed:
            break

    normalized: dict[int, int] = {}
    label_map: dict[int, int] = {}
    for node in sorted(nodes):
        original = labels[node]
        if original not in label_map:
            label_map[original] = len(label_map)
        normalized[node] = label_map[original]
    return normalized


def community_summaries(edges: EdgeList, communities: dict[int, int]) -> list[dict]:
    """Summarise communities by size, density, leader, and relation mix."""
    if not communities:
        return []

    members: dict[int, set[int]] = defaultdict(set)
    internal_edges: dict[int, int] = defaultdict(int)
    relation_mix: dict[int, dict[str, int]] = defaultdict(lambda: defaultdict(int))
    degree_map: dict[int, int] = defaultdict(int)

    for node_id, community_id in communities.items():
        members[community_id].add(node_id)

    for src, dst, rel, _ in edges:
        degree_map[src] += 1
        degree_map[dst] += 1
        src_comm = communities.get(src)
        dst_comm = communities.get(dst)
        if src_comm is not None and src_comm == dst_comm:
            internal_edges[src_comm] += 1
            relation_mix[src_comm][rel] += 1

    summaries = []
    for community_id, entity_ids in members.items():
        size = len(entity_ids)
        possible_edges = max((size * (size - 1)) / 2, 1)
        density = round(internal_edges[community_id] / possible_edges, 3) if size > 1 else 0.0
        leader_id = max(
            entity_ids,
            key=lambda node_id: (degree_map.get(node_id, 0), -node_id),
        )
        relation_breakdown = relation_mix[community_id]
        top_relations = sorted(
            relation_breakdown.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:3]

        summaries.append({
            "community_id": community_id,
            "size": size,
            "internal_edges": internal_edges[community_id],
            "density": density,
            "entity_ids": sorted(entity_ids),
            "leader_id": leader_id,
            "leader_degree": degree_map.get(leader_id, 0),
            "top_relations": [
                {"relation_type": rel, "count": count}
                for rel, count in top_relations
            ],
        })

    return sorted(summaries, key=lambda item: (item["size"], item["internal_edges"]), reverse=True)


# ── Shortest Path (BFS, directed) ────────────────────────────────────────────

def shortest_path(
    source: int,
    target: int,
    edges: EdgeList,
) -> dict | None:
    """
    BFS shortest path (directed). Returns None if no path exists.

    Returns:
        {
            "path":      [source_id, ..., target_id],
            "relations": ["cites", ...],   # len = len(path) - 1
            "length":    int,
        }
    """
    if source == target:
        return {"path": [source], "relations": [], "length": 0}

    adj: dict[int, list[tuple[int, str]]] = defaultdict(list)
    for src, dst, rel, _ in edges:
        adj[src].append((dst, rel))

    # BFS: queue items are (current_node, path_so_far, relations_so_far)
    queue: deque[tuple[int, list[int], list[str]]] = deque(
        [(source, [source], [])]
    )
    visited: set[int] = {source}

    while queue:
        curr, path, rels = queue.popleft()
        for neighbor, rel in adj.get(curr, []):
            if neighbor in visited:
                continue
            new_path = path + [neighbor]
            new_rels = rels + [rel]
            if neighbor == target:
                return {
                    "path":      new_path,
                    "relations": new_rels,
                    "length":    len(new_path) - 1,
                }
            visited.add(neighbor)
            queue.append((neighbor, new_path, new_rels))

    return None  # unreachable
