#!/cws/anaconda/envs/mlenv/bin/python -W ignore

# Load forecast winds from ofcast.
# get_winds.cgi

import json
import numpy as np
import pandas as pd
import ofcast_archived as ofcast

import cgi, cgitb
cgitb.enable()


def getForecastWinds(**kwargs):
    """
    Retrieves forecast wind data, calculates the time difference between consecutive rows, and returns it as a JSON object.

    Keyword Arguments:
        sessionID (str): User session ID.
        fName (str): Forecast name.
        achive (int): is number previous issues to get (0 = current)
        data_type (str): either forecast data of the model data contained in the form

    Returns:
        None, but prints a JSON object representing the retrieved wind data.
    """
    #setup some defaults if not passed
    sessionID = kwargs.get("sessionID", "davink46641")
    fName = kwargs.get("fName", "Woodside - Mermaid Sound 5 days")
    archive = kwargs.get("archive", 0)
    data_type = kwargs.get("data_type", "forecast")
    server = kwargs.get("server", "op")
    df = None
    
    #attempt to get forecast winds from ofcast
    try:
        df = ofcast.load_archive(sessionID, server, fName, archive, data_type)
        
        if df is None:
            raise Exception("No sessionID")
        
        # find time diff with previous row
        df['time_diff'] = (df['time_local'] - df['time_local'].shift()) / np.timedelta64(1, 'h')

        df['time_diff'] = df['time_diff'].fillna(0).astype(int)

        # reorder columns so it matches the desired output
        df = df[['wnd_dir', 'wnd_spd', 'time_diff']]
        
        #print out in the format "dir/spd/previous_hr,"
        winds = df.values.tolist()
        print(json.dumps(winds))

    #return a defualt string of winds useful for testing
    except: 
        json_winds = [[230, 6, 3], [270, 10, 3], [300, 11, 3], [290, 15, 3], [270, 12, 3], [250, 13, 3], [250, 11, 3], [270, 8, 3], [280, 6, 3], [290, 8, 3], [320, 15, 3], [310, 16, 3], [280, 15, 3], [260, 9, 3], [260, 10, 3], [320, 7, 3], [290, 10, 3], [340, 11, 3], [330, 13, 3], [290, 11, 3], [310, 13, 3], [300, 12, 3], [280, 12, 3], [340, 9, 3], [340, 7, 3], [330, 9, 3], [320, 12, 3], [310, 10, 3], [310, 10, 3], [290, 9, 3], [270, 5, 3], [300, 6, 3], [290, 12, 3], [280, 8, 3], [310, 10, 3], [290, 10, 3], [280, 11, 3], [280, 10, 3], [260, 10, 3], [240, 8, 3], [220, 7, 3], [280, 10, 3], [290, 14, 3], [270, 14, 3], [270, 12, 3], [260, 12, 3], [250, 13, 3], [260, 12, 3], [250, 12, 3], [260, 15, 3], [270, 17, 3], [270, 16, 3], [270, 14, 3], [260, 14, 3], [260, 14, 3], [250, 14, 3], [260, 13, 3], [270, 14, 3], [280, 16, 3], [270, 18, 3], [250, 18, 3]]
        print(json.dumps(json_winds))

def get_gfeWinds(**kwargs):
    """
    Retrieves GFE wind data, calculates the time difference between consecutive rows, and returns it as a JSON object.

    Keyword Arguments:
        sessionID (str): User session ID.
        fName (str): Forecast name.
        achive (int): is number previous issues to get (0 = current)
        data_type (str): either forecast data of the model data contained in the form

    Returns:
        None, but prints a JSON object representing the retrieved wind data.
    """
    #setup some defaults if not passed
    sessionID = kwargs.get("sessionID", "davink83142")
    fName = kwargs.get("fName", "Woodside - Mermaid Sound 7 days")
    archive = kwargs.get("archive", 0)
    data_type = kwargs.get("data_type", "forecast")
    server = kwargs.get("server", "dev")
    
    #get winds from GFE output csv file
    file_dir = '/srv/local/web/vulture/gfe_data/point_data/'
    file_name = 'latest_prac.csv'
    
    #read in the csv point data from GFE
    df_all = pd.read_csv(file_dir + file_name)
    df_all = df_all.set_index('time')
    
    #get on the forecast name
    df = df_all[df_all['name'] == fName]
    
    grouped_df = df.groupby(['time','field']).mean()
    pivoted_df = grouped_df.pivot_table(values='value', index='time', columns='field')
    pivoted_df = pivoted_df.rename_axis('time')
    print(pivoted_df)
    
    pivoted_df = pivoted_df.apply(pd.to_numeric, errors='coerce')
    pivoted_df = pivoted_df.fillna(value=np.nan).replace([np.inf, -np.inf], np.nan).round(0).astype('Int64')
    
    #reorder columns so it matches the desired output
    df = pivoted_df.rename(columns={'Wind_Dir':'wnd_dir', 'Wind_Mag':'wnd_spd'})
    df['time_diff'] = 1
    df = df[['wnd_dir', 'wnd_spd', 'time_diff']]
    
    #print out in the format "dir/spd/previous_hr,"
    winds = df.values.tolist()
    wind_string = ','.join(['/'.join(map(str, item)) for item in winds])
                   
    print(wind_string)    
    
def print_headers(content_type="application/json"):
    print(f"Content-Type: {content_type}")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: POST, GET, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type\n")
    
def main():

    print_headers("application/json")
    
    q = cgi.FieldStorage()
    keys = q.keys()

    kwargs = {
        key: q.getvalue(key)
        for key in keys
    }

    # print(kwargs)
    
    getForecastWinds(**kwargs)
    # getForecastWinds(**kwargs)

if __name__ == "__main__":
    
    main()