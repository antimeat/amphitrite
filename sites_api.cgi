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
import io

URL = "http://wa-cws-op.bom.gov.au/web/forecastChecker/activeSites.cgi?include_vw_name=1"

def load():
    """Load up a dataframe of sites from the ofcast active sites"""
    s = requests.get(URL,verify=False).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))

    #remove values that are not owned by a shift, ie: there is no "(D?)" in the name
    df = df[df['ofcastName'].str.contains("\(")]
    df['name'] = df['ofcastName'].map(lambda n: n.split(' (')[0])
    
    return df

def load_json():
    """Spit it all the site out in json"""
    df = load()
    df = df.sort_values(by='name')

    return df.to_json(orient='records')

def get_html_titles():
    """Return site titles with lat lon"""
    site_dict = {}
    json_data = load_json()
    all_info = json.loads(json_data)

    for i,site in enumerate(all_info):
        site_dict[site['name']] = site['name'] + ': ' + str(site['lat']) + ',' + str(site['lon'])
        print('{}<br>'.format(site_dict[site['name']]))    
    
def get_json_titles():
    """Return site titles in json"""
    site_dict = {}
    json_data = json.loads(load_json())
    
    for i,site in enumerate(json_data):
        site_dict[site["name"]] = {"name": site["name"], "lat": site["lat"], "lon": site["lon"]}
    
    return site_dict

def main():
    # Parse the parameters
    form = cgi.FieldStorage()
    get = form.getvalue("get", "html")

    # Check if site_name is 'list' to list all sites as links
    if get == 'html':
        print("Content-Type: text/html")
        print()
        print(get_html_titles())
    else:
        # Set the HTTP header for JSON content
        print("Content-Type: application/json")
        print()
        print(get_json_titles())
        
if __name__ == "__main__":
    main()
