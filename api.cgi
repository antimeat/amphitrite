#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Script for extracting images from a web directory and returning image names as a JSON response.
"""
__author__ = "Daz Vink"
__date__ = "2023-11-14"

from datetime import datetime,timedelta
import json
import os
import sys
import cgi
import sys
import database as db

def main():
    
    # Set the HTTP header for JSON content
    print("Content-Type: application/json")
    print("Access-Control-Allow-Origin: *") 
    print("Access-Control-Allow-Methods: GET, POST, OPTIONS")
    print("Access-Control-Allow-Headers: Content-Type") 
    print()
    
    # Parse the parameters
    form = cgi.FieldStorage()
    site_name = form.getvalue('site_name',"Woodside - Pluto 10 days")
    run_time = form.getvalue('run_time',None)
    
    #Create instance of your class
    result = None

    # if we dont have a run_time get the latest
    if run_time:
        result = db.get_wavetable_from_db(site_name,run_time)
    else:
        result = db.get_wavetable_from_db(site_name)
        
    # Print the result as JSON
    print(result["data"])
    # print(json.dumps({"data":"<h1>THis is a test</h1>"}))

if __name__ == "__main__":
    main()