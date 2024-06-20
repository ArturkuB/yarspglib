import argparse
from yarspglib.yarspg_operations_handler import (
    serialize_rdf_to_yarspg, parse_yarspg,
    compress_file, decompress_file, combine_sections, split_yarspg
)

class CommandLineInterface:
    """A class to handle the command line interface."""

    def __init__(self):
        """Inits CommandLineInterface and parses the arguments."""
        self.args = self._parse_args()

    @staticmethod
    def _parse_args():
        """Parses the command line arguments.

        Returns:
            Namespace: The parsed arguments.
        """
        parser = argparse.ArgumentParser(
            description="This program processes files in RDF and YARS-PG formats, facilitating serialization and parsing between them. It also includes options for compressing files (gzip, brotli, zstandard, snappy) post-serialization and decompressing them pre-parsing",
            prog='yarspglib'
        )

        subparsers = parser.add_subparsers(dest='action', required=True, help='Action to perform: serialize or parse.')

        serialize_parser = subparsers.add_parser('serialize', help='Serialize RDF to YARS-PG.')
        serialize_subparsers = serialize_parser.add_subparsers(dest='type', required=True, help='Type of serialization: wholefile or sections.')

        serialize_wholefile_parser = serialize_subparsers.add_parser('wholefile', help='Serialize entire RDF file to YARS-PG.')
        serialize_wholefile_parser.add_argument('input', type=str, help='Input RDF file.')
        serialize_wholefile_parser.add_argument('output', type=str, help='Output YARS-PG file.')
        serialize_wholefile_parser.add_argument('--compression', type=str, choices=['gzip', 'brotli', 'zstd', 'snappy'], help='Compression method.')
        serialize_wholefile_parser.add_argument('-l', '--level', type=int, help='Compression level (only for gzip, brotli, zstd).')

        serialize_sections_parser = serialize_subparsers.add_parser('sections', help='Serialize RDF file to YARS-PG with separate nodes and edges sections.')
        serialize_sections_parser.add_argument('input', type=str, help='Input RDF file.')
        serialize_sections_parser.add_argument('--output-nodes', type=str, required=True, help='Output YARS-PG file for nodes.')
        serialize_sections_parser.add_argument('--output-edges', type=str, required=True, help='Output YARS-PG file for edges.')
        serialize_sections_parser.add_argument('--compression', type=str, choices=['gzip', 'brotli', 'zstd', 'snappy'], help='Compression method.')
        serialize_sections_parser.add_argument('-l', '--level', type=int, help='Compression level (only for gzip, brotli, zstd).')

        parse_parser = subparsers.add_parser('parse', help='Parse YARS-PG to RDF.')
        parse_subparsers = parse_parser.add_subparsers(dest='type', required=True, help='Type of parsing: wholefile or sections.')

        parse_wholefile_parser = parse_subparsers.add_parser('wholefile', help='Parse entire YARS-PG file to RDF.')
        parse_wholefile_parser.add_argument('input', type=str, help='Input YARS-PG file.')
        parse_wholefile_parser.add_argument('output', type=str, help='Output RDF file.')
        parse_wholefile_parser.add_argument('--compression', type=str, choices=['gzip', 'brotli', 'zstd', 'snappy'], help='Decompression method.')
        parse_wholefile_parser.add_argument('--format', type=str, default='nt', help='Output RDF format. N-Triples is default output format')

        parse_sections_parser = parse_subparsers.add_parser('sections', help='Parse YARS-PG files with separate nodes and edges sections to RDF.')
        parse_sections_parser.add_argument('--input-nodes', type=str, required=True, help='Input YARS-PG file for nodes.')
        parse_sections_parser.add_argument('--input-edges', type=str, required=True, help='Input YARS-PG file for edges.')
        parse_sections_parser.add_argument('output', type=str, help='Output RDF file.')
        parse_sections_parser.add_argument('--compression', type=str, choices=['gzip', 'brotli', 'zstd', 'snappy'], help='Decompression method.')
        parse_sections_parser.add_argument('--format', type=str, default='nt', help='Output RDF format. N-Triples is default output format')

        return parser.parse_args()

    def execute(self):
        """Executes the appropriate action based on the arguments."""
        if self.args.action == 'serialize':
            self.serialize()
        elif self.args.action == 'parse':
            self.parse()

    def serialize(self):
        """Serializes the RDF file to YARS-PG and compresses if needed."""
        if self.args.type == 'wholefile':
            serialize_rdf_to_yarspg(self.args.input, self.args.output)
            print(f"Serialized file created: {self.args.output}")
            if self.args.compression:
                compressed_output = f"{self.args.output}.{self.args.compression}"
                compress_file(self.args.output, compressed_output, self.args.compression, self.args.level)
        elif self.args.type == 'sections':
            temp_file = f"{self.args.input}.temp"
            serialize_rdf_to_yarspg(self.args.input, temp_file)
            nodes_section, edges_section = split_yarspg(temp_file)

            with open(self.args.output_nodes, "w", encoding="utf-8") as f:
                f.write("\n".join(nodes_section))
            print(f"Serialized nodes file created: {self.args.output_nodes}")

            with open(self.args.output_edges, "w", encoding="utf-8") as f:
                f.write("\n".join(edges_section))
            print(f"Serialized edges file created: {self.args.output_edges}")

            if self.args.compression:
                compress_file(self.args.output_nodes, f"{self.args.output_nodes}.{self.args.compression}", self.args.compression, self.args.level)

                compress_file(self.args.output_edges, f"{self.args.output_edges}.{self.args.compression}", self.args.compression, self.args.level)

    def parse(self):
        """Decompresses the YARS-PG file if needed and parses it to RDF."""
        if self.args.type == 'wholefile':
            if self.args.compression:
                decompressed_input = f"{self.args.input}.decompressed"
                decompress_file(self.args.input, decompressed_input, self.args.compression)

                parse_yarspg(decompressed_input, self.args.output, self.args.format)
            else:
                parse_yarspg(self.args.input, self.args.output, self.args.format)
            print(f"Parsed file created: {self.args.output}")
        elif self.args.type == 'sections':
            if self.args.compression:
                decompressed_nodes = f"{self.args.input_nodes}.decompressed"
                decompressed_edges = f"{self.args.input_edges}.decompressed"
                decompress_file(self.args.input_nodes, decompressed_nodes, self.args.compression)
                decompress_file(self.args.input_edges, decompressed_edges, self.args.compression)
                combine_sections(decompressed_nodes, decompressed_edges, "combined.yarspg")
                parse_yarspg("combined.yarspg", self.args.output, self.args.format)
            else:
                combine_sections(self.args.input_nodes, self.args.input_edges, "combined.yarspg")
                parse_yarspg("combined.yarspg", self.args.output, self.args.format)
            print(f"Parsed file created: {self.args.output}")


