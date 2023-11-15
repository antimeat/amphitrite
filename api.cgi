#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Refactored script for extracting images or listing sites as links.
author: Daz Vink
date: 2023-11-14
"""

import cgi
import database as db
import os

BASE_DIR = "/cws/op/webapps/er_ml_projects/davink/amphitrite"
BASE_URL = "http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite"
def list_sites_as_links():
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

    html_table_rows = "".join([f"<tr><td><a href='api.cgi?site_name={site_names[i]}' target='_blank'>{site_names[i]}</a></td><td>{tables[i]}</td><td>{', '.join(map(str, partitions[i]))}</td></tr>" for i in range(len(site_names))])
    return f"{table_style}<h2>Partitioned Swell Tables</h2><table>{headers}{html_table_rows}</table>"

def main():
    # Parse the parameters
    form = cgi.FieldStorage()
    site_name = form.getvalue('site_name', "Woodside - Pluto 10 days")

    # Check if site_name is 'list' to list all sites as links
    if site_name == 'list':
        print("Content-Type: text/html")
        print()
        print(list_sites_as_links())
    else:
        # Set the HTTP header for JSON content
        print("Content-Type: application/json")
        print("Access-Control-Allow-Origin: *") 
        print("Access-Control-Allow-Methods: GET, POST, OPTIONS")
        print("Access-Control-Allow-Headers: Content-Type") 
        print()

        run_time = form.getvalue('run_time', None)
        # Fetch wavetable data from the database
        result = db.get_wavetable_from_db(site_name, run_time) if run_time else db.get_wavetable_from_db(site_name)
        # Print the result as JSON
        print(result["data"])

if __name__ == "__main__":
    main()
