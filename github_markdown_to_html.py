#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import json
import requests
import argparse
import os
import glob

def markdown_to_html(md_content):
    """Convert Markdown to HTML using GitHub's API."""
    url = "https://api.github.com/markdown"
    headers = {'Content-Type': 'application/json'}
    data = {"text": md_content, "mode": "gfm"}
    response = requests.post(url, headers=headers, json=data)
    return response.text

def convert_file(file_path):
    """Convert a single file from Markdown to HTML."""
    with open(file_path, 'r', encoding='utf-8') as md_file:
        markdown_content = md_file.read()

    html_content = markdown_to_html(markdown_content)
    html_filename = file_path.replace('.md', '.html')
    
    with open(html_filename, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML using GitHub API")
    parser.add_argument('--input', help="Path to the input Markdown file")
    parser.add_argument('--all', action='store_true', help="Convert all Markdown files in the current directory")
    return parser.parse_args()

def main():
    # Parse arguments
    args = parse_arguments()

    if args.all:
        # Convert all .md files in the current directory
        for md_file in glob.glob('*.md'):
            convert_file(md_file)
    elif args.input:
        # Convert a specific file
        convert_file(args.input)
    else:
        print("No input provided. Use --input for a specific file or --all for all files.")

if __name__ == "__main__":
    main()
