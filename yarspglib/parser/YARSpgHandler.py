import json
import urllib.parse
from antlr4.tree.Tree import TerminalNodeImpl
from rdflib import URIRef, Literal
from yarspglib.parser.YARSpgParser import YARSpgParser


class YARSpgHandler:
    def __init__(self, graph):
        self.graph = graph
        self.nodes = {}

    def process_node(self, node):
        if isinstance(node, YARSpgParser.NodeContext):
            n_id = node.node_id().getText()
            n_type = node.node_label()[0].getText().strip("\"")
            n_props = node.prop_list().getText()
            n_props = self.process_node_props(n_props)
            self.nodes[n_id] = {'type': n_type, 'properties': n_props}

    def process_edge(self, edge):
        if isinstance(edge, YARSpgParser.EdgeContext):
            if edge.directed() is not None:
                sid = edge.directed().node_id()[0].getText()
                oid = edge.directed().node_id()[1].getText()
                e_label = edge.directed().edge_label()[0].getText()
                e_props = edge.directed().prop_list().getText()

            if edge.undirected() is not None:
                sid = edge.undirected().node_id()[0].getText()
                oid = edge.undirected().node_id()[1].getText()
                e_label = edge.undirected().edge_label()[0].getText()
                e_props = edge.undirected().prop_list().getText()

            predicate = self.process_edge_props(e_props)
            if e_label.strip("\"") == 'IRI':
                self.graph.add((self.match_type(sid), URIRef(self.encode_uri(predicate)),
                                self.match_type(oid)))

    def match_type(self, element_id):
        obj = self.nodes.get(element_id)
        if obj:
            properties = obj.get('properties', {})
            value = properties.get('@value')
            datatype = properties.get('@datatype')
            lang = properties.get('@lang')
            if obj['type'] == 'Literal':
                return Literal(value, datatype=datatype, lang=lang)
            else:
                return URIRef(self.encode_uri(value)) if value else None
        return None

    def encode_uri(self, uri: str) -> str:
        if uri:
            return urllib.parse.quote(uri, safe=":/#")
        return uri

    def process_node_props(self, props_data):
        props_data = props_data.strip("[]")
        try:
            props_dict = json.loads("{" + props_data + "}")
        except json.JSONDecodeError as e:
            print(f"Properties decoding error: {e}")
            print(f"Invalid properties: {props_data}")
            props_dict = {}
        props = {}
        for key, value in props_dict.items():
            props[key] = value
        return props

    def process_edge_props(self, props_data):
        props_data = props_data.strip("[]")
        props_dict = json.loads("{" + props_data + "}")
        return props_dict['@value']

    def traverse_tree(self, tree):
        if isinstance(tree, TerminalNodeImpl):
            return
        for child in tree.getChildren():
            if isinstance(child, YARSpgParser.NodeContext):
                self.process_node(child)
            if isinstance(child, YARSpgParser.EdgeContext):
                self.process_edge(child)
            self.traverse_tree(child)
