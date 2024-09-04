#!/usr/bin/env python3

import os
import sys
import json
from datetime import datetime, timedelta
import requests
from enum import Enum
import argparse


# ANSI color codes
class Color(Enum):
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    RED = "\033[91m"
    RESET = "\033[0m"


def print_msg(level, message, color):
    """Print a colored message with format [level] message."""
    if isinstance(color, Color):
        color_code = color.value
        reset_code = Color.RESET.value
        print(f"{color_code}[{level}]{reset_code} {message}")
    else:
        print(
            f"[{level}] {message}"
        )  # Fallback to regular print if color is not recognized


def load_config(config_file_path):
    """Load configuration from a JSON file."""
    try:
        with open(config_file_path, "r") as config_file:
            return json.load(config_file)
    except FileNotFoundError:
        print_msg(
            "error", f"Configuration file '{config_file_path}' not found.", Color.RED
        )
        sys.exit(1)


def get_date_info(date_str=None, move_days=None):
    """Get date formatted as 'MM-dd' and 'yyyy-MM'."""
    if date_str:
        try:
            date = datetime.strptime(date_str, "%Y-%m-%d")
        except ValueError:
            print_msg(
                "error",
                f"Invalid date format '{date_str}'. Use 'YYYY-MM-DD'.",
                Color.RED,
            )
            sys.exit(1)
    else:
        date = datetime.now()

    if move_days is not None:
        date += timedelta(days=move_days)

    current_date = date.strftime("%m-%d")
    current_year_month = date.strftime("%Y-%m")
    return current_date, current_year_month


def create_directory(path):
    """Create a directory if it does not exist."""
    if not os.path.exists(path):
        os.makedirs(path)


def download_file(url, output_path):
    """Download a file from a URL."""
    try:
        print_msg("info", f"Downloading {url}", Color.GREEN)
        response = requests.get(url)
        response.raise_for_status()
        with open(output_path, "wb") as f:
            f.write(response.content)
    except requests.RequestException as e:
        print_msg("error", f"Error downloading {url}: {e}", Color.RED)
        sys.exit(1)


def replace_content(file_path, title, author):
    """Replace the title and author in the LaTeX file with the directory name and author name."""
    try:
        with open(file_path, "r") as file:
            content = file.read()
        new_content = content.replace(r"\title{Title}", rf"\title{{{title}}}")
        if author:
            new_content = new_content.replace(
                r"\author{Author}", rf"\author{{{author}}}"
            )
        with open(file_path, "w") as file:
            file.write(new_content)
        print_msg("info", f"Replaced title and author in: {file_path}", Color.GREEN)
    except Exception as e:
        print_msg(
            "error", f"Error replacing title and author in {file_path}: {e}", Color.RED
        )
        sys.exit(1)


def create_remark_file(dir_path, remark_name):
    """Create a remark file in the specified directory."""
    remark_path = os.path.join(dir_path, remark_name)
    with open(remark_path, "w"):
        pass
    print_msg("info", f"Remark file created: {remark_path}", Color.GREEN)


def check_root_directory(root_dir):
    """Check if the root directory is valid and suggest potential fixes."""
    script_dir = os.path.abspath(os.path.dirname(__file__))
    current_dir = os.getcwd()

    if os.path.abspath(root_dir) in [script_dir, current_dir]:
        return True
    else:
        print_msg(
            "error",
            f"The specified root directory '{root_dir}' must be the directory where the script is located or the current working directory.",
            Color.RED,
        )
        return False


def main():
    # Argument parsing
    parser = argparse.ArgumentParser(description="Create a new LaTeX note or report.")
    parser.add_argument(
        "template_type", type=str, help="Template type (e.g., note, report)"
    )
    parser.add_argument(
        "--name", type=str, help="Specify a name for the directory and main file"
    )
    parser.add_argument("--remark", type=str, help="Remark file name (optional)")
    parser.add_argument("--date", type=str, help="Specify the date (YYYY-MM-DD)")
    parser.add_argument(
        "--move",
        type=int,
        help="Specify the number of days to move from today (e.g., -1 for yesterday, 1 for tomorrow)",
    )
    parser.add_argument(
        "--config",
        type=str,
        default=os.path.join(".", ".config", "create_config.json"),
        help="Path to configuration file (default: ./.config/create_config.json)",
    )
    parser.add_argument(
        "--root",
        type=str,
        help="Specify the root directory (overrides configuration file)",
    )
    args = parser.parse_args()

    # Ensure that --date and --move are not used together
    if args.date and args.move is not None:
        print_msg(
            "error",
            "Error: --date and --move options cannot be used together.",
            Color.RED,
        )
        sys.exit(1)

    # Load configuration
    config_data = load_config(args.config)

    # Validate template type
    template_type = args.template_type
    if template_type not in config_data or template_type == "_config":
        print_msg(
            "error",
            f"Invalid template type '{template_type}'. Please choose from: {', '.join([key for key in config_data.keys() if key != '_config'])}.",
            Color.RED,
        )
        sys.exit(1)

    # Get configuration details for the selected template type
    template_config = config_data[template_type]
    main_url = template_config["mainTemplateUrl"]

    # Use default values if optional configuration is not provided
    class_urls = template_config.get("classFileUrl", [])
    if isinstance(class_urls, str):
        class_urls = [class_urls]
    author_name = template_config.get("Author", None)
    prefix = template_config.get("directoryPrefix", f"{template_type}-")

    # Determine the root directory
    root_dir = args.root if args.root else config_data["_config"]["rootDirectory"]

    # Check if root directory is valid
    if not check_root_directory(root_dir):
        sys.exit(1)

    # Get date and construct directory and file names
    date, year_month = get_date_info(args.date, args.move)
    parent_dir = os.path.join(root_dir, year_month)

    if args.name:
        dir_name = f"{prefix}{args.name}"
    else:
        dir_name = f"{prefix}{date}"

    file_name = f"{dir_name}.tex"

    # Define full directory path and target file path
    dir_path = os.path.join(parent_dir, dir_name)
    dest_file = os.path.join(dir_path, file_name)

    # Create parent directory if it doesn't exist
    create_directory(parent_dir)

    # Check if the target directory already exists
    if os.path.exists(dir_path):
        print_msg(
            "error",
            f"The target directory '{dir_path}' already exists. Please check or remove the existing directory.",
            Color.RED,
        )
        sys.exit(1)
    else:
        # Create new directory
        create_directory(dir_path)

    # Download the main template file
    download_file(main_url, dest_file)

    # Download the class files if specified
    for url in class_urls:
        download_file(url, os.path.join(dir_path, os.path.basename(url)))

    # Replace the title and author in the downloaded main template file
    replace_content(dest_file, dir_name, author_name)

    # If a remark is provided, create a remark file
    if args.remark:
        create_remark_file(dir_path, args.remark)

    # Output success message
    print_msg("info", f"Successfully Created: {dir_path}", Color.GREEN)


if __name__ == "__main__":
    main()
