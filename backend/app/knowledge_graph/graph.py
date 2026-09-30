"""
Knowledge Graph – NetworkX-based entity-relationship graph.
"""

import logging
from typing import List, Optional
import networkx as nx

logger = logging.getLogger(__name__)

# Seed knowledge for demo
SEED_TRIPLES = [
    ("Elon Musk", "CO_FOUNDED", "Tesla"),
    ("Tesla", "FOUNDED_IN", "2003"),
    ("Tesla", "HEADQUARTERED_IN", "Austin, Texas"),
    ("Martin Eberhard", "CO_FOUNDED", "Tesla"),
    ("Elon Musk", "CEO_OF", "SpaceX"),
    ("Elon Musk", "BORN_IN", "Pretoria, South Africa"),
    ("Albert Einstein", "DEVELOPED", "Special Relativity"),
    ("Albert Einstein", "DEVELOPED", "General Relativity"),
    ("Albert Einstein", "BORN_IN", "Ulm, Germany"),
    ("Albert Einstein", "WON", "Nobel Prize in Physics"),
    ("Eiffel Tower", "LOCATED_IN", "Paris"),
    ("Eiffel Tower", "BUILT_IN", "1889"),
    ("Eiffel Tower", "DESIGNED_BY", "Gustave Eiffel"),
    ("Python", "CREATED_BY", "Guido van Rossum"),
    ("Python", "FIRST_RELEASED", "1991"),
    ("ChatGPT", "DEVELOPED_BY", "OpenAI"),
    ("ChatGPT", "LAUNCHED_IN", "2022"),
    ("OpenAI", "HEADQUARTERED_IN", "San Francisco"),
]

NODE_TYPES = {
    "Elon Musk": "PERSON", "Martin Eberhard": "PERSON", "Albert Einstein": "PERSON",
    "Guido van Rossum": "PERSON", "Gustave Eiffel": "PERSON",
    "Tesla": "ORGANIZATION", "SpaceX": "ORGANIZATION", "OpenAI": "ORGANIZATION",
    "ChatGPT": "PRODUCT", "Python": "PRODUCT", "Eiffel Tower": "PLACE",
    "Paris": "PLACE", "Austin, Texas": "PLACE", "Ulm, Germany": "PLACE",
    "Pretoria, South Africa": "PLACE", "San Francisco": "PLACE",
    "2003": "DATE", "1889": "DATE", "1991": "DATE", "2022": "DATE",
    "Special Relativity": "CONCEPT", "General Relativity": "CONCEPT",
    "Nobel Prize in Physics": "AWARD",
}


class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.DiGraph()
        self._load_seed()

    def _load_seed(self):
        for subj, pred, obj in SEED_TRIPLES:
            self.graph.add_node(subj, type=NODE_TYPES.get(subj, "ENTITY"), label=subj)
            self.graph.add_node(obj, type=NODE_TYPES.get(obj, "ENTITY"), label=obj)
            self.graph.add_edge(subj, obj, relation=pred, weight=1.0)
        logger.info(f"Knowledge graph loaded: {self.graph.number_of_nodes()} nodes, {self.graph.number_of_edges()} edges")

    def add_triple(self, subject: str, predicate: str, obj: str, node_type: str = "ENTITY"):
        self.graph.add_node(subject, type=node_type, label=subject)
        self.graph.add_node(obj, type=NODE_TYPES.get(obj, node_type), label=obj)
        self.graph.add_edge(subject, obj, relation=predicate)

    def get_graph_data(self) -> dict:
        nodes = []
        for node, attrs in self.graph.nodes(data=True):
            nodes.append({
                "id": node,
                "label": attrs.get("label", node),
                "type": attrs.get("type", "ENTITY"),
                "properties": {k: v for k, v in attrs.items() if k not in ("label", "type")},
            })

        edges = []
        for src, tgt, attrs in self.graph.edges(data=True):
            edges.append({
                "source": src,
                "target": tgt,
                "relation": attrs.get("relation", "RELATED_TO"),
                "weight": attrs.get("weight", 1.0),
                "properties": {},
            })

        return {
            "nodes": nodes,
            "edges": edges,
            "total_nodes": self.graph.number_of_nodes(),
            "total_edges": self.graph.number_of_edges(),
        }

    def query_neighbors(self, entity: str, depth: int = 2) -> dict:
        """Get subgraph around an entity up to `depth` hops."""
        if entity not in self.graph:
            return {"nodes": [], "edges": [], "total_nodes": 0, "total_edges": 0}

        subgraph_nodes = {entity}
        frontier = {entity}
        for _ in range(depth):
            new_frontier = set()
            for n in frontier:
                new_frontier.update(self.graph.successors(n))
                new_frontier.update(self.graph.predecessors(n))
            subgraph_nodes.update(new_frontier)
            frontier = new_frontier

        sub = self.graph.subgraph(subgraph_nodes)
        nodes = [
            {"id": n, "label": d.get("label", n), "type": d.get("type", "ENTITY"), "properties": {}}
            for n, d in sub.nodes(data=True)
        ]
        edges = [
            {"source": u, "target": v, "relation": d.get("relation", ""), "weight": 1.0, "properties": {}}
            for u, v, d in sub.edges(data=True)
        ]
        return {"nodes": nodes, "edges": edges, "total_nodes": len(nodes), "total_edges": len(edges)}


# Singleton
knowledge_graph = KnowledgeGraph()
