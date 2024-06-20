from rdflib import Graph
from yarspglib.parser.YARSpgHandler import YARSpgHandler
from yarspglib.parser.YARSpgLexer import YARSpgLexer
from yarspglib.parser.YARSpgParser import YARSpgParser
from antlr4 import *


class YARSpgProcessor:
    def __init__(self):
        self.graph = Graph()

    def process_YARSpg(self, data):
        input_stream = InputStream(data)
        lexer = YARSpgLexer(input_stream)
        stream = CommonTokenStream(lexer)
        parser = YARSpgParser(stream)
        tree = parser.yarspg()
        handler = YARSpgHandler(self.graph)
        handler.traverse_tree(tree)
