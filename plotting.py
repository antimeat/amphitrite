#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    plotting.py
"""

import os
import json
import urllib.request
import amphitrite_configs as configs
import argparse

# Set the umask to 0 to ensure that no permissions are masked
os.umask(0)

BASE_DIR = configs.BASE_DIR
BASE_URL = configs.BASE_URL

# Base URL for the iframe and image sources
BASE_URL_GHPLOTS = "http://wa-vw-er.bom.gov.au/webapps/vwave/plots/"
BASE_URL_IMAGES = "http://wa-vw-er.bom.gov.au/webapps/vwave/plotsSpec/"
BASE_URL_TABLES = BASE_URL + "/transformer/tables/"  

OUTPUT_DIR = os.path.join(BASE_DIR, "plots")
TABLES = {}

def load_tables():
    """
    Load tables from the API
    """
    global TABLES  
    url = BASE_URL + "/api.cgi?get=tables"  
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")
    TABLES = json.loads(data)
  
def generate_html(site_name):
    """
    Generate HTML content for a site
    """
    plot_file = TABLES[site_name]['table'] + ".html"
    image_file = TABLES[site_name]['table'] + ".png"
    table_file = site_name.replace(' ', '_').replace('-', '') + "_data.html"  # Normalize filenames

    # HTML content
    html_content = f"""<!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8" />
            <meta name="viewport" content="width=device-width, initial-scale=1.0" />
            <title>{site_name}</title>
            <link rel="stylesheet" href="body.css" />
        </head>
        <body>
            <header>
                <h1>{site_name}</h1>
            </header>
            <div class="container">
                <div class="left-column">
                    <div class="plot">
                        <iframe src="{BASE_URL_GHPLOTS}{plot_file}"></iframe>
                    </div>
                    <div class="image">
                        <img src="{BASE_URL_IMAGES}{image_file}" alt="{site_name} Wave Plot" />
                    </div>
                </div>
                <div class="right-column">
                    <div class="table">
                        <iframe src="{BASE_URL_TABLES}{table_file}"></iframe>
                    </div>
                </div>
            </div>
        </body>
    </html>"""

    # Write the HTML content to a file
    out_file = os.path.join(OUTPUT_DIR, f"{site_name.lower().replace(' ', '_').replace('-', '')}.html")
    with open(out_file, "w") as file:
        file.write(html_content)

    # Set permissions to 666 (read and write for user, group, and others)
    # os.chmod(out_file, 0o666)
    
def plot_all_combined_pages():
    """
    Loop through the TABLES dictionary and generate HTML content for each site
    """
    load_tables()
    for site_name in TABLES:
        generate_html(site_name)

def plot_single_combined_page(site_name):
    """
    Plot individual page content 
    """
    load_tables()
    generate_html(site_name)

def main():
    parser = argparse.ArgumentParser(description="Generate HTML content for each site")
    parser.add_argument("--site", help="Site name")
    args = parser.parse_args()

    if args.site:
        try:
            plot_single_combined_page(args.site)
            print(f"Generated HTML content for {args.site}")
        except Exception as e:
            print(f"Error: {e}")
        
    else:
        try:
            plot_all_combined_pages()
        except Exception as e:
            print(f"Error: {e}")

if __name__ == "__main__":
    main()
