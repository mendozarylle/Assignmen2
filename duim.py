#!/usr/bin/env python3

import subprocess
import sys
import argparse

'''
OPS445 Assignment 2
Program: duim.py 
Author: "Rylle Mendoza
The python code in this file (duim.py) is original work written by
"Your Name". No code in this file is copied from any other source 
except those provided by the course instructor, including any person, 
textbook, or online resource. I have not shared this python script 
with anyone or anything except for submission for grading.  
I understand that the Academic Honesty Policy will be enforced and 
violators will be reported and appropriate action will be taken.

Description: A tool to display disk usage of a directory, visualized as bar graphs.
Date: 24/12/1
'''

def parse_command_args():
    """
    Set up argparse to handle command-line arguments.
    Returns parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="DU Improved -- See Disk Usage Report with bar charts",
        epilog="Copyright 2023"
    )
    parser.add_argument(
        "-H", "--human-readable",
        action="store_true",
        help="Print sizes in human-readable format (e.g., 1K, 23M, 2G)."
    )
    parser.add_argument(
        "-l", "--length",
        type=int,
        default=20,
        help="Specify the length of the graph. Default is 20."
    )
    parser.add_argument(
        "target",
        nargs="?",
        default=".",
        help="The directory to scan."
    )
    return parser.parse_args()

def percent_to_graph(percent: int, total_chars: int) -> str:
    """
    Converts a percentage into a bar graph representation.
    Args:
        percent (int): Percentage to visualize (0-100).
        total_chars (int): Total length of the bar graph.
    Returns:
        str: A string representing the bar graph.
    """
    if not (0 <= percent <= 100):
        raise ValueError("Percentage must be between 0 and 100.")
    filled = round((percent / 100) * total_chars)
    return "=" * filled + " " * (total_chars - filled)

def call_du_sub(location: str) -> list:
    """
    Calls `du` to get disk usage of a location.
    Args:
        location (str): The directory to scan.
    Returns:
        list: Raw `du` output as a list of strings, ignoring permission errors.
    """
    try:
        process = subprocess.Popen(
            ["du", "-d", "1", location],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        output, errors = process.communicate()
        if process.returncode != 0 and "Permission denied" not in errors:
            print(f"Error: {errors.strip()}", file=sys.stderr)
            sys.exit(1)
        # Filter out permission denied errors
        if errors:
            filtered_errors = "\n".join(
                line for line in errors.splitlines() if "Permission denied" not in line
            )
            if filtered_errors.strip():  # Print other errors if present
                print(f"Other errors occurred: {filtered_errors}", file=sys.stderr)
        return [line.strip() for line in output.split("\n") if line]
    except FileNotFoundError:
        print("Error: `du` command is not available on this system.", file=sys.stderr)
        sys.exit(1)

def create_dir_dict(raw_dat: list) -> dict:
    """
    Converts raw `du` output into a dictionary.
    Args:
        raw_dat (list): Raw `du` output.
    Returns:
        dict: Mapping of directory paths to their sizes in bytes.
    """
    dir_dict = {}
    for entry in raw_dat:
        size, path = entry.split(maxsplit=1)
        dir_dict[path] = int(size)
    return dir_dict

def bytes_to_human_r(kibibytes: int, decimal_places: int = 2) -> str:
    """
    Converts size in KiB to human-readable format.
    Args:
        kibibytes (int): Size in KiB.
        decimal_places (int): Number of decimal places for rounding.
    Returns:
        str: Size in a human-readable format.
    """
    suffixes = ['KiB', 'MiB', 'GiB', 'TiB', 'PiB']
    suf_count = 0
    result = kibibytes
    while result > 1024 and suf_count < len(suffixes) - 1:
        result /= 1024
        suf_count += 1
    return f"{result:.{decimal_places}f} {suffixes[suf_count]}"

if __name__ == "__main__":
    args = parse_command_args()
    target_directory = args.target
    graph_length = args.length
    human_readable = args.human_readable

    try:
        # Step 1: Get raw `du` output
        du_output = call_du_sub(target_directory)

        # Step 2: Convert raw data to a dictionary
        dir_dict = create_dir_dict(du_output)

        # Step 3: Calculate total size and percentages
        total_size = sum(dir_dict.values())

        # Step 4: Display results
        print(f"Total: {bytes_to_human_r(total_size)}   {target_directory}" if human_readable else f"Total: {total_size} bytes   {target_directory}")

        for path, size in dir_dict.items():
            percent = (size / total_size) * 100
            bar_graph = percent_to_graph(percent, graph_length)
            size_display = bytes_to_human_r(size) if human_readable else f"{size} B"
            print(f"{percent:5.1f} % [{bar_graph}] {size_display} {path}")

    except Exception as e:
        print(f"An error occurred: {e}", file=sys.stderr)
        sys.exit(1)

