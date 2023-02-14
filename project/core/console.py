import sys

COLOURS = {
    "RED": "\033[1;31m",
    "BLUE": "\033[1;34m",
    "CYAN": "\033[1;36m",
    "GREEN": "\033[0;32m",
    "RESET": "\033[0;0m",
    "BOLD": "\033[;1m",
    "REVERSE": "\033[;7m",
}


def print_to_console(output, colour=None):
    """Prints to console using sys.stdout using a defined colour."""
    if colour:
        sys.stdout.write(COLOURS[colour])
    sys.stdout.write(output)
    sys.stdout.write(COLOURS["RESET"])


def print_error_to_console(output):
    """Prints to console using sys.stderr in the color red."""
    sys.stderr.write(COLOURS["RED"])
    sys.stderr.write(output)
    sys.stderr.write(COLOURS["RESET"])
