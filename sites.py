import os
from datetime import datetime, timedelta
import pandas as pd
import requests
import io

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

if __name__ == "__main__":

     print(load_json())
