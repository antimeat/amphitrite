#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Comparision of autoseas algorithms for a given site
author: Daz Vink
date: 2023-11-14
"""

import json
import cgi
import cgitb
import requests
import datetime

cgitb.enable()

# Function to calculate directional difference
def directional_difference(angle1, angle2):
    diff = abs(angle1 - angle2) % 360
    return min(diff, 360 - diff)

def calculate_differences(original_data, compared_data):
    # Extract "seas" lists from the input dictionaries
    # Convert the JSON strings to dictionaries
    original_data_dict = json.loads(original_data)
    compared_data_dict = json.loads(compared_data)
    
    # Extract "seas" lists from the dictionaries
    original_seas = original_data_dict["seas"]
    compared_seas = compared_data_dict["seas"]
    
    # Calculate differences
    return [(abs(float(o[0]) - float(c[0])), abs(float(o[1]) - float(c[1])), directional_difference(float(o[2]), float(c[2]))) for o, c in zip(original_seas, compared_seas)]

def generate_comparison_table(differences, original_algo, algorithm_name):

    #formatting for the html table
    html = "<table border='1' style='border-collapse: collapse; width: 80%; margin-bottom: 20px;'>"

   # Table header for clarity
    html += "<thead style='background-color: #f2f2f2;'><tr>"
    html += f"<th colspan='3' style='text-align: center;'><h2>{original_algo} vs. {algorithm_name}</h2></th>"
    html += "</tr></thead>"
    
    # Second row for column titles
    html += "<tr>"
    html += "<th style='background-color: #f9f9f9;'>hs diff (m)</th>"
    html += "<th style='background-color: #f9f9f9;'>pd diff (s)</th>"
    html += "<th style='background-color: #f9f9f9;'>dir diff (degrees)</th>"
    html += "</tr></thead>"
    
    for diff in differences:
        hs_diff, period_diff, dir_diff = diff
        html += f"<tr><td>{hs_diff:.2f}</td><td>{period_diff}</td><td>{dir_diff}</td></tr>"
    html += "</table>"
    return html

def generate_wind_sea_table(winds, seas, algorithm_name):

    # Parse the JSON strings into Python lists
    winds_data = json.loads(winds)
    seas_data = json.loads(seas)
    
    # Ensure that we're working with the lists contained within the parsed JSON
    winds = winds_data.get('winds', [])
    seas = seas_data.get('seas', [])
    
    #formatting for the html table
    html = "<table border='1' style='border-collapse: collapse; width: 80%; margin-bottom: 20px;'>"

   # Table header for clarity
    html += "<thead style='background-color: #f2f2f2;'><tr>"
    html += f"<th colspan='4' style='text-align: center;'><h2>{algorithm_name}</h2></th>"
    html += "</tr></thead>"
    
    # Second row for column titles
    html += "<tr>"
    html += "<th style='background-color: #f9f9f9;'>winds</th>"
    html += "<th style='background-color: #f9f9f9;'>seas_hs (m)</th>"
    html += "<th style='background-color: #f9f9f9;'>seas_pd (s)</th>"
    html += "<th style='background-color: #f9f9f9;'>seas_dir (degrees)</th>"
    html += "</tr></thead>"
    
    for i,wind in enumerate(winds):
        seas_hs, seas_pd, seas_dir = seas[i]        
        html += f"<tr><td>{wind}</td><td>{seas_hs}</td><td>{seas_pd}</td><td>{seas_dir}</td></tr>"
    html += "</table>"
    return html

def call_autoseas(params):
    # Path to the original CGI script
    url = 'http://wa-vw-er.bom.gov.au/webapps/er_ml_projects/davink/amphitrite/autoseas.cgi'
    
    # Convert params dictionary to URL-encoded string
    # Assuming params is a dictionary
    try:
        # Make a POST request
        response = requests.post(url, data=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            return response.text
        else:
            print_error(params['site'])
            exit()
    except json.JSONDecodeError:
        # Handle the case where response is not JSON
        return {'error': 'The response is not in JSON format'}
    
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        return json.dumps({'error': 'Failed to connect to the original CGI script.'})

def get_ofcast_winds(params):
    """Get Ofcast winds. You need to pass site name and sessionID via the params dict
    Args:
        params (_dict_): parameters passed via post on the url

    Returns:
        _str_: list to string
    """
    # Path to CGI script
    url = "http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/autoseas/get_winds.cgi"
    
    params["get"] = "ofcast_archived"
    params["data_type"] = "forecast"
    params["fName"] = params["site"]
    
    # Convert params dictionary to URL-encoded string
    try:
        # Make a POST request
        response = requests.post(url, data=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            response_txt = response.text
            wind_list = json.loads(response_txt)
            
            # Flatten the list and convert it to a string in the desired format
            wind_str = ','.join('/'.join(map(str, sublist)) for sublist in wind_list)
                        
            return wind_str, json.dumps({"winds":wind_list})
        else:
            return json.dumps({'error': f'Failed to fetch data. Status code: {response.status_code}'})
    except requests.exceptions.RequestException as e:
        return json.dumps({'error': 'Failed to connect to the original CGI script.'})

def get_cgi_params():
    
    #midnight for the first time step
    midnight = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).strftime('%Y%m%d%H')
    
    form = cgi.FieldStorage()
    params = {}
    
    for key in form.keys():
        params[key] = form.getvalue(key)
    
    #default settings here
    params['site'] = form.getvalue('site',"Woodside - Mermaid Sound 7 days")
    params['first_time_step'] = form.getvalue('first_time_step',midnight)
    params['src'] = form.getvalue('src','partition')
    # params['sessionID'] = form.getvalue('sessionID',"_blah")
    # params['get'] = form.getvalue('get',"ofcast_archived")
    # params['data_type'] = form.getvalue('data_type',"forecast")
    # params['archive'] = form.getvalue('archive',"0")        
    
    return params

def fetch_algorithm_data(algo, params):
    
    # Adjust params to specify the algorithm if necessary
    params['src'] = "autoseas" 
    params['type'] = algo 
    
    return call_autoseas(params)

def main():
    params = get_cgi_params()
    site_name = params['site']
    
    #first lets get some forecast winds
    winds = get_ofcast_winds(params)
    params['winds'] = winds[0]
    
    # Fetch new algorithm data
    original_algo = "breugen-hothuijsen"
    original_data = fetch_algorithm_data(original_algo, params)
    
    # Algorithms to compare
    algorithms = ["breugen-hothuijsen", "bretschneider", "shallow"]
    
    # Store HTML tables
    comparison_tables = []
    wind_sea_tables = []
    
    for algo in algorithms:
        alg_data = fetch_algorithm_data(algo, params)
        wind_sea_table = generate_wind_sea_table(winds[1], alg_data, algo)
        wind_sea_tables.append(wind_sea_table)
    
        if original_algo != algo:
            # Calculate differences (implement this based on your data structure)
            differences = calculate_differences(original_data, alg_data)
            
            # Generate comparison table
            comparison_table = generate_comparison_table(differences, original_algo, algo)
            comparison_tables.append(comparison_table)
        
    # Output HTML with CSS for centered, side-by-side tables without gaps
    print_headers()
    print("<html><head><style>")
    print(".body { display: flex; justify-content: center; flex-wrap: nowrap; }")  # Center flex items and ensure no wrapping
    print(".table-container { display: flex; justify-content: center; flex-wrap: nowrap; }")  # Center flex items and ensure no wrapping
    print(".table-container > div { flex: 1; padding: 0; box-sizing: border-box; }")  # Use flex: 1 for equal width and remove padding
    print("table { width: 100%; margin: 0 auto; border-collapse: collapse; }")  # Center tables within their divs and remove margins
    print("</style></head><body>")
    
    print("<h1 class='body'>Comparison of autoseas algorithms</h1><hr>")
    print(f"<h2 class='body'>{site_name}</h2><hr>")
    
    #wind_sea_tables
    print("<div class='table-container'>")
    for table in wind_sea_tables:
        print(f"<div>{table}</div>")  # Each table is wrapped in a div for flex display
    print("</div>")

    print("<h1 class='body'><br>Difference tables</h1><hr>")

    #comparison tables
    print("<div class='table-container'>")
    for table in comparison_tables:
        print(f"<div>{table}</div>")  # Each table is wrapped in a div for flex display
    print("</div>")
    
    
    print("</body></html>")

def print_error(site_name):
    print("Status: 404 Not Found")  
    print("Content-Type: text/html")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: POST, GET, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type\n")
    
    response = {
        'error': f"Fetch Limits for '{site_name}' doesn't exist. Create new fetch - depth file for the site."
    }

    print(json.dumps(response))
    
def print_headers():
    print("Content-Type: text/html")
    print("Access-Control-Allow-Origin: *")
    print("Access-Control-Allow-Methods: POST, GET, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type\n")
    
if __name__ == "__main__":
    main()
