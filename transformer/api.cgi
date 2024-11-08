#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import cgi
import cgitb
import json

import sites

cgitb.enable()

print("Content-Type: text/html\n")

q = cgi.FieldStorage()

get = q.getvalue('get', 'sites_from_config')

if get == 'sites':

    print(sites.load_json())

elif get == 'titles':
    
    site_dict = {}
    all_info = json.loads(sites.load_json())

    for i,site in enumerate(all_info):
        site_dict[site['name']] = site['name'] + ': ' + str(site['lat']) + ',' + str(site['lon'])
        print('{}<br>'.format(site_dict[site['name']]))

    #print(json.dumps(site_dict))    

elif get == 'sites_from_config':
    
    print(sites.load_json_from_config())

