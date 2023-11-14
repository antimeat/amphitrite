#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Refactored script for extracting images or listing sites as links.
"""
__author__ = "Daz Vink"
__date__ = "2023-11-14"

import cgi
import database as db

def list_sites_as_links():
    site_names = db.get_all_sites()["data"]
    table_style = """
        <style>
            table { 
                border-collapse: collapse; 
                width: 50%; 
                margin: 20px auto; /* Centers the table */
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
    html_table_rows = "".join([f"<tr><td><a href='api.cgi?site_name={name}',target='_blank'>{name}</a></td></tr>" for name in site_names])
    return f"{table_style}<h2>Partitioned Swell Tables</h2><table>{html_table_rows}</table>"

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
