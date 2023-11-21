#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Refactored script for extracting images or listing sites as links.
author: Daz Vink
date: 2023-11-15
"""
import cgi
import json
import pandas as pd
import requests
from io import StringIO
import os
import logging
import sys

ACTIVE_STIES_URL = "http://wa-cws-op.bom.gov.au/web/forecastChecker/activeSites.cgi?include_vw_name=1"
CONFIG_SITES_URL = "http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=list_json"
EXCLUSION_SITES_URL = "http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=exclusion"
BASE_DIR = "/cws/op/webapps/er_ml_projects/davink/amphitrite"
LOG_FILE = os.path.join(BASE_DIR,'sites_api.log')

logging.basicConfig(filename=LOG_FILE, level=logging.ERROR)

def handle_error(status_code, message):
    """Handle errors by logging and sending an appropriate response."""
    logging.error(message)
    print(f"Status: {status_code}")
    print("Content-Type: application/json")
    print()
    print(json.dumps({"success": False, "message": message}))
    sys.exit()

def load():
    """Load up a dataframe of sites from the ofcast active sites"""
    try:
        s = requests.get(ACTIVE_STIES_URL,verify=False).content
        df = pd.read_csv(StringIO(s.decode('utf-8')))

        #remove values that are not owned by a shift, ie: there is no "(D?)" in the name
        df = df[df['ofcastName'].str.contains("\(")]
        df['name'] = df['ofcastName'].map(lambda n: n.split(' (')[0])
        
        return df
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")
        
def load_json():
    """Spit it all the site out in json"""
    try: 
        df = load()
        df = df.sort_values(by='name')
    
        return df.to_json(orient='records')
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")
        
def get_active_partition_names():
    """Return all active sits in json"""
    try:
        # Fetch site configurations
        config_sites_response = requests.get(CONFIG_SITES_URL, verify=False)
        config_sites_df = pd.DataFrame(config_sites_response.json())
        config_sites_df = config_sites_df.transpose()                               
        config_sites_df = config_sites_df.reset_index()
        config_sites_df = config_sites_df.rename(columns={"index": "name"})

        # Fetch exclusion sites
        exclusion_sites_response = requests.get(EXCLUSION_SITES_URL, verify=False)
        exclusion_sites_df = pd.DataFrame(exclusion_sites_response.json())
        exclusion_sites_df = exclusion_sites_df.transpose()                               
        exclusion_sites_df = exclusion_sites_df.reset_index(drop=True)
        
        # Compare active sites with site configurations
        in_config_not_in_excluded = set(config_sites_df['name']) - set(exclusion_sites_df['name'])       
        
        return json.dumps(list(in_config_not_in_excluded))
    
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")
            
def get_html_sites():
    """Return site titles with lat lon"""
    try: 
        site_dict = {}
        json_data = load_json()
        all_info = json.loads(json_data)
    
        for i,site in enumerate(all_info):
            site_dict[site['name']] = site['name'] + ': ' + str(site['lat']) + ',' + str(site['lon'])
            print('{}<br>'.format(site_dict[site['name']]))    
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")
            
def get_json_sites():
    """Return site titles in json"""
    try: 
        site_dict = {}
        json_data = json.loads(load_json())
        
        for i,site in enumerate(json_data):
            site_dict[site["name"]] = {"name": site["name"], "lat": site["lat"], "lon": site["lon"]}
        
        return site_dict
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")
        
def compare_sites_and_config():
    """Compare the results of the active sites and the config file."""
    try:
        # Fetch active sites
        active_sites_df = load()
        active_sites_df = active_sites_df[["name", "lat", "lon"]]
        
        # Fetch site configurations
        config_sites_response = requests.get(CONFIG_SITES_URL, verify=False)
        config_sites_df = pd.DataFrame(config_sites_response.json())
        config_sites_df = config_sites_df.transpose()                               
        config_sites_df = config_sites_df.reset_index()
        config_sites_df = config_sites_df.rename(columns={"index": "name"})

        # Fetch exclusion sites
        exclusion_sites_response = requests.get(EXCLUSION_SITES_URL, verify=False)
        exclusion_sites_df = pd.DataFrame(exclusion_sites_response.json())
        exclusion_sites_df = exclusion_sites_df.transpose()                               
        exclusion_sites_df = exclusion_sites_df.reset_index(drop=True)
        
        # Compare active sites with site configurations
        in_active_not_in_config = set(active_sites_df['name']) - set(config_sites_df['name'])
        in_config_not_in_active = set(config_sites_df['name']) - set(active_sites_df['name'])
        in_active_not_excluded = in_active_not_in_config - set(exclusion_sites_df['name'])
        
        # CSS for centering table headers and highlighting rows
        styles = "<style>th { text-align: center; } .highlight { background-color: #ffff99; }</style>"

        # Start HTML output
        print("<html><head>")
        print(styles)  # Include the CSS style in the head
        print("</head><body>")

        # Print the tables side by side at the top with horizontal centering
        print("<table style='margin-left: auto; margin-right: auto;'>")

        # Active Sites Table
        print("<tr>")
        print("<td style='vertical-align: top; padding-right: 20px;'><h2 style='text-align:center'>Active Sites</h2>")
        print(active_sites_df.to_html(index=False))
        print("</td>")
        
        # Site Configurations Table
        print("<td style='vertical-align: top; padding-left: 20px;'><h2 style='text-align:center'>Site Configurations</h2>")
        print(config_sites_df.to_html(index=False))
        print("</td>")

        # Nested table for differences with highlights
        print("<td style='vertical-align: top; padding-left: 20px;'>")
        print("<h2 style='text-align:center'>&nbsp;</h2>")
        print("<table>")

        # Convert DataFrame to HTML
        in_active_not_excluded_df = pd.DataFrame(list(in_active_not_excluded), columns=['Site'])
        table_html = in_active_not_excluded_df.to_html(index=False)

        # Post-process HTML to add highlighting
        table_empty = len(in_active_not_excluded_df.index.values) < 1
        if table_empty:
            # 'In Active Sites but Not in Config' Table with highlights
            print("<tr><td style='vertical-align: top; padding-left: 20px;'><h3 style='text-align:center'>")
            normal_th = f"<th>Site</th>"
            highlighted_th = f"<th style='background: lightgreen;'/>Site config and exclusions up to date!</th>"
            table_html = table_html.replace(normal_th, highlighted_th)
            print(table_html)
            print("</td></tr>")

        else:
            for site in in_active_not_excluded:
                if site not in exclusion_sites_df["name"].values:
                    # Replace exact match of the row with highlighted version
                    normal_row = f'<tr>\n      <td>{site}</td>\n    </tr>'
                    highlighted_row = f'<tr class="highlight">\n      <td>{site}</td>\n    </tr>'
                    table_html = table_html.replace(normal_row, highlighted_row)
                    
                    # 'In Active Sites but Not in Config' Table with highlights
                    print("<tr><td style='vertical-align: top; padding-left: 20px;'><h3 style='text-align:center'>Active Sites Not excluded</h3>")
                    print(table_html)
                    print("</td></tr>")


        # 'In Config but Not in Active Sites' Table
        print("<tr><td style='vertical-align:top; padding-top: 20px; padding-left: 20px;'><h3 style='text-align:center'>Excluded from Active Sites</h3>")
        # print(pd.DataFrame(list(in_config_not_in_active), columns=['Site']).to_html(index=False))
        print(exclusion_sites_df.to_html(index=False))
        print("</td></tr>")

        print("</table>")
        print("</td>")
        
        print("</tr>")
        print("</table>")

        print("</body></html>")

    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")
        
def get_json_tables():
    """Return aswave tables in json"""
    try: 
        file_name = "nc_table_names.txt"
        df = pd.read_csv(file_name, names=["name", "lat", "lon"])
        df = df.sort_values(by="name")
        json = df.to_json(orient='records')
        
        return json
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")
        
def get_html_tables():
    """Return site titles with lat lon"""
    try: 
        site_dict = {}
        file_name = "nc_table_names.txt"
        df = pd.read_csv(file_name, names=["name", "lat", "lon"])
        df = df.sort_values(by="name")
        
        json_data = json.loads(df.to_json(orient="records"))
        
        for i,site in enumerate(json_data):
            site_dict[site['name']] = site['name'] + ': ' + str(site['lat']) + ',' + str(site['lon'])
            print('{}<br>'.format(site_dict[site['name']]))    
    except Exception as e:
        handle_error(500, f"Internal Server Error: {e}")
        
def main():
    # Parse the parameters
    form = cgi.FieldStorage()
    get = form.getvalue("get", "html")

    # Check if site_name is 'list' to list all sites as links
    if "json_sites" in get.lower():
        # Set the HTTP header for JSON content
        print("Content-Type: application/json")
        print()
        print(get_json_sites())
    
    elif "json_tables" in get.lower():
        # Set the HTTP header for JSON content
        print("Content-Type: application/json")
        print()
        print(get_json_tables())
    
    elif "html_sites" in get.lower(): 
        print("Content-Type: text/html")
        print()
        get_html_sites()
    
    elif "compare" in get.lower(): 
        print("Content-Type: text/html")
        print()
        compare_sites_and_config()
    
    elif "active_sites" in get.lower(): 
        print("Content-Type: application/json")
        print()
        print(get_active_partition_names())
    
    else: 
        print("Content-Type: text/html")
        print()
        get_html_tables()
           
if __name__ == "__main__":
    main()
