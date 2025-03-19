#!/usr/bin/env python
import argparse
import json
import os
import sys
from typing import Dict, List, Tuple, Union, Optional, Any


def find_all_json_files(directory: str = ".") -> List[str]:
    """
    Find all JSON files in the repository.
    Except files that have LocalRunOutputs on their path.

    Args:
        directory: Base directory to search from

    Returns:
        List of paths to JSON files
    """
    json_files = list()
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.json') and "LocalRunOutputs" not in root:
                json_files.append(os.path.join(root, file))
    return json_files


def detect_indentation(content: str) -> int:
    """
    Detect the most common indentation level in a JSON file.

    Args:
        content: The content of the JSON file

    Returns:
        The detected indentation level, or 2 as default
    """
    lines = content.split('\n')
    indents: List[int] = []

    for line in lines:
        if line.strip() and line.startswith(' '):
            # Count leading spaces
            indent_size = len(line) - len(line.lstrip(' '))
            if indent_size > 0:
                indents.append(indent_size)

    # Determine most common indent or default to 2
    indent_size = 2
    if indents:
        indent_size = min(indents)

    return indent_size


def update_auth_mode(obj: Any, direction: str) -> bool:
    """
    Recursively update AuthenticationMode in a JSON object.

    Args:
        obj: The JSON object (dict or list)
        direction: The conversion direction, either "ConnectionString2Msi" or "Msi2ConnectionString"

    Returns:
        True if modifications were made, False otherwise
    """
    modified = False

    if isinstance(obj, dict):
        # Check if this dictionary has the key we're looking for
        if "AuthenticationMode" in obj:
            current_mode = obj["AuthenticationMode"]

            if direction == "ConnectionString2Msi" and current_mode == "ConnectionString":
                obj["AuthenticationMode"] = "Msi"
                modified = True
            elif direction == "Msi2ConnectionString" and current_mode == "Msi":
                obj["AuthenticationMode"] = "ConnectionString"
                modified = True

        # Recursively process all dictionary values
        for key, value in obj.items():
            if update_auth_mode(value, direction):
                modified = True

    # Handle lists by recursively processing each element
    elif isinstance(obj, list):
        for item in obj:
            if update_auth_mode(item, direction):
                modified = True

    return modified


def read_json_file(file_path: str) -> Tuple[Optional[Union[Dict, List]], int, Optional[str]]:
    """
    Read and parse a JSON file, detecting its indentation.

    Args:
        file_path: Path to the JSON file

    Returns:
        Tuple of (data, indent_size, error_message) where:
            - data is the parsed JSON or None if parsing failed
            - indent_size is the detected indentation or 2 as default
            - error_message is None if successful, or contains an error message
    """
    # Check if file is empty
    if os.path.getsize(file_path) == 0:
        return None, 2, "Empty file"

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            # First read raw content to analyze indentation
            content = f.read()
            indent_size = detect_indentation(content)

            # Now try to parse the JSON
            try:
                data = json.loads(content)
                return data, indent_size, None
            except json.JSONDecodeError as je:
                return None, indent_size, f"Invalid JSON: {str(je)}"
    except UnicodeDecodeError:
        return None, 2, "File encoding issues"
    except Exception as e:
        return None, 2, f"Error reading file: {str(e)}"


def write_json_file(file_path: str, data: Union[Dict, List], indent_size: int) -> bool:
    """
    Write JSON data to a file with the specified indentation.

    Args:
        file_path: Path to the JSON file
        data: The JSON data to write
        indent_size: The indentation level to use

    Returns:
        True if successful, False otherwise
    """
    try:
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=indent_size, ensure_ascii=False)
        return True
    except Exception as e:
        print(f"Error writing to {file_path}: {str(e)}")
        return False


def process_json_file(file_path: str, direction: str) -> int:
    """
    Process a single JSON file to update AuthenticationMode.

    Args:
        file_path: Path to the JSON file
        direction: The conversion direction, either "ConnectionString2Msi" or "Msi2ConnectionString"

    Returns:
        1 if file was processed, 0 if it was skipped
    """
    data, indent_size, error = read_json_file(file_path)

    if error:
        print(f"Skipping {file_path}: {error}")
        return 0

    # Update the authentication mode
    if update_auth_mode(data, direction):
        if write_json_file(file_path, data, indent_size):
            print(f"Modified {file_path} (using indent size: {indent_size})")
            return 1

    return 0


def process_files(direction: str) -> int:
    """
    Process all JSON files to replace auth mode.

    Args:
        direction: The conversion direction, either "ConnectionString2Msi" or "Msi2ConnectionString"

    Returns:
        Exit code (0 for success)
    """
    print(f"Running conversion: {direction}")

    files = find_all_json_files()
    processed = 0
    total = len(files)

    for file_path in files:
        processed += process_json_file(file_path, direction)

    print(f"Modified {processed} out of {total} files")
    return 0


def main() -> int:
    """
    Main entry point for the script.

    Returns:
        Exit code (0 for success)
    """
    parser = argparse.ArgumentParser(description='Convert AuthenticationMode in JSON files')

    # Add direction as the only argument
    parser.add_argument('--direction', choices=['ConnectionString2Msi', 'Msi2ConnectionString'],
                        required=True, help='Specify the conversion direction')

    args = parser.parse_args()
    return process_files(args.direction)


if __name__ == '__main__':
    sys.exit(main())
