import os
from datetime import datetime, timedelta
import pandas as pd
import requests
import io

CONFIG_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'site_config.txt')
URL = "http://wa-cws-op.bom.gov.au/web/forecastChecker/activeSites.cgi?include_vw_name=1"
#URL = "http://wa-aifs-local.bom.gov.au/vulture/dev/activeSites.cgi?include_vw_name=1"

def load():
    '''Load up a dataframe of sites from the ofcast active sites'''
    
    s = requests.get(URL,verify=False).content
    df = pd.read_csv(io.StringIO(s.decode('utf-8')))

    #remove values that are not owned by a shift, ie: there is no "(D?)" in the name
    df = df[df['ofcastName'].str.contains("\(")]
    df['name'] = df['ofcastName'].map(lambda n: n.split(' (')[0])
    
    return df

def load_json():
    '''Spit it all the site out in json'''
    
    df = load()
    df = df.sort_values(by='name')

    return df.to_json(orient='records')


def load_json_from_config():
    """Load the site names from the config file"""
 
    site_names = []
    
    try:
        with open(CONFIG_FILE, 'r') as file:
            for line in file:
                #ignore blank lines and comments
                if line.strip() == '' or line.strip() == '\n' or line.startswith("#"):
                    continue
                
                # Capture site name at the start of the line
                parts = line.strip().split(',')
                site_names.append(parts[0].strip())
                
        df = pd.DataFrame(site_names, columns=['name'])
        df = df.sort_values(by='name')
            
        return df.to_json(orient='records')
            
    except Exception as e:
        return str(e)

if __name__ == "__main__":

     print(load_json_from_config())
