import random
import sys

from yarspglib.command_line_interface import CommandLineInterface

def main():
    try:
        cli = CommandLineInterface()
        cli.execute()

    except Exception as e:
        print(f"Error occurred: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
