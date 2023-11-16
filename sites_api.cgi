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

ACTIVE_STIES_URL = "http://wa-cws-op.bom.gov.au/web/forecastChecker/activeSites.cgi?include_vw_name=1"
CONFIG_SITES_URL = "http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/api.cgi?get=list_json"

def load():
    """Load up a dataframe of sites from the ofcast active sites"""
    s = requests.get(ACTIVE_STIES_URL,verify=False).content
    df = pd.read_csv(StringIO(s.decode('utf-8')))

    #remove values that are not owned by a shift, ie: there is no "(D?)" in the name
    df = df[df['ofcastName'].str.contains("\(")]
    df['name'] = df['ofcastName'].map(lambda n: n.split(' (')[0])
    
    return df

def load_json():
    """Spit it all the site out in json"""
    df = load()
    df = df.sort_values(by='name')
    
    return df.to_json(orient='records')

def get_html_sites():
    """Return site titles with lat lon"""
    site_dict = {}
    json_data = load_json()
    all_info = json.loads(json_data)
   
    for i,site in enumerate(all_info):
        site_dict[site['name']] = site['name'] + ': ' + str(site['lat']) + ',' + str(site['lon'])
        print('{}<br>'.format(site_dict[site['name']]))    
    
def get_json_sites():
    """Return site titles in json"""
    site_dict = {}
    json_data = json.loads(load_json())
    
    for i,site in enumerate(json_data):
        site_dict[site["name"]] = {"name": site["name"], "lat": site["lat"], "lon": site["lon"]}
    
    return site_dict

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

        # Compare active sites with site configurations
        in_active_not_in_config = set(active_sites_df['name']) - set(config_sites_df['name'])
        in_config_not_in_active = set(config_sites_df['name']) - set(active_sites_df['name'])

        # Start HTML output
        print("<html><body>")

        # Print the tables side by side at the top with horizontal centering
        print("<table style='margin-left: auto; margin-right: auto;'><tr>")
        print("<td style='vertical-align: top; padding-right: 20px;'><h2>Active Sites</h2>")
        print(active_sites_df.to_html(index=False))
        print("</td><td style='vertical-align: top; padding-left: 20px;'><h2>Site Configurations</h2>")
        print(config_sites_df.to_html(index=False))
        print("</td></tr></table>")

        # Print differences
        print("<table style='margin-top: 20px; margin-left: auto; margin-right: auto;'><tr>")
        print("<td style='vertical-align: top; padding-right: 20px;'><h3>In Active Sites but Not in Config</h3>")
        print(pd.DataFrame(list(in_active_not_in_config), columns=['Site']).to_html(index=False))
        print("</td><td style='vertical-align: top; padding-left: 20px;'><h3>In Config but Not in Active Sites</h3>")
        print(pd.DataFrame(list(in_config_not_in_active), columns=['Site']).to_html(index=False))
        print("</td></tr></table>")

        # End HTML output
        print("</body></html>")

    except requests.RequestException as e:
        print(f"Request failed: {e}")


def get_json_tables():
    """Return aswave tables in json"""
    file_name = "nc_table_names.txt"
    df = pd.read_csv(file_name, names=["name", "lat", "lon"])
    df = df.sort_values(by="name")
    json = df.to_json(orient='records')
    
    return json

def get_html_tables():
    """Return site titles with lat lon"""
    site_dict = {}
    file_name = "nc_table_names.txt"
    df = pd.read_csv(file_name, names=["name", "lat", "lon"])
    df = df.sort_values(by="name")
    
    json_data = json.loads(df.to_json(orient="records"))
    
    for i,site in enumerate(json_data):
        site_dict[site['name']] = site['name'] + ': ' + str(site['lat']) + ',' + str(site['lon'])
        print('{}<br>'.format(site_dict[site['name']]))    

    
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
    
    else: 
        print("Content-Type: text/html")
        print()
        get_html_tables()
           
if __name__ == "__main__":
    main()
