#!/cws/anaconda/envs/mlenv/bin/python -W ignore
import autoseas.auto_seas as auto_seas
import partition_smusher as smusher
import datetime
import pandas as pd
import json
import os
import urllib.parse
import cgi
import cgitb
import amphitrite_configs as configs
cgitb.enable()

# Constants
HT_DECIMAL_PLACES = {
    "Barrow Island 7 Day - AusWaveBWI".replace(' ', '_'): 2
}
DEFAULT_WINDS = "330/10/3,330/20/3,330/20/3,330/20/3,330/20/3,330/20/3,330/20/3,330/20/3,330/20/3"
DEFAULT_SITE = 'Woodside - Scarborough 10 Days'
BASE_DIR = configs.BASE_DIR
FETCH_DIR = os.path.join(BASE_DIR,"autoseas/fetchLimits/")

def transform_site_name(site_name):
    """Reformat the site name to api friendly"""
    site_name = site_name.replace(" ","_")
    return site_name
    
def get_request_parameters(required_params):
    """Decode URL-encoded strings and validate required parameters.
    Args:
        required_params (list): A list of strings representing required parameter names.
    Returns:
        dict: Parameters extracted from the request.
    Raises:
        ValueError: If a required parameter is missing.
    """
    field_storage = cgi.FieldStorage()
    params = {}
    for key in field_storage.keys():
        value = field_storage.getvalue(key)
        if isinstance(value, str):
            value = urllib.parse.unquote(value)
        params[key] = value

    # Check for missing required parameters
    for param in required_params:
        if param not in params or not params[param]:
            raise ValueError(f"missing parameter required: {param}")

    return params

def fetch_table_exists(site):
    fetch_file = f"{FETCH_DIR}{site}.csv"
    fetch_file = transform_site_name(fetch_file)
    return os.path.exists(fetch_file)

def parse_winds(wind_string):
    winds = []
    for wind in wind_string.split(','):
        direction, speed, duration = wind.split('/')
        if direction != "NaN":
            if (direction != '' and speed != ''):
                winds.append((float(direction), float(speed), int(duration)))
            else:
                winds.append((0, 0, 0))
    return winds

def calculate_seas(kwargs):
    source = kwargs.get('src', "smush")
    site = kwargs.get('site', DEFAULT_SITE).replace(' ', '_')
    winds = parse_winds(kwargs.get('winds', DEFAULT_WINDS))
    max_fetch = float(kwargs.get('maxFetch', auto_seas.MAX_FETCH))
    first_seas = int(kwargs.get('firstSeas', 0))
    wind_weights = [float(w) for w in kwargs.get('windWeights', '0.25,0.75').split(',')]
    return_dir = kwargs.get('returnDir', '0') != '0'
    return_pd_dir = kwargs.get('returnPdDir', '1') != '0'

    
    seas = auto_seas.autoSeas(
        site, 
        winds, 
        src=source, 
        firstSeas=first_seas, 
        maxFetch=max_fetch,
        windWeights=wind_weights,
        debug=kwargs.get('debug', False),
        returnDir=return_dir,
        returnPdDir=return_pd_dir,
        calcType=kwargs.get('type'),
        averageFetch=kwargs.get('averageFetch', True),
        varyDecreaseFactors=kwargs.get('varyDecreaseFactors', False)
    )
    
    return seas, return_dir, return_pd_dir

def format_seas_data(seas, site_name, return_dir, return_pd_dir):
    """just round some stuff correctly please"""
    ht_places = HT_DECIMAL_PLACES.get(site_name, 1)
    
    if return_dir:
        return [[round(s, ht_places), int(round(d))] for s, d in seas]
    elif return_pd_dir:
        return [[round(s, ht_places), int(round(pd)), int(round(d))] for s, pd, d in seas]
    return [round(s, ht_places) for s in seas]

def main():
    
    # Define required parameters
    required_params = ['site', 'winds', 'src', 'first_time_step']

    try:
        # Attempt to get and validate request parameters
        kwargs = get_request_parameters(required_params)
        # Further processing...
    except ValueError as e:
        # If a required parameter is missing, return an error response
        response = {"success": False, "message": str(e)}
        print_error(response)
        exit(0)
    
    #process required params
    winds = parse_winds(kwargs.get('winds'))
    site_name = kwargs.get('site')
    time_step_str = kwargs.get("first_time_step")
    first_time_step = datetime.datetime.strptime(time_step_str, "%Y%m%d%H")
    source = kwargs.get("src", "autoseas")
    
    #optional params
    calc_type = kwargs.get("type","new")
    return_dir = kwargs.get('returnDir', '0') != '0'
    return_pd_dir = kwargs.get('returnPdDir', '1') != '0'
    
    #work out what we want to do ["autoseas","smush","partition"]        
    #cant do much without a depth and fetch table however
    if not fetch_table_exists(site_name):
        print_error(site_name)
        exit(0)
        
    # lets go smushing
    if "smush" in source:
    
        #dataframe needed for smushing
        df_wind = pd.DataFrame(winds, columns=["wind_dir", "wind_spd", "diff"])
    
        #now we need to create a datetimeindex for our df_wind from first_time_step
        # Create a TimedeltaIndex from the 'diff' column, offsetting the first value
        time_deltas = pd.to_timedelta(df_wind['diff'], unit='h')
        time_deltas.iloc[0] = pd.to_timedelta(0, unit='h')

        # Generate the DateTimeIndex by adding the cumulative sum of time deltas to the first time step
        datetime_index = first_time_step + time_deltas.cumsum()

        # Assign the DateTimeIndex to your DataFrame and name it
        df_wind.index = datetime_index
        df_wind.index.name = "time[UTC]"
        
        #lets now do some smushing of partition and autoseas from df_wind
        smush_box = smusher.PartitionSmusher(site_name,first_time_step,df_wind.index)
        seas_df = smush_box.smush_seas(site_name,df_wind,calc_type)
        seas = seas_df.values.tolist()
        formatted_seas = format_seas_data(seas, site_name, return_dir, return_pd_dir)
        
        response = {'seas': formatted_seas}
    
    # just the raw partion please    
    elif "autoseas" in source:
        site_name = transform_site_name(site_name)
        seas, return_dir, return_pd_dir = calculate_seas(kwargs)
        formatted_seas = format_seas_data(seas, site_name, return_dir, return_pd_dir)
        response = {'seas': formatted_seas}
        
    # else we do default autoseas calcs    
    else:
        
        #dataframe needed for smushing
        df_wind = pd.DataFrame(winds, columns=["wind_dir", "wind_spd", "diff"])
    
        #now we need to create a datetimeindex for our df_wind from first_time_step
        # Create a TimedeltaIndex from the 'diff' column, offsetting the first value
        time_deltas = pd.to_timedelta(df_wind['diff'], unit='h')
        time_deltas.iloc[0] = pd.to_timedelta(0, unit='h')

        # Generate the DateTimeIndex by adding the cumulative sum of time deltas to the first time step
        datetime_index = first_time_step + time_deltas.cumsum()
        
        # Assign the DateTimeIndex to your DataFrame and name it
        df_wind.index = datetime_index
        df_wind.index.name = "time[UTC]"
        
        #lets now get the partition
        smush_box = smusher.PartitionSmusher(site_name,first_time_step,df_wind.index)
        seas_df = smush_box.get_seas_partition_timeadjusted_df(site_name)
        seas = seas_df.values.tolist()
        formatted_seas = format_seas_data(seas, site_name, return_dir, return_pd_dir)
        
        response = {'seas': formatted_seas}
    
    if 'callback' in kwargs:
        response = f"{kwargs['callback']}({json.dumps(response)})"
        
    print_headers()
    print(json.dumps(response))

def print_error(response):
    print("Status: 404 Not Found")  
    print_headers()
    
    response = {
        'error': f"Fetch Limits failed: '{response}'."
    }

    print(json.dumps(response))
        
def print_headers():
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: POST, GET, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type\n")
   

if __name__ == "__main__":
    main()
