#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import json
import requests
import argparse
import html
import glob
import markdown2

def github_markdown_to_html(md_content):
    """Convert Markdown to HTML using GitHub's API."""
    url = "https://api.github.com/markdown"
    headers = {"Accept": "application/vnd.github+json",'Content-Type': 'text/x-markdown'}
    data = {"text": md_content, "mode": "gfm"}
    response = requests.post(url, headers=headers, json=data)
    return response.text

def gitlab_markdown_to_html(md_content):
    """Convert Markdown to HTML using GitLab's API."""
    token = "glpat-66gAQXFiCirWSxBL_Gj5"
    url = "https://gitlab.bom.gov.au/api/v4/markdown"
    headers = {"PRIVATE-TOKEN": token, 'Content-Type': 'application/json'}
    data = {"text": md_content, "gfm": "true"}
    response = requests.post(url, headers=headers, json=data)
    
    if response.status_code == 200 or response.status_code == 201:
        # Unescape HTML content
        html_content = html.unescape(json.loads(response.text).get('html', ''))
        return html_content
    else:
        return f"Error: {response.status_code} - {response.text}"

def markdown2_to_html(md_content,css_file_path="github-markdown.css"):
    """
    Convert Markdown to HTML using markdown2 library.

    Args:
    - md_content (str): String containing Markdown content.

    Returns:
    - str: String containing converted HTML content.
    """
    # Extras for additional features like Table of Contents, fenced code blocks
    extras = ["toc", "fenced-code-blocks", "tables"]

    # Convert Markdown to HTML
    html_content = markdown2.markdown(md_content, extras=extras)

    # HTML header with link to the CSS file
    html_header = f"""
    <head>
        <link rel="stylesheet" type="text/css" href="{css_file_path}">
    </head>
    """

    # Combine HTML header and content
    final_html = f"<html>{html_header}<body>{html_content}</body></html>"

    return final_html
    
def convert_file(file_path):
    """Convert a single file from Markdown to HTML."""
    with open(file_path, 'r', encoding='utf-8') as md_file:
        markdown_content = md_file.read()

    html_content = markdown2_to_html(markdown_content)
    html_filename = file_path.replace('.md', '.html')
    
    with open(html_filename, 'w', encoding='utf-8') as html_file:
        html_file.write(html_content)

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description="Convert Markdown to HTML using GitLab API")
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
