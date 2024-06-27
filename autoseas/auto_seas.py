"""
Wind Speed in knots
Fetch Limits in nautical miles
Durations in hours
Author: Rabi Rivett
To Do
-----

- rate of decrease of seas by a percentage over time of the original amount... constant linear decrease
    - need to keep track of the seas when no longer forced
- 
"""
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import csv, math
from math import pi, cos, sin, atan2, radians
from autoseas.bretschneider import Bretschneider
from autoseas.shallowWaterSeas import ShallowWaterSeas
from autoseas.breugen_holthuijsen import BreugenHolthuijsen
from bisect import bisect_left

DEBUG = False

if DEBUG:
    print("\n\n\n\n\n\n\n\n\n\n\n")

SHOW_TABLE = False

FETCH_WEIGHTS = [0.2, 0.6, 0.2]
MAX_FETCH = 100  # 100km
MAX_DEPTH = 50  # 60km
MAX_DURATION = 36.0  # hours

DIRECTION_WEIGHTED_BIN_DELTAS = range(-8, 9, 1)

def cosSquaredSpeedAdjust(offset):
    """Reduce the wind speed for bins either side of the wind diration."""
    # no adjust
    angle = offset * 10.0
    adjust = (pow(cos(radians(angle)), 2))
    return adjust

    # 95%
    #return (20 - abs(offset)) / 20.0

DIRECTION_WEIGHTED_BIN_WEIGHTS = [cosSquaredSpeedAdjust(b) for b in DIRECTION_WEIGHTED_BIN_DELTAS]

BIN_DELTAS = [-2, -1, 0, 1, 2]
BIN_WEIGHTS = [1.0, 1.0, 1.0, 1.0, 1.0]

WINDS = [
    (200, 21),
    (190, 21),
    (180, 19),
    (170, 18),
    (170, 13),
    (200, 10),
    (240, 14),
    (240, 17),
    (230, 18),
    (230, 20),
    (220, 21),
    (210, 18),
    (210, 13),
    (230, 14),
    (240, 13),
    (230, 14),
    ]

#WINDS = WINDS[:6]

seaLimitsTable = None

def autoSeas(siteName, 
             winds,
             src="smush",
             firstSeas=0,
             maxFetch=MAX_FETCH,
             maxDuration=MAX_DURATION,
             windWeights=[0.25, 0.75],
             returnDir=False,
             returnPdDir=False,
             calcType='new',
             debug=False,
             averageFetch=True,
             varyDecreaseFactors=False,
             useDirectionWeights=True):
    """
    
    Parameters
    ----------
        windWeight : float
            Weight of final wind when doing a weighted average between previous and next.
    
    """
    
    #print "maxFetch", maxFetch

    if useDirectionWeights:
        binDeltas = DIRECTION_WEIGHTED_BIN_DELTAS
        binWeights = DIRECTION_WEIGHTED_BIN_WEIGHTS

    else:
        binDeltas = BIN_DELTAS
        binWeights = BIN_WEIGHTS
    
    fetchTable, depthTable, unlimitedFetchTable, note = loadFetchAndDepthTables(siteName, maxFetch)

    # clip unlimited fetch and smooth
    fetchForDecreaseFactor = {}
    for d, f in unlimitedFetchTable.items():
        if str(f).upper() == 'U':
            f = MAX_FETCH
        fetchForDecreaseFactor[d] = f
    fetchForDecreaseFactor = calcAverageFetches(fetchForDecreaseFactor)
            
    if averageFetch:
        fetchTable = calcAverageFetches(fetchTable)
    
    if calcType in ['deep', 'mixed', "bretschneider"]:
        
        if calcType == "mixed":
            # assume there is a seaLimits table for this product
            SeaCalc = Bretschneider()
            SeaCalc.setSeaLimitsFile("autoseas/seaLimits/{}.csv".format(siteName))
        else:
            SeaCalc = Bretschneider()
            SeaCalc.setFetchTable(fetchTable)
        
    elif calcType == "shallow":    
        SeaCalc = ShallowWaterSeas()
        SeaCalc.setFetchAndDepthTables(fetchTable, depthTable)
    
    else:
        SeaCalc = BreugenHolthuijsen()
        SeaCalc.setFetchAndDepthTables(fetchTable, depthTable)            
           
    # this the amount the 'unforced' seas are reduced every three hours
    if varyDecreaseFactors:
        decreaseFactor = calcVaryingDecreaseFactor(fetchForDecreaseFactor)
    else:
        decreaseFactor = calcDecreaseFactor()

    # Print some inputs if needed
    if debug or SHOW_TABLE:
        print("Angle   Fetch   AvFetch   DecreaseFactor")
        for d, dir in enumerate(range(0, 360, 10)):
            uFetch = "{:.1f}".format(unlimitedFetchTable[dir]) if unlimitedFetchTable[dir] != 'U' else unlimitedFetchTable[dir]
            print("{:3d}{: >10}{:9.1f}{:12.2f}".format(dir, uFetch, fetchTable[dir], decreaseFactor[d]))
        print("")

    seaBins = np.zeros(36)
    
    if DEBUG: 
        print(seaBins)

    if SHOW_TABLE or debug:
        if firstSeas is not None:
            print('Using a first seas value. First duration is not used in the calculations.\n')
        printWindAndSeaBinsHeader()
    
    wind = winds[0]
    
    if (firstSeas == 0):
        duration = 4.0
        seaBins = initSeas(SeaCalc, seaBins, wind, duration, binDeltas, binWeights)
    else:
        duration = 0
        seaBins = initSeasFromFirstSeas(SeaCalc, seaBins, wind, firstSeas, binDeltas, binWeights)
    
    if SHOW_TABLE or debug:
        printWindAndSeaBins(wind, wind, duration, seaBins)
    
    old = seaBins.copy()
    
    #setup intial values of mSeas
    mSeas = [getSeasToReturn(seaBins, returnDir)]
    
    if returnPdDir:
        windSpd = winds[0][1]
        windDir = winds[0][0]
        mSeas = [get_seas(SeaCalc, seaBins, windSpd, windDir, returnDir, returnPdDir)]
                
    # calc seas using the average of two wind dirs
    for i in range(1, len(winds)):

        if DEBUG: 
            print("pre update bins\n"), np.round(seaBins, 2)
        
        # update sea bins
        w, duration = getWind(winds, i, windWeights)
        seaBins = updateBins(SeaCalc, seaBins, w, duration, decreaseFactor, binDeltas, binWeights)

        if SHOW_TABLE or debug:
            printWindAndSeaBins(winds[i], w, duration, seaBins)
        
        if returnPdDir:
            windSpd = w[1]
            windDir = w[0]
            mSeas.append(get_seas(SeaCalc, seaBins, windSpd, windDir, returnDir, returnPdDir))
        else:
            mSeas.append(getSeasToReturn(seaBins, returnDir))

        if DEBUG: 
            print("updated seaBins for", w[0], round(w[1]))
            #print np.round(seaBins, 1)
        if DEBUG: 
            print(np.max(seaBins))
        
    if SHOW_TABLE or debug:
        print("")
    
    if debug:
        print("\n\n")

    if returnDir:
        return [[max(s[0], 0.1),s[1]] for s in mSeas]
    elif returnPdDir:
        return [[max(s[0], 0.1),s[1],s[2]] for s in mSeas]
    else:
        return [max(s, 0.1) for s in mSeas]

def calcAverageFetch(d, fetchTable):
    """Calc the average fetch for the given d (direction)."""

    dirs = [
        d - 10 if d > 0 else 350,
        d,
        d + 10 if d < 350 else 0
        ]
    
    fetches = [fetchTable[dir] for dir in dirs]
    
    average = sum([f * w for f, w in zip(fetches, FETCH_WEIGHTS)])

    return average
        
def calcAverageFetches(fetchTable):
    """Calculate the average for 1 bin either side using some fudged weights (FETCH_WEIGHTS)."""
    print(f"fetchTable: {fetchTable}")
    averaged = {d: calcAverageFetch(d, fetchTable) for d in range(0, 360, 10)}
    return averaged
    
class Interpolate(object):
    def __init__(self, x_list, y_list):
        if any([y - x <= 0 for x, y in zip(x_list, x_list[1:])]):
            raise ValueError("x_list must be in strictly ascending order!")
        x_list = self.x_list = map(float, x_list)
        y_list = self.y_list = map(float, y_list)
        intervals = zip(x_list, x_list[1:], y_list, y_list[1:])
        self.slopes = [(y2 - y1)/(x2 - x1) for x1, x2, y1, y2 in intervals]
    def __getitem__(self, x):
        i = bisect_left(self.x_list, x) - 1
        return self.y_list[i] + self.slopes[i] * (x - self.x_list[i])
    
    
def calcVaryingDecreaseFactor(fetchTable):
    """This is the factor at which seas decrease when no longer being forced."""

    # Decay due to dispersion and angular spreading
    dispersionAndAngularSpread = 0.93
    
    # Seas also decay because seas that arrives 3 hours later comes from a shorter fetch.
    # 5 second wave travels ~20nm miles in 3 hours. 
    # The following link links average (plateaud) decay factors for the specified fetch and a 20nm shorter fetch.
    # See decreaseFactorFromChangeOfFetch.xls spreadsheet for calcs and chart.
    # The 0.0 fetch value is a 'guesstimate' of a low value. Nominally this should reduce most seas to close to zero.
    # The decay factor changes to 'no change' for >= 300.0 nm

	# Values modified after eyeballing autoseas vs obs.
    decayFactorsForFetches = [[0.0, 0.7], [25.0, 0.7],  [100.0, 0.90], [300.0, 0.90]]
    
    interp = Interpolate(
        [p[0] for p in decayFactorsForFetches],
        [p[1] for p in decayFactorsForFetches]
        )
        
    factors = []
    for d in range(0, 360, 10):
        f = fetchTable[d]
        if f >= 300.0 or f == 'U':
            f = 300.0

        # interp based on decay factors for fetch change
        factor = interp[f]

        # incorporate the dispersion and angular spread change too
        #factor *= dispersionAndAngularSpread
            
        factors.append(factor)
        
    return np.array(factors)


def calcDecreaseFactor():
    """Return a decrease factor of 0.7 for all directions."""
    factor = np.array([0.7 for i in range(0, 360, 10)])
    return factor

def getSeasToReturn(seaBins, returnDir):

    maxSeas = np.max(seaBins)

    if not returnDir:
        return max(0.1, maxSeas)
    else:
        dirs = 10.0 * np.array(range(0, 36))
        dirsAtMax = dirs[seaBins == maxSeas]

        maxSeas = max(0.1, maxSeas)
        avDir = round(averageDirection(dirsAtMax))
    
        return [maxSeas, avDir]

def get_seas(SeaCalc, seaBins, windSpd, windDir, returnDir, returnPdDir):

    maxSeas = np.max(seaBins)

    if returnDir:
        dirs = 10.0 * np.array(range(0, 36))
        dirsAtMax = dirs[seaBins == maxSeas]

        maxSeas = max(0.1, maxSeas)
        avDir = round(averageDirection(dirsAtMax))
    
        return [maxSeas, avDir]

    elif returnPdDir:
        dirs = 10.0 * np.array(range(0, 36))
        dirsAtMax = dirs[seaBins == maxSeas]

        maxSeas = max(0.1, maxSeas)
        avDir = round(averageDirection(dirsAtMax))
        # sea_pd = SeaCalc.calcPeriodFromWind(windSpd, avDir)
        sea_pd = SeaCalc.calcPeriod(maxSeas, windSpd, avDir)
        
        return [maxSeas, sea_pd, avDir]

    else:
        return max(0.1, maxSeas)
    
def averageDirection(dirs, weights=None):
    # Calculate the average direction by averaging the unit vectors and returning the direction.
    # Use the weights list if provided.
    
    num = len(dirs)

    if weights is None:
        w = 1.0 / float(num)
        weights = [w for d in dirs]
    
    u = np.sum([w * sin(d * pi / 180.0) for d, w in zip(dirs, weights)])
    v = np.sum([w * cos(d * pi / 180.0) for d, w in zip(dirs, weights)])

    avDir = atan2(u, v) * 180.0 / pi
    
    if avDir < 0:
        avDir += 360.0
        
    return avDir
    

def printWindAndSeaBinsHeader():
    print("                                                  Sea Bins (by direction)")
    print(" Wind        AvWind               Seas    " + "".join(["{:6.0f}".format(angle) for angle in range(0, 360, 10)]))

    
def printWindAndSeaBins(wind, usedWind, duration, seaBins):

    # print wind
    p = "({:3.0f}/{:2.0f})   ".format(wind[0], wind[1])

    # print wind
    p += "({:3.0f}/{:2.0f} for {:3.1f}hrs)   ".format(usedWind[0], usedWind[1], duration)

    # print calculated seas
    seas = getSeasToReturn(seaBins, True)
    p += "{:3.0f} {:2.1f}m   ".format(seas[1], seas[0])

    # print bins
    bins = ["{:2.2f}".format(round(b, 2)) for b in seaBins]
    p += "  ".join(bins)
    print(p)
    
    
def directionDiff(d1, d2):
    """Calc difference between two angles (going around the clock in the smallest direction."""
    diff = abs(d1 - d2) % 360
    return min(diff, 360 - diff)

    
def getWind(winds, i, weights):
    """Get the wind from the list matching the index i.
    Average the wind speeds and directions for i and i-1 with a weighting provided in weight.
    
    If the direction changes 40 degrees or more, then half the duration and don't average.
    """
    # duration is number of hours since previous, if not provided in wind tuple assume it is 3
    duration = winds[i][2] if len(winds[i]) == 3 else 3
    
    w0 = winds[i-1]
    w1 = winds[i]
    
    dirDiff = directionDiff(w1[0], w0[0])

    if w1[1] > w0[1]:
        # wind increasing
        weight = weights[1]
    else:
        # wind decreasing
        weight = weights[0]

    if dirDiff >= 40.0:
        dirn = w1[0]
        spd = w1[1]
        duration = duration / 2.0
        
    else:
        # average the winds
        dirn = averageDirection([w1[0], w0[0]], [weight, 1.0-weight])
        spd = round(w1[1] * weight + w0[1] * (1.0 - weight), 1)
        #print(f"model wind: {w1[1]}, modified wind: {spd}")

    return (dirn, spd), duration

def updateBins(SeaCalc, seaBins, wind, duration, decreaseFactor, binDeltas, binWeights, useBinDirn=False):
    """Calculate the equivalent duration for the given wind and current sea bins, then + duration hours
    and calculate the resulting seas."""
    
    durations = [SeaCalc.calcEquivDuration(seas, wind[1], wind[0]) for seas in seaBins]


    d = dirIndex(wind[0])

    newSeaBins = np.zeros(36).astype(float)
    for binDelta, spdAdjust in zip(binDeltas, binWeights):

        i = binIndex(d, binDelta)

        if useBinDirn:
            # use the wind direction of the bin being calculated
            windDir = i * 10.0
        else:
            windDir = wind[0]

        newSeaBins[i] = SeaCalc.seasFromFetchAndDuration(
            wind[1] * spdAdjust,
            windDir,
            durations[i] + duration)
    
    # Take the most reduced seas out of reducing by the factor or reducing by a fixed amount when the seas are <= 1.0. 
    # The fixed amount is 1 - factor.
    reducedSeaBins = np.minimum(
        np.array(seaBins) * decreaseFactor,  # original reduced by the factor
        0.5 * decreaseFactor  # reduced by the factor but based on a 1.0m seas
        )

    newSeaBins = np.maximum(newSeaBins, reducedSeaBins)
    
    #print durations
    if DEBUG:
        for i, d, s in zip(range(36), durations, newSeaBins):
            print(i * 10, d, s)

    #print newSeaBins

    return newSeaBins
    

def initSeas(SeaCalc, seaBins, wind, duration, binDeltas, binWeights):
    """Init the seaBins based on the wind speed, dir and fixed duration."""
    d = dirIndex(wind[0])

    for binDelta, spdAdjust in zip(binDeltas, binWeights):
        i = binIndex(d, binDelta)
        seaBins[i] = SeaCalc.seasFromFetchAndDuration(wind[1] * spdAdjust, wind[0], duration)

    return seaBins


def initSeasFromFirstSeas(SeaCalc, seaBins, wind, firstSeas, binDeltas, binWeights):
    """Init the bins with first seas in the bins baed on the wind."""
    d = dirIndex(wind[0])
    
    firstSeas = float(firstSeas)
    
    for binDelta, spdAdjust in zip(binDeltas, binWeights):
        i = binIndex(d, binDelta)
        seaBins[i] = firstSeas * spdAdjust
        
    return seaBins    


def binIndex(dirIndex, change):
    b = dirIndex + change
    if b < 0:
        b += 36
    if b >= 36:
        b -= 36
    return b


def dirIndex(windDir):
    return int(round(windDir / 10.0)) % 36


#############################################################
# Fetch and depth information
#############################################################
def loadFetchAndDepthTables_old(siteName, maxFetch):
    """Load the fetch and depth tables from csv. Return None if no fetch information."""

    fetches = {}
    depths = {}
    unlimitedFetches = {}

    note = ''

    with open("autoseas/fetchLimits/" + siteName + ".csv", mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for r in reader:

            if r['windDir'] == 'note':
                note = r['fetch']
                continue

            dirn = int(r['windDir'])

            # Turn fetch into a number and limit to the max fetch
            fetch = r['fetch']
            unlimitedFetches[dirn] = float(fetch) if str(fetch).upper() != 'U' else 'U'
            fetch = maxFetch if fetch == 'U' else float(fetch)
            if fetch > maxFetch:
                fetch = maxFetch
            fetches[dirn] = fetch

            # Turn depth into a number if it exists
            if r['depth'] != '':
                depth = float(r['depth'])
                depths[dirn] = depth

    # check for any depth values
    if depths.keys():
        for dirn in fetches.keys():
            if dirn not in depths:
                depths[dirn] = MAX_DEPTH    
    else:
        depths = None

    return fetches, depths, unlimitedFetches, note

def loadFetchAndDepthTables(siteName, maxFetch):
    """Load the fetch and depth tables from csv. Return None if no fetch information."""

    fetches = {}
    depths = {}
    unlimitedFetches = {}

    note = ''
        
    with open("autoseas/fetchLimits/" + siteName + ".csv", mode='r') as csvfile:
        reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
        for r in reader:

            if r['windDir'] == 'note':
                note = r['fetch']
                continue

            dirn = int(r['windDir'])

            # Turn fetch into a number and limit to the max fetch
            fetch = r['fetch']
            unlimitedFetches[dirn] = float(fetch) if fetch != 'U' else 'U'
            fetch = maxFetch if str(fetch).upper() == 'U' else float(fetch)
            if fetch > maxFetch:
                fetch = maxFetch
            fetches[dirn] = fetch

            # Turn depth into a number if it exists
            if r['depth'] != '':
                depth = float(r['depth'])
                depths[dirn] = depth
            else:
                depths[dirn] = MAX_DEPTH
            
    # check for any depth values
    if depths.keys():
        for dirn in fetches.keys():
            if dirn not in depths:
                depths[dirn] = 60
    else:
        depths = None
        
    return fetches, depths, unlimitedFetches, note

def getFetch(fetchTable, windDir):
    """Get fetch from the table for the given windDir."""
    i = 10 * dirIndex(windDir)
    return fetchTable[i]

def getDepth(depthTable, windDir):
    i = 10 * dirIndex(windDir)
    return depthTable[i]


#############################################################
# Tests
#############################################################

if __name__ == "__main__":
    # Add the directory containing the autoseas package to sys.path
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
    from bretschneider import Bretschneider
    from shallowWaterSeas import ShallowWaterSeas
    from breugen_holthuijsen import BreugenHolthuijsen
    
    np.set_printoptions(suppress=True, formatter={'float_kind':'{:f}'.format})
    
    
    WINDS_1 = [
        (200, 40),
        (190, 40),
        (180, 40),
        (170, 40),
        (170, 40),
        (200, 10),
        (240, 14),
        (240, 17),
        (230, 18),
        (230, 20),
        (220, 21),
        (210, 18),
        (210, 13),
        (230, 14),
        (240, 13),
        (230, 14),
    ]
    
    WINDS_2 = [
        (200, 10),
        (190, 20),
        (180, 20),
        (170, 10),
        (170, 10),
        (200, 10),
        (240, 14),
        (240, 17),
        (230, 18),
        (230, 20),
        (220, 21),
        (210, 18),
        (210, 13),
        (230, 14),
        (240, 13),
        (230, 14),
    ]
    

    
    siteName = 'Woodside_-_Enfield_and_Vincent_10_days' 
    #siteName = 'CITIC_Pacific_-_Mermaid_Strait' 
    winds_1 = WINDS_1
    winds_2 = WINDS_2
    src="autoseas"
    firstSeas=0
    maxFetch=MAX_FETCH
    maxDuration=MAX_DURATION
    windWeights=[0.25, 0.75]
    returnDir=False
    returnPdDir=True
    calcType='holthuijsen'
    debug=False
    averageFetch=True
    varyDecreaseFactors=False
    useDirectionWeights=True
    
    seas_1 = autoSeas(
        siteName, 
        winds_1,
        src = src,
        firstSeas = firstSeas,
        maxFetch = maxFetch,
        maxDuration = maxDuration,
        windWeights = windWeights,
        returnDir = returnDir,
        returnPdDir = returnPdDir,
        calcType = 'bretschneider',
        debug = debug,
        averageFetch = averageFetch,
        varyDecreaseFactors = varyDecreaseFactors,
        useDirectionWeights = useDirectionWeights
    )
    
    seas_2 = autoSeas(
        siteName, 
        winds_2,
        src = src,
        firstSeas = firstSeas,
        maxFetch = maxFetch,
        maxDuration = maxDuration,
        windWeights = windWeights,
        returnDir = returnDir,
        returnPdDir = returnPdDir,
        calcType = 'holthuijsen',
        debug = debug,
        averageFetch = averageFetch,
        varyDecreaseFactors = varyDecreaseFactors,
        useDirectionWeights = useDirectionWeights
    ) 
    
    # Flatten the lists if they contain nested lists
    seas_1 = np.round(seas_1, 2)
    seas_2 = np.round(seas_2, 2)

    print(f"winds_1: {winds_1}, seas: {seas_1}\n\n\n")    
    print(f"winds_2: {winds_2}, seas: {seas_2}")    
    
