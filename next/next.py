#!/usr/bin/env python3

import os
import sys
import json
import requests
import argparse
import logging
from datetime import datetime

# Configure the logging system
logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")


def load_config(config_file_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_file_path, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        logging.error(f"Configuration file '{config_file_path}' not found.")
        sys.exit(1)


def create_directory(path):
    """Create a directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def download_file(url, output_path):
    """Download a file from a URL."""
    try:
        logging.info(f"Downloading {url}")
        response = requests.get(url)
        response.raise_for_status()
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response.content)
    except requests.RequestException as e:
        logging.error(f"Error downloading {url}: {e}")
        sys.exit(1)


def create_empty_file(output_path):
    """Create an empty file."""
    try:
        logging.info(f"Creating empty file {output_path}")
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, "w"):
            pass
    except OSError as e:
        logging.error(f"Error creating file {output_path}: {e}")
        sys.exit(1)


def prompt_for_replacement(file_path):
    """Prompt the user for whether to replace an existing file."""
    while True:
        choice = (
            input(
                f"File '{file_path}' already exists. Do you want to replace it? (y/n): "
            )
            .strip()
            .lower()
        )
        if choice in ["y", "n"]:
            return choice == "y"
        print("Invalid choice. Please enter 'y' or 'n'.")


def validate_template_type(template_type, config_data):
    """Validate the template type against the configuration data."""
    if template_type not in config_data:
        logging.error(
            f"Invalid template type '{template_type}'. Please choose from: {', '.join(config_data.keys())}."
        )
        sys.exit(1)
    return config_data[template_type]


def handle_existing_directory(dir_path):
    """Check if the target directory already exists and handle accordingly."""
    if os.path.exists(dir_path):
        logging.error(
            f"The target directory '{dir_path}' already exists. Please check or remove the existing directory."
        )
        sys.exit(1)
    else:
        create_directory(dir_path)


def process_template_files(template_config, dir_path):
    """Download files or create new files based on the template configuration."""
    for file_name, value in template_config.items():
        output_path = os.path.join(dir_path, file_name)
        if isinstance(value, str) and value.startswith("http"):
            # If value is a URL, download the file
            if os.path.exists(output_path):
                replace = prompt_for_replacement(output_path)
                if not replace:
                    logging.info(f"Skipping download for {output_path}.")
                    continue
            download_file(value, output_path)
        elif value is None:
            # If value is None, create an empty file
            if os.path.exists(output_path):
                replace = prompt_for_replacement(output_path)
                if not replace:
                    logging.info(f"Skipping creation of {output_path}.")
                    continue
            create_empty_file(output_path)
        else:
            logging.error(
                f"Invalid configuration for file '{file_name}'. Must be a URL or None."
            )
            sys.exit(1)


def create_info_file(dir_path, template_type, message=""):
    """Create an info file in the directory with absolute path and template type."""
    info_file_path = os.path.join(dir_path, ".info")
    absolute_path = os.path.abspath(dir_path)

    info_content = (
        f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        f"Type: {template_type}\n"
        f"Path: {absolute_path}\n"
        f"Detail: {message}\n"
    )
    with open(info_file_path, "w", encoding="utf-8", newline="\n") as f:
        f.write(info_content)
    logging.info(f"Created info file: {info_file_path}")


def normalize_path_for_display(path):
    """Convert any path to Linux style for display purposes."""
    return path.replace(os.sep, "/")


def find_info_files(root_dir):
    """Recursively find all .info files under the specified root directory."""
    info_files = []
    for dirpath, _, filenames in os.walk(root_dir):
        if ".git" in dirpath or ".aux" in dirpath:
            continue
        for file in filenames:
            if file.endswith(".info"):
                info_files.append(os.path.join(dirpath, file))
    logging.debug(f"Found {len(info_files)} .info files in {root_dir}")
    return info_files


def read_info_file(info_path):
    """Read the .info file and return its contents including extra text."""
    with open(info_path, "r", encoding="utf-8") as f:
        content = f.read()
    lines = content.splitlines()
    info_data = {}
    extra_text = []
    section = "info"

    for line in lines:
        if line.strip() == "":
            section = "text"
            continue
        if section == "info":
            if ":" in line:
                key, value = line.split(":", 1)
                info_data[key.strip().lower()] = value.strip()
        elif section == "text":
            extra_text.append(line)

    if extra_text:
        info_data["detail"] = "\n".join(extra_text)

    logging.debug(f"Parsed info file: {info_path}")
    return info_data


def rewrite_info_file(info_path, info_data):
    """Rewrite the .info file with updated path information."""
    content = []
    if "date" in info_data:
        content.append(f"Date: {info_data['date']}")
    if "type" in info_data:
        content.append(f"Type: {info_data['type']}")
    if "path" in info_data:
        content.append(f"Path: {info_data['path']}")
    if "detail" in info_data:
        content.append(f"Detail: {info_data['detail']}")

    with open(info_path, "w") as f:
        f.write("\n".join(content))
    logging.debug(f"Updated info file: {info_path}")


def find_pdf_files(directory):
    """Find all PDF files in the given directory."""
    pdf_files = [
        os.path.join(directory, file)
        for file in os.listdir(directory)
        if file.endswith(".pdf")
    ]
    logging.debug(f"Found {len(pdf_files)} PDF files in {directory}")
    return pdf_files


def parse_date(date_string):
    """Parse a date string into a datetime object. Return None if invalid."""
    try:
        return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def log_git_style_entry(item):
    """Print item information in a style similar to `git log`."""
    folder_display_path = normalize_path_for_display(item["full_path"])

    # Console output in git log style
    print(f"[{item['type']}] {item['date']}")
    print(f"    {item['name']}")
    print(f"    Path: {folder_display_path}")

    for pdf in item["pdf_files"]:
        print(f"    PDF: {normalize_path_for_display(pdf)}")

    if item["extra_text"]:
        print(f"\n    {item['extra_text']}")
    print()  # Blank line after each entry


def log_compact_style_entry(item):
    """Print item information in a compact, single-line format."""
    folder_display_path = normalize_path_for_display(item["full_path"])
    extra_text = f" {item['extra_text']}" if item["extra_text"] else ""

    # Console output in compact style
    print(f"[{item['type']}] {folder_display_path}{extra_text}")


def collect_and_display(
    root_dir, limit=5, filter_type=None, filter_name=None, compact=False, reverse=False
):
    """Collect information from .info files and print to console, with filtering, limiting, and optional reverse order."""
    all_info = []

    info_files = find_info_files(root_dir)
    for info_file in info_files:
        info_data = read_info_file(info_file)
        folder_path = os.path.dirname(info_file)

        # Check if Path is correct and rewrite if necessary
        expected_path = os.path.abspath(folder_path)
        if "path" in info_data and info_data["path"] != expected_path:
            info_data["path"] = expected_path
            rewrite_info_file(info_file, info_data)
        elif "path" not in info_data:
            info_data["path"] = expected_path
            rewrite_info_file(info_file, info_data)

        pdf_files = find_pdf_files(folder_path)

        date_str = info_data.get("date", "Unknown Date")
        date_obj = parse_date(date_str) if date_str != "Unknown Date" else None

        item_info = {
            "date": date_str,
            "date_obj": date_obj,
            "type": info_data.get("type", "Unknown Type"),
            "name": os.path.relpath(folder_path, root_dir),
            "full_path": folder_path,
            "pdf_files": pdf_files,
            "extra_text": info_data.get("detail", ""),
        }

        # Apply filters
        if filter_type and item_info["type"].lower() != filter_type.lower():
            continue
        if filter_name and filter_name.lower() not in item_info["name"].lower():
            continue

        all_info.append(item_info)

    # Sort the entries by date (newest first or oldest first)
    all_info.sort(key=lambda x: (x["date_obj"] or datetime.min), reverse=True)

    # Limit the number of displayed entries
    displayed_info = all_info[:limit]

    # Reverse the order if requested
    if reverse:
        displayed_info = displayed_info[::-1]

    # Display the entries with a truncation notice
    if len(all_info) > limit and reverse:
        print("... (total: %d)" % len(all_info))

    # Print entries
    for item in displayed_info:
        if compact:
            log_compact_style_entry(item)
        else:
            log_git_style_entry(item)

    if len(all_info) > limit and not reverse:
        print("... (total: %d)" % len(all_info))


def main():
    parser = argparse.ArgumentParser(
        description="Manage .info files and create directories/templates."
    )
    subparsers = parser.add_subparsers(dest="command")

    # Subparser for 'create' command
    create_parser = subparsers.add_parser(
        "create", help="Create directories and files based on templates."
    )
    create_parser.add_argument(
        "directory",
        type=str,
        help="Directory to create.",
    )
    create_parser.add_argument(
        "--config",
        type=str,
        default=".config/next_config.json",
        help="Configuration file for templates. (default: .config/next_config.json)",
    )
    create_parser.add_argument(
        "--type",
        "-t",
        type=str,
        required=True,
        help="Template type to use.",
    )
    create_parser.add_argument(
        "--message",
        "-m",
        type=str,
        default="",
        help="Optional message for the .info file.",
    )

    # Subparser for 'index' command
    index_parser = subparsers.add_parser(
        "index", help="Index and display .info file information."
    )
    index_parser.add_argument(
        "--root",
        type=str,
        default=".",
        help="Root directory to search for .info files. (default: .)",
    )
    index_parser.add_argument(
        "-l",
        "--limit",
        type=int,
        default=5,
        help="Limit the number of displayed entries.",
    )
    index_parser.add_argument("--filter-type", type=str, help="Filter entries by type.")
    index_parser.add_argument("--filter-name", type=str, help="Filter entries by name.")
    index_parser.add_argument(
        "-c",
        "--compact",
        action="store_true",
        help="Use single-line compact output format.",
    )
    index_parser.add_argument(
        "-r",
        "--reverse",
        action="store_true",
        help="Display entries in reverse chronological order.",
    )

    args = parser.parse_args()

    if args.command == "create":
        config_data = load_config(args.config)
        template_config = validate_template_type(args.type, config_data)
        handle_existing_directory(args.directory)
        process_template_files(template_config, args.directory)
        create_info_file(args.directory, args.type, args.message)
    elif args.command == "index":
        root_dir = os.path.abspath(args.root)
        logging.debug(f"Starting to process files in {root_dir}")
        collect_and_display(
            root_dir,
            limit=args.limit,
            filter_type=args.filter_type,
            filter_name=args.filter_name,
            compact=args.compact,
            reverse=args.reverse,
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
