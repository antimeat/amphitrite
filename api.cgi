#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Refactored script for extracting images or listing sites as links.
author: Daz Vink
date: 2023-11-14
"""

import cgi
import database as db
import os
import pandas as pd
import json
import sys
import logging

BASE_DIR = "/cws/op/webapps/er_ml_projects/davink/amphitrite"
BASE_URL = "http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite"
LOG_FILE = os.path.join(BASE_DIR,'api.log')

try:
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        filename=LOG_FILE, 
        level=logging.ERROR,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    logging.info("Logging initialized successfully.")
except Exception as e:
    print(f"Logging setup failed: {e}")

def handle_error(status_code, message):
    """Handle errors by logging and sending an appropriate response."""
    logging.error(message)
    print(f"Status: {status_code}")
    print("Content-Type: application/json")
    print()
    print(json.dumps({"success": False, "message": message}))
    sys.exit()

def load_config_file(config_file):
    """Read in the sites config file"""
    try:
        site_tables = {}
        with open(config_file, 'r') as file:
            for line in file:
                # Skip comment lines
                if line.startswith('#'):
                    continue

                parts = line.strip().split(', ')
                if len(parts) < 3:
                    continue  # Skip malformed lines

                site = parts[0]
                table = parts[1]
                # Parse all split ranges
                split_ranges = [tuple(map(float, part.split('-'))) for part in parts[2:]]

                site_tables[site] = {"table": table, "parts": split_ranges}

        return site_tables

    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")

def load_exclusion_file(config_file):
    """Load the exclusion_sites.txt and return json"""
    try:
        sites = {}
        with open(config_file, 'r') as file:
            for line in file:
                # Strip leading and trailing spaces
                stripped_line = line.strip()

                # Skip comment lines and empty lines
                if stripped_line.startswith('#') or not stripped_line:
                    continue

                sites[stripped_line] = {"name": stripped_line}

        return sites

    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")

def database_check():
    """Display sites and run_times as columns in an HTML table"""
    try:
        sites_str, run_times_str = db.api_output()

        table_style = """
            <style>
                table { 
                    border-collapse: collapse; 
                    width: 80%; 
                    margin: 20px auto; 
                }
                th, td { 
                    border: 1px solid black; 
                    padding-right: 20px;
                    padding-left: 20px;
                    vertical-align: top;
                    text-align: top; 
                }
                tr:nth-child(even) { 
                    background-color: #f2f2f2; 
                }
            </style>
        """
        
        html_table = f"{table_style}<table><tr><td>{sites_str}</td><td>{run_times_str}</td></tr></table>"
        print(html_table)

    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")

def list_sites_as_html():
    """Print out all the sites and links to tables from the database via html"""
    try:
        site_data = db.get_all_sites()["data"]
        site_names = site_data[0]
        tables = site_data[1]
        partitions = site_data[2]
        table_style = """
            <style>
                table { 
                    border-collapse: collapse; 
                    width: 50%; 
                    margin: 20px auto; 
                }
                th, td { 
                    border: 1px solid black; 
                    padding: 8px; 
                    text-align: left; 
                }
                tr:nth-child(even) { 
                    background-color: #f2f2f2; 
                }
                h2 {
                    text-align: center;
                }
            </style>
        """
        headers = "<tr><th>Forecast site</th><th>Auswave table</th><th>Partitions</th></tr>"

        html_table_rows = "".join([f"<tr><td><a href='api.cgi?get=site&site_name={site_names[i]}' target='_blank'>{site_names[i]}</a></td><td>{tables[i]}</td><td>{', '.join(map(str, partitions[i]))}</td></tr>" for i in range(len(site_names))])
        return f"{table_style}<h2>Partitioned Swell Tables</h2><table>{headers}{html_table_rows}</table>"
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")

def list_sites_as_json():
    """Return aswave tables in json"""
    try:
        file_name = os.path.join(BASE_DIR,"site_config.txt")
        json_str = load_config_file(file_name)
        
        return json.dumps(json_str)
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")

def list_exclusion_as_json():
    """Return exclusion sites in json"""
    try:
        file_name = os.path.join(BASE_DIR,"exclusion_list.txt")
        json_str = load_exclusion_file(file_name)
        
        return json.dumps(json_str)
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")

def main():
    # Parse the parameters
    form = cgi.FieldStorage()
    get = form.getvalue('get', "list_html")

    # Check if site_name is 'list' to list all sites as links
    if get == 'list_html':
        print("Content-Type: text/html")
        print()
        print(list_sites_as_html())
    
    elif get == 'database':
        print("Content-Type: text/html")
        print()
        database_check()
    
    elif get == 'list_json':
        print("Content-Type: application/json")
        print()
        print(list_sites_as_json())    
    
    elif get == 'exclusion':
        print("Content-Type: application/json")
        print()
        print(list_exclusion_as_json())    
    
    elif get == "site":
        site_name = form.getvalue('site_name', "Woodside - Pluto 7 days") 
        run_time = form.getvalue('run_time', None)
        
        # Fetch wavetable data from the database
        result = db.get_wavetable_from_db(site_name, run_time) if run_time else db.get_wavetable_from_db(site_name)
        
        # Set the HTTP header for JSON content
        print("Content-Type: application/json")
        print()
        print(result["data"])
    else:
        print("Content-Type: text/html")
        print()
        print(list_sites_as_html())
        
if __name__ == "__main__":
    main()
