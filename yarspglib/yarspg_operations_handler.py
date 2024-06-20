import gzip
import brotli
import zstandard as zstd
import snappy
from rdflib import Graph
from yarspglib.serializer.YARSpgSerializer import YARSpgSerializer
from yarspglib.parser.YARSpgProcessor import YARSpgProcessor

def serialize_rdf_to_yarspg(input_file: str, output_file: str) -> None:
    graph = Graph()
    graph.parse(input_file, format="nt")
    serializer = YARSpgSerializer(graph)
    with open(output_file, "wb") as f:
        serializer.serialize(f)

def parse_yarspg(input_file: str, output_file: str, rdf_format: str) -> None:
    with open(input_file, "r", encoding="utf8") as file:
        yarspg_data = file.read()
    processor = YARSpgProcessor()
    processor.process_YARSpg(yarspg_data)
    with open(output_file, "wb") as f:
        processor.graph.serialize(f, format=rdf_format, encoding="utf-8")

def split_yarspg(temp_file: str):
    with open(temp_file, "r", encoding="utf-8") as file:
        nodes_section = []
        edges_section = []
        section = None

        for line in file:
            line_lower = line.lower().strip()  # Remove surrounding whitespace
            if line_lower.startswith("#nodes") or line_lower.startswith("# nodes") or line_lower.startswith("%nodes") or line_lower.startswith("% nodes"):
                section = "nodes"
            elif line_lower.startswith("#edges") or line_lower.startswith("# edges") or line_lower.startswith("%edges") or line_lower.startswith("% edges"):
                section = "edges"
            elif section == "nodes":
                nodes_section.append(line.strip())
            elif section == "edges":
                edges_section.append(line.strip())
    return nodes_section, edges_section

def combine_sections(nodes_file: str, edges_file: str, combined_file: str) -> None:
    with open(combined_file, "w", encoding="utf-8") as f_out:
        with open(nodes_file, "r", encoding="utf-8") as nodes_in:
            f_out.write("# Nodes\n")
            f_out.write(nodes_in.read())
        f_out.write("\n# Edges\n")
        with open(edges_file, "r", encoding="utf-8") as edges_in:
            f_out.write(edges_in.read())

def compress_file(input_file: str, output_file: str, compress_func, level=None) -> None:
    with open(input_file, "rb") as f_in:
        data = f_in.read()
        if compress_func == 'gzip':
            compressed_data = gzip.compress(data, compresslevel=level) if level else gzip.compress(data)
        elif compress_func == 'brotli':
            compressed_data = brotli.compress(data, quality=level) if level else brotli.compress(data)
        elif compress_func == 'zstd':
            compressed_data = zstd.ZstdCompressor(level=level).compress(data) if level else zstd.ZstdCompressor().compress(data)
        elif compress_func == 'snappy':
            compressed_data = snappy.compress(data)
        else:
            raise ValueError(f"Unknown compression method: {compress_func}")

        with open(output_file, "wb") as f_out:
            f_out.write(compressed_data)
            print(f"Compressed file created: {output_file}")

def decompress_file(input_file: str, output_file: str, decompress_func) -> None:
    with open(input_file, "rb") as f_in:
        compressed_data = f_in.read()
        if decompress_func == 'gzip':
            data = gzip.decompress(compressed_data)
        elif decompress_func == 'brotli':
            data = brotli.decompress(compressed_data)
        elif decompress_func == 'zstd':
            data = zstd.ZstdDecompressor().decompress(compressed_data)
        elif decompress_func == 'snappy':
            data = snappy.decompress(compressed_data)
        else:
            raise ValueError(f"Unknown decompression method: {decompress_func}")

        with open(output_file, "wb") as f_out:
            f_out.write(data)
            print(f"Decompressed file created: {output_file}")

def write_to_file(data: bytes, output_file: str):
    with open(output_file, "wb") as f:
        f.write(data)
        print(f"File created: {output_file}")
