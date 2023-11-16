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

BASE_DIR = "/cws/op/webapps/er_ml_projects/davink/amphitrite"
BASE_URL = "http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite"

def load_config_file(config_file):
        """
        Get the table name and partition ranges related to the siteName
        Parameters:
            siteName: ofcast site name
        Returns:
            a dictionary with the table name and partition ranges
        """
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

def list_sites_as_html():
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

def list_sites_as_json():
    """Return aswave tables in json"""
    file_name = os.path.join(BASE_DIR,"site_config.txt")
    json_str = load_config_file(file_name)
    
    return json.dumps(json_str)

def main():
    # Parse the parameters
    form = cgi.FieldStorage()
    get = form.getvalue('get', "list_html")

    # Check if site_name is 'list' to list all sites as links
    if get == 'list_html':
        print("Content-Type: text/html")
        print()
        print(list_sites_as_html())
    elif get == 'list_json':
        print("Content-Type: application/json")
        print()
        print(list_sites_as_json())    
    else:
        # Set the HTTP header for JSON content
        print("Content-Type: application/json")
        print()
        print(list_sites_as_html())
        
        site_name = form.getvalue('site_name', "Woodside - Pluto 7 days") 
        run_time = form.getvalue('run_time', None)
        # Fetch wavetable data from the database
        result = db.get_wavetable_from_db(site_name, run_time) if run_time else db.get_wavetable_from_db(site_name)
        # Print the result as JSON
        print(result["data"])

if __name__ == "__main__":
    main()
