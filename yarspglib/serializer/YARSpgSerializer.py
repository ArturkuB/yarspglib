from typing import IO, Optional
from rdflib import URIRef, Literal, Graph
from rdflib.serializer import Serializer
from rdflib.term import Node
from tqdm import tqdm


class YARSpgSerializer(Serializer):
    """
    Serializes RDF graphs to YARS-PG format.
    """

    def __init__(self, store: Graph):
        super().__init__(store)
        self.nodes = {}
        self.edges = []
        self.node_map = {}
        self.subject_counter = 1
        self.object_counter = 1
        self.datatype_counter = 1
        self.lang_counter = 1

    def serialize(
            self,
            stream: IO[bytes],
            base: Optional[str] = None,
            encoding: Optional[str] = "utf-8",
            **args,
    ) -> None:

        total_iterations = len(self.store)

        for triple in tqdm(self.store, total=total_iterations, desc="Processing"):
            subject, predicate, obj = triple
            self.serialize_triple(subject, predicate, obj)

        self.serialize_nodes(stream)
        self.serialize_edges(stream)

    def serialize_triple(
            self,
            subject: Node,
            predicate: Node,
            obj: Node
    ) -> None:
        sid = self.get_or_create_node(subject, is_subject=True)
        oid = self.get_or_create_node(obj, is_subject=False)
        self.edges.append((sid, predicate, oid))

    def get_or_create_node(self, node: Node, is_subject: bool) -> str:
        if node in self.node_map:
            return self.node_map[node]

        if is_subject:
            node_id = f"s{self.subject_counter}"
            self.subject_counter += 1
        else:
            node_id = f"o{self.object_counter}"
            self.object_counter += 1

        node_type = self.typeOf(node)
        if node_type == 'IRI':
            self.createNode(node_id, 'IRI', node)
        elif node_type == 'BNode':
            self.createNode(node_id, 'BNode', node)
        else:
            lang = getattr(node, 'language', None)
            datatype = getattr(node, 'datatype', None)
            if lang is not None:
                self.lang_counter += 1
            if datatype is not None:
                self.datatype_counter += 1

            self.createNode(node_id, 'Literal', node, datatype, lang)

        self.node_map[node] = node_id
        return node_id

    def createNode(self, node_id: str, node_type: str, value: Node, datatype: Optional[str] = None,
                   lang: Optional[str] = None) -> None:
        node_data = {"type": node_type, "value": value}
        if node_type == 'Literal':
            node_data['datatype'] = datatype
            node_data['lang'] = lang
        self.nodes[node_id] = node_data

    def serialize_nodes(self, stream: IO[bytes]) -> None:
        """
        Serialize all nodes. Add `# Nodes` in the beginning.
        """
        stream.write(b"# Nodes\n")
        for node_id, node_data in self.nodes.items():
            node_type = node_data['type']
            value = node_data['value']
            if node_type == 'IRI':
                node_str = f"({node_id} {{\"IRI\"}} [{self.serialize_value(value)}])\n"
            elif node_type == 'Literal':
                node_str = f"({node_id} {{\"Literal\"}} [{self.serialize_value(value)}])\n"
            else:
                node_str = f"({node_id} {{\"BNode\"}} [{self.serialize_value(value)}])\n"
            stream.write(node_str.encode("utf-8"))

    def serialize_edges(self, stream: IO[bytes]) -> None:
        """
        Serialize all edges. Add `# Edges` in the beginning.
        """
        stream.write(b"# Edges\n")
        for source_id, predicate, destination_id in self.edges:
            edge_str = f"({source_id})-({self._serialize_predicate(predicate)})->({destination_id})\n"
            stream.write(edge_str.encode("utf-8"))
        print('Numer of nodes:', len(self.nodes))
        print('Number of edges:', len(self.edges))

    def serialize_value(self, value: Node) -> str:
        """
        Serialize the value of the node or edge.
        """
        if isinstance(value, URIRef):
            return f"\"@value\": \"{value}\""

        serialized_value = f"\"@value\": \"{value}\""
        if isinstance(value, Literal):
            if isinstance(value.value, str):
                value_str = value.value
                value_str = value_str.replace("\\", "\\\\").replace("\n", "\\n").replace("\"", "\\\"")
            else:
                value_str = value.value
            serialized_value = f"\"@value\": \"{value_str}\""
            if value.datatype:
                serialized_value += f", \"@datatype\": \"{value.datatype}\""
            if value.language:
                serialized_value += f", \"@lang\": \"{value.language}\""
        return serialized_value

    def _serialize_predicate(self, predicate: Node) -> str:
        """
        Serialize the predicate of the edge.
        """
        return f"{{\"IRI\"}} [{self.serialize_value(predicate)}]"

    def typeOf(self, node: Node) -> str:
        """
        Determine the type of the node (IRI, Literal, Blank Node).
        """
        if isinstance(node, URIRef):
            return 'IRI'
        elif isinstance(node, Literal):
            return 'Literal'
        else:
            return 'BNode'
