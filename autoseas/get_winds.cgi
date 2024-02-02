#!/cws/anaconda/envs/mlenv/bin/python -W ignore

print("Content-Type: application/json\n")

# Load forecast winds from ofcast.
# Print json for [[dirn, spd, hours since previous], ...]

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
    sessionID = kwargs.get("sessionID", "davink83142")
    fName = kwargs.get("fName", "Woodside - Mermaid Sound 7 days")
    archive = kwargs.get("archive", 0)
    data_type = kwargs.get("data_type", "forecast")
    
    df = ofcast.load_archive(sessionID, fName, archive, data_type)

    # find time diff with previous row
    df['time_diff'] = (df['time_local'] - df['time_local'].shift()) / np.timedelta64(1, 'h')

    df['time_diff'] = df['time_diff'].fillna(0).astype(int)

    # reorder columns so it matches the desired output
    df = df[['wnd_dir', 'wnd_spd', 'time_diff']]
    
    #print out in the format "dir/spd/previous_hr,"
    winds = df.values.tolist()
    # wind_string = ','.join(['/'.join(map(str, item)) for item in winds])
                   
    # print(wind_string)    

    # #json_string = json.dumps(['/'.join(map(str, item)) for item in winds])
    print(json.dumps(winds))

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
    
if __name__ == "__main__":
    
    q = cgi.FieldStorage()
    keys = q.keys()

    kwargs = {
        key: q.getvalue(key)
        for key in keys
    }

    # print(kwargs)
    
    getForecastWinds(**kwargs)
    # getForecastWinds(**kwargs)
