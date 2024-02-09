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

cgitb.enable()

# Function to calculate directional difference
def directional_difference(angle1, angle2):
    diff = abs(angle1 - angle2) % 360
    return min(diff, 360 - diff)

def calculate_differences(original_data, compared_data):
    # Extract "seas" lists from the input dictionaries
    original_seas = original_data["seas"]
    compared_seas = compared_data["seas"]
    
    # Calculate differences
    return [(abs(float(o[0]) - float(c[0])), abs(float(o[1]) - float(c[1])), directional_difference(float(o[2]), float(c[2]))) for o, c in zip(original_seas, compared_seas)]

def generate_comparison_table(differences, algorithm_name):
    html = f"<h2>Comparison: Original vs. {algorithm_name}</h2>"
    html += "<table border='1'><tr><th>Significant Wave Height Difference (m)</th><th>Period Difference (s)</th><th>Directional Difference (degrees)</th></tr>"
    for diff in differences:
        hs_diff, period_diff, dir_diff = diff
        html += f"<tr><td>{hs_diff:.2f}</td><td>{period_diff}</td><td>{dir_diff}</td></tr>"
    html += "</table>"
    return html

def call_autoseas(params):
    # Path to the original CGI script
    url = 'http://wa-vw-er/webapps/er_ml_projects/davink/amphitrite/autoseas.cgi'
    
    # Convert params dictionary to URL-encoded string
    # Assuming params is a dictionary
    try:
        # Make a POST request
        response = requests.post(url, data=params)
        
        # Check if the request was successful
        if response.status_code == 200:
            return json.loads(response.text)
        else:
            return json.dumps({'error': f'Failed to fetch data. Status code: {response.status_code}'})
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
            wind_str = '/'.join(str(item) for sublist in wind_list for item in sublist)

            # wind_list.replace(" ","").replace("[","").replace("]","").replace(",","/") 
            # wind_str = [wind for sublist in wind_list for item in sublist]

            return wind_str
        else:
            return json.dumps({'error': f'Failed to fetch data. Status code: {response.status_code}'})
    except requests.exceptions.RequestException as e:
        # Handle connection errors
        return json.dumps({'error': 'Failed to connect to the original CGI script.'})

def get_cgi_params():
    
    form = cgi.FieldStorage()
    params = {}
    for key in form.keys():
        params[key] = form.getvalue(key)
    return params

def fetch_algorithm_data(algo, params):
    
    # Adjust params to specify the algorithm if necessary
    params['src'] = "autoseas" 
    params['type'] = algo 
    
    return call_autoseas(params)

def main():
    print_headers()
    params = get_cgi_params()
    
    #first lets get some forecast winds
    # winds = get_ofcast_winds(params)
    
    # Fetch new algorithm data
    algo = "breugen-hothuijsen"
    original_data = fetch_algorithm_data(algo, params)
    
    # Algorithms to compare
    algorithms = ['bretschneider', 'shallow']
    
    # Store HTML tables
    comparison_tables = []
    
    for algo in algorithms:
        # Fetch algorithm data
        alg_data = fetch_algorithm_data(algo, params)
        
        # Calculate differences (implement this based on your data structure)
        differences = calculate_differences(original_data, alg_data)
        
        # Generate comparison table
        comparison_table = generate_comparison_table(differences, algo)
        comparison_tables.append(comparison_table)
    
    # Output HTML
    print("<html><body>")
    for table in comparison_tables:
        print(table)
    print("</body></html>")
    
def print_headers():
    print("Content-Type: text/html")
    print("Access-Control-Allow-Origin: *\n")

if __name__ == "__main__":
    main()
