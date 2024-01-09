#!/cws/anaconda/envs/mlenv/bin/python -W ignore

print("Content-Type: text/html\n")

import autoseas.autoSeas as autoSeas
import json, sys, os
import cgi, cgitb; cgitb.enable()

# Default, if not set, is 1 decimal place
HT_DECIMAL_PLACES = {
    "Barrow Island 7 Day - AusWaveBWI".replace(' ', '_'): 2
    }

def jsonAutoSeas(**kwargs):

    if 'winds' not in kwargs:
        kwargs['winds'] = "360/10/3,330/20/3,330/20/3,330/20/9,330/20/9,330/20/9,330/20/9,330/20/9,330/20/9"

    if 'site' not in kwargs:
        kwargs['site'] = 'Woodside_-_Mermaid_Sound_7_days'
        
    # check for fetch table
    fetchFile = "autoseas/fetchLimits/"+ kwargs['site'] +".csv"
    if not os.path.exists(fetchFile):
        j = json.dumps({'error 1': "Fetch Limis for '{}' doesn't exist. Create a new site with the following name.".format(kwargs['site']), 'site': kwargs['site']})

    else:

        maxFetch = float(kwargs.get('maxFetch', autoSeas.MAX_FETCH))
        firstSeas = kwargs.get('firstSeas', 0)

        windWeights = kwargs.get('windWeights', '0.25,0.75')
        windWeights = [float(w) for w in windWeights.split(',')]

        averageFetch = kwargs.get('averageFetch', True)
        varyDecreaseFactors = kwargs.get('varyDecreaseFactors', False)

        returnDir = kwargs.get('returnDir', 0)
        returnDir = int(returnDir) > 0

        returnPdDir = kwargs.get('returnPdDir', 0)
        returnPdDir = int(returnPdDir) > 0
        
        calcType = kwargs.get('type')

        debug = kwargs.get('debug', False)

        showTable = kwargs.get('showTable', False)

        if debug or showTable:
            print("<span style='font-size: 11px'>")

        if showTable:
            autoSeas.SHOW_TABLE = True
            print("<pre>")

        if kwargs['winds'] == '':
            # no winds
            exit()

        winds = []
        for w in kwargs['winds'].split(','):
            w = w.split('/')
            if w[0] != "NaN":
                winds.append((float(w[0]), float(w[1]), int(w[2])))

        seas = autoSeas.autoSeas(kwargs['site'], winds, firstSeas, maxFetch,
                                 windWeights=windWeights,
                                 debug=debug,
                                 returnDir=returnDir,
                                 returnPdDir=returnPdDir,
                                 calcType=calcType,
                                 averageFetch=averageFetch,
                                 varyDecreaseFactors=varyDecreaseFactors)

        ht_places = HT_DECIMAL_PLACES.get(kwargs['site'], 1)

        if returnDir:
            seas = [[round(s, ht_places), int(round(d))] for s, d in seas]
        elif returnPdDir:
            seas = [[round(s, ht_places), int(round(pd)), int(round(d))] for s, pd, d in seas]    
        else:
            seas = [round(s, ht_places) for s in seas]

        j = json.dumps({'seas': seas})

    if 'callback' in kwargs:
        j = "{}({})".format(kwargs['callback'], j)

    print(j)


if __name__ == "__main__":

    q = cgi.FieldStorage()
    keys = q.keys()

    kwargs = {
        key: q.getvalue(key)
        for key in keys
    }

    jsonAutoSeas(**kwargs)