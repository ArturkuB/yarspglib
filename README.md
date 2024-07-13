<br />
<div align="center">
  <h3 align="center">YARSPGLib</h3>
</div>

YARSPGLib processes files in RDF and [YARS-PG formats](https://github.com/lszeremeta/yarspg), facilitating serialization and parsing between them. It also includes options for compressing files ([gzip](https://docs.python.org/3/library/gzip.html), [Brotli](https://pypi.org/project/Brotli/), [zstandard](https://pypi.org/project/zstandard/), [snappy](https://pypi.org/project/python-snappy/)) post-serialization and decompressing them pre-parsing.

## Features 
-  **Serialization Support**: Serialize RDF files to YARS-PG format using the RDFLib library. This includes: 
	-  **Wholefile Serialization**: Serialize entire RDF files into a single YARS-PG file. Supports optional compression methods such as gzip, brotli, zstd, and snappy, with configurable compression levels. 
	-  **Section Serialization**: Serialize RDF files into YARS-PG format with separate nodes and edges sections. Each section can be compressed independently using the same optional compression methods. 
-  **Parsing Support**: Parse YARS-PG files back into RDF format. The parser is generated using ANTLR 4.13.1, providing several capabilities. This includes: 
	-  **Whole file parsing and compression**: Parse entire YARS-PG files into RDF format. Supports optional decompression for compressed YARS-PG files. 
	-  **Nodes and edges sections parsing and compression**: Decompress separate nodes and edges YARS-PG sections and parse them into RDF format. 
-  **Command-Line Interface (CLI)**: A user-friendly CLI for managing the serialization and parsing processes. The CLI provides options for specifying input and output files, choosing compression methods, and setting compression levels.

## Installation 

### Python from Source

1. **Clone Repository**:
   ```shell
   git clone git@github.com:ArturkuB/yarspglib.git
   ```

2. **Install Requirements**:
   ```shell
   pip install -r requirements.txt
   ```

3. **Execute YARSPGLib**:
   ```shell
   python -m yarspglib [-h]
   ```

## Usage


To view all options, use:

```shell
python -m yarspglib -h
```



### Options

- `-h`, `--help`: Display the help message.
- `-a {serialize,parse}`, `--action {serialize,parse}`: Choose the action to perform. Options are `serialize` for serializing RDF to YARS-PG or `parse` for parsing YARS-PG to RDF.
- `-t {wholefile,sections}`, `--type {wholefile,sections}`: Choose the type of operation. Options are `wholefile` for processing entire files or `sections` for processing nodes and edges separately.
- `-i INPUT`, `--input INPUT`: Specify the input file. Optional for both serialization and parsing actions.
- `-o OUTPUT`, `--output OUTPUT`: Specify the output file. Optional for both serialization and parsing actions.
- `--output-nodes OUTPUT_NODES`: Specify the output file for nodes when serializing sections. Required if `--type sections` is chosen.
- `--output-edges OUTPUT_EDGES`: Specify the output file for edges when serializing sections. Required if `--type sections` is chosen.
- `--input-nodes INPUT_NODES`: Specify the input file for nodes when parsing sections. Required if `--type sections` is chosen.
- `--input-edges INPUT_EDGES`: Specify the input file for edges when parsing sections. Required if `--type sections` is chosen.
- `-c {gzip,brotli,zstd,snappy}`, `--compression {gzip,brotli,zstd,snappy}`: Choose the compression method. Optional for both serialization and parsing actions.
- `-l LEVEL`, `--level LEVEL`: Specify the compression level (only applicable for gzip, brotli, and zstd). Optional for serialization with compression.
- `-f FORMAT`, `--format FORMAT`: Specify the RDF output format. Default is `nt`. 


### Practical Examples 

1. Serialize an RDF file to YARS-PG format with gzip compression at level 7:
   ```shell
   python -m yarspglib serialize wholefile input.nt output.yarspg --compression gzip -l 7
   ```
2. Serialize an RDF file to YARS-PG format, separating nodes and edges, with brotli compression at level 9:
   ```shell
   python -m yarspglib serialize sections input.nt --output-nodes output_nodes.yarspg --output-edges output_edges.yarspg --compression brotli -l 9
   ```
3. Serialize an RDF file to YARS-PG format without compression:
   ```shell
   python -m yarspglib serialize wholefile input.nt output.yarspg
    ```
4. Serialize an RDF file to YARS-PG format, separating nodes and edges, without compression:
   ```shell
   python -m yarspglib serialize sections input.nt --output-nodes output_nodes.yarspg --output-edges output_edges.yarspg
   ```
5. Parse a YARS-PG file to RDF format::
   ```shell
    python -m yarspglib parse wholefile input.yarspg output.nt --format nt
    ```
6. Parse a compressed YARS-PG file (using gzip) to RDF format:
   ```shell
   python -m yarspglib parse wholefile input.yarspg.gzip output.nt --compression gzip --format nt
   ```
7. Parse YARS-PG files with separated nodes and edges to RDF format:
	```shell
	python -m yarspglib parse sections --input-nodes input_nodes.yarspg --input-edges input_edges.yarspg output.nt --format nt
	```
8. Parse compressed YARS-PG files with separated nodes and edges (using brotli) to RDF format:
	```shell
	python -m yarspglib parse sections --input-nodes input_nodes.yarspg.br --input-edges input_edges.yarspg.br output.nt --compression brotli --format nt
	```
9. Serialize an RDF file to YARS-PG format, separating nodes and edges, with zstd compression at level 6:
	```shell
	python -m yarspglib parse sections --input-nodes input_nodes.yarspg.br --input-edges input_edges.yarspg.br output.nt --compression brotli --format nt
	```



## License 

YARSPGLib is licensed under the [MIT License](https://github.com/ArturkuB/yarspglib/blob/main/LICENSE).
