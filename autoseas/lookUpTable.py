import numpy as np
import csv
from scipy.ndimage import map_coordinates

def loadTable(fileName):

    table = {}
    first = True

    cols = None
    rows = []
    
    data = []

    with open(fileName, mode='r') as csvfile:
        reader = csv.reader(csvfile, delimiter=',', quotechar='"')
        for r in reader:
            if first:
                # get the cols
                first = False
                cols = [float(n) for n in r[1:]]
                
            else:
                rows.append(int(r[0]))
                data.append([float(n) for n in r[1:]])

    return {'cols': cols, 'rows': rows, 'data': data}


def indice(data, value):
    """Assumes data is sorted."""
    i0 = -1
    i1 = -1
    
    #print value, data 
    
    for i, d in enumerate(data):
        if d == value:
            return float(i)

        elif d > value:
            i0 = i - 1
            i1 = i
            break
        
    #print i0, i1
    
    if i0 < 0:
        return float(len(data) - 1)
        
    # get the fraction between the indicies
    diff = float(value - data[i0])
    r = float(data[i1] - data[i0])
    fraction = diff / r
    
    #print "range", r
    #print "diff", diff
    #print "fraction", fraction
            
    return i0 + fraction


def valueFromTable(table, rowVal, colVal):
    
    #print rowVal, colVal
    
    rowIndex = -1

    rowIndex = indice(table['rows'], rowVal)
    colIndex = indice(table['cols'], colVal)

    #print rowIndex, colIndex
    #print table['data']

    val = map_coordinates(table['data'], [[rowIndex], [colIndex]], order=1)

    #print rowVal, colVal, val

    return val[0]
