"""

Equation 3-39 from Shore Protection Manual 1984

"""

import numpy as np
import pandas as pd
import math
import csv
from autoseas.lookUpTable import loadTable, valueFromTable

MAX_FETCH = 100.0  # 100nm
MAX_DURATION = 36.0  # hours
GRAVITY = 9.81  # m/s

def seasFromFetchAndDepth(spd, fetch, depth):
    """
    
    spd : knots
    fetch : nautical miles
    depth : m
    """
    ua = windStressFactor(spd)
    f = fetch * 1852.0  # convert to m

    seas = waveHeightInShallowWater(ua, f, depth)
    
    return seas

def seasInShallowWater(spd, duration, fetch, depth):
    """
    Calculate the seas for a given duration, fetch and water depth.
    
    
    spd : knots
    duration : hours
    fetch : nautical miles
    depth : m
    """
    ua = windStressFactor(spd)
    dur = duration * 3600.0
    f = fetch * 1852.0
    
    # duration limited - use deep water value
    durLimited = durationLimited(ua, dur)

    fLimited = waveHeightInShallowWater(ua, f, depth)

    ht = min(durLimited, fLimited)
    
    return ht

    
def seasFetchLimited(spd, fetch):
    """

    spd : knots
    fetch : nautical miles
    """
    ua = windStressFactor(spd)
    f = fetch * 1852.0
    return fetchLimited(ua, f)
    
    
def seasDurationLimited(spd, duration):
    """

    spd : knots
    duration : hours
    """
    ua = windStressFactor(spd)
    dur = duration * 3600.0
    return durationLimited(ua, dur)
    
#
# General Equations
#
    
def windStressFactor(speed10m):
    # speed10m in knots
    return 0.71 * math.pow(speed10m * 0.514444, 1.23)


#
# Deep water equations
#
    
def fullyDevelopedHeight(ua):
    # Equation 3-36
    return (ua ** 2.0) * 0.2433 / GRAVITY

    
def fullyDevelopedDuration(ua):
    # Duration (hours) for a wind speed to fully develop the seas.
    # Equation 3-38
    return ua * 71500.0 / GRAVITY

    
def fetchLimited(ua, fetch):
    """Fetch limited wave height.
    
    Equation 3-33
    
    ua : m/s
    fetch : m
    """
    ht = (ua ** 2.0 / GRAVITY) * 0.0016 * math.pow(GRAVITY * fetch / (ua ** 2.0), 0.5)
    
    ht = 0.0005112 * ua * math.sqrt(fetch)
    
    # restrict the height to the fully developed height
    maxHt = fullyDevelopedHeight(ua)
    
    print("fully developed height", maxHt)
    
    ht = min(ht, maxHt)
        
    return ht
    
def durationLimited(ua, duration):
    """Find the duration limited wave height.
    
    Use equation 3-35 to go from the duration to the equivalent fetch, then
    return the fetch limited value for that fetch.
    
    ua : m/s
    duration : s
    """
    # restrict the duration to the duration to acheive fully developed
    maxDuration = fullyDevelopedDuration(ua)
    duration = min(duration, maxDuration)
    
    equivFetch = math.pow(((GRAVITY * duration / ua) / 68.8), 3.0 / 2.0) * (ua ** 2.0) / GRAVITY
    
    print("equivFetch: ", duration / 3600.0, round(equivFetch, 2))
    
    ht = fetchLimited(ua, equivFetch)

    return ht
    
#
# Shallow Water Equations
#
    
def waveHeightInShallowWater(ua, fetch, depth):
    """
    
    ua : wind stress factor (m/s)
    fetch : m
    depth : m
    """

    if ua == 0:
        # no wind, no waves
        return 0
    
    # Equation 3-39 from Shore Protection Manual 1984
    H = ((ua ** 2.0) / GRAVITY) * 0.283 * \
        math.tanh(
            0.530 * math.pow(GRAVITY * depth / (ua ** 2.0), 0.75)
        ) * math.tanh( \
            0.00565 * math.pow(GRAVITY * fetch / (ua ** 2.0), 0.5) / \
            math.tanh(
                0.530 * math.pow(GRAVITY * depth / (ua ** 2.0), 0.75)
            )
        )

    return H


def periodInShallowWater(ua, fetch, depth):
    """
    ua : wind stress factor (m/s)
    fetch : m
    depth : m
    """
    
    # Equation 3-40 from Shore Protection Manual 1984
    fetch = fetch * 1852.0  # convert to m
    T = (ua / GRAVITY) * 7.54 * \
        math.tanh(
            0.833 * math.pow(GRAVITY * depth / (ua ** 2.0), (3.0 / 8.0))
        ) * math.tanh( \
            0.0379 * math.pow(GRAVITY * fetch / (ua ** 2.0), 0.3333) / \
            math.tanh(
                0.833 * math.pow(GRAVITY * depth / (ua ** 2.0), (3.0 / 8.0))
            )
        )

    return T

def minDurationInShallowWater(ua, fetch, depth):
    """
    The minimum duration required for the wind (ua) to blow for the
    seas to reach 'fully developed' for the given fetch.
    
    Equation 3-41
    
    ua : wind stress factor (m/s)
    fetch : m
    depth : m    
    """
    T = periodInShallowWater(ua, fetch, depth)
    minDuration = (ua / GRAVITY) * 537.0 * math.pow(GRAVITY * T / ua, (7.0, 3.0))
    return minDuration
    
    
def test_methods():
    
    # From example on page 3-66
    seas = waveHeightInShallowWater(22.0, 24.4 * 1000.0, 11.0)
    print("seas", round(seas, 1))
    assert abs(seas - 1.5) < 0.1
    
    period = periodInShallowWater(22.0, 24.4 * 1000.0, 11.0)
    print("period", round(period, 1))
    assert abs(period - 4.4) < 0.1
    
    
    
    # lng jetty - typical value
    seas = seasFromFetchAndDepth(22.0, 5.0, 7.0)
    print("lng jetty seas", round(seas, 2))
    
    # 240 / 22 knots
    seas = seasFromFetchAndDepth(22.0, 8.0, 10.0)
    print("lng jetty seas", round(seas, 2))


    #
    seas = seasInShallowWater(22.0, 6, 5, 6.0)
    print("seas in shallow water", round(seas, 2))
    
    # for example on page 3-53 i
    seas = seasDurationLimited(45.7, 3)
    print("seas", seas)
    assert abs(seas - 3.3) < 0.1

    # for example on page 3-53 g
    seas = seasFetchLimited(45.7, 5.4)
    print("seas fetch limited", seas)
    assert abs(seas - 1.75) < 0.1
    
    # for example on page 3-53 h
    seas = seasFetchLimited(45.7, 54.0)
    print("seas fetch limited", seas)
    assert abs(seas - 5.5) < 0.1

    # comparing to GD chart
    # 10 m/s (19.4 knots), 12 hours, 2.0m
    seas = seasDurationLimited(19.4, 12.0)
    print("compare to gd seas of 2.0: ", seas)

    #
    durations = [3.0, 6.0, 10.0, 20.0]
    seas = [round(seasDurationLimited(20.0, d), 1) for d in durations]
    print("")
    print("spd: 20.0")
    for d, s in zip(durations, seas):
        print("{}: {}".format(d, s))
    print("")
    
    print("20 knots as wind stress (m/s)", windStressFactor(20))
    

def dirIndex(windDir):
    return int(round(windDir / 10.0)) % 36

def inverse(f, delta=0.0001):
    def f_1(y):
        lo, hi = find_bounds(f, y)
        return binary_search(f, y, lo, hi, delta)
    return f_1

def find_bounds(f, y):
    x = 1
    while f(x) < y:
        x = x * 2
    lo = 0 if (x ==1) else x/2
    return lo, x

def binary_search(f, y, lo, hi, delta):
    while lo <= hi:
        x = (lo + hi) / 2
        if f(x) < y:
            lo = x + delta
        elif f(x) > y:
            hi = x - delta
        else:
            return x;
    return hi if (f(hi) - y < y - f(lo)) else lo

class ShallowWaterSeas(object):

    def __init__(self):
        self.FETCH_AND_DEPTH = {}

        # using deep water values for duration based growth, limit to bretschneider values for fetch
        self.DURATIONS = loadTable('autoseas/bs_durations.csv')
        self.FETCH_TABLE = loadTable('autoseas/bs_fetchLimits.csv')

    def setFetchAndDepthFile(self, siteName, maxFetch):
        """Redundant I think."""
    
        with open("autoseas/fetchLimits/"+ siteName +".csv", 'rb') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for r in reader:
                dirn = int(r['windDir'])
                fetch = r['fetch']
                fetch = maxFetch if fetch == 'U' else float(fetch)
                if fetch > maxFetch:
                    fetch = maxFetch

                depth = float(r['depth'])
                
                self.FETCH_AND_DEPTH[dirn] = (fetch, depth)
    
    def setFetchAndDepthTables(self, fetchTable, depthTable):
        """Set fetch and depth from the input tables."""
        self.FETCH_AND_DEPTH = {}
        for d, f in fetchTable.items():
            self.FETCH_AND_DEPTH[d] = (f, depthTable[d])
        
    def getFetchAndDepth(self, windDir):
        """Get the fetch and depth in the table for the given windDir."""
        i = 10 * dirIndex(windDir)
        
        fetchAndDepth = self.FETCH_AND_DEPTH[i]
        
        #print windDir, i, fetchAndDepth
        #print "<br>"
        
        return fetchAndDepth

    def calcPeriodFromWind(self, windSpd, windDir):
        """Calculate the period from the seas"""
        
        depth = self.getFetchAndDepth(windDir)[1]
        g = 9.81  
        wind_speed_mps = windSpd * 0.51444  # convert wind speed from knots to m/s
    
        # Bretschneider peak period in deep water
        Tp_deep = 0.286 * wind_speed_mps ** 2 / g

        # Wavelength in deep water
        L_deep = g * Tp_deep ** 2 / (2 * math.pi)

        # Wave speed in shallow water
        C_shallow = math.sqrt(g * depth)

        # Wave period in shallow water
        T_shallow = L_deep / C_shallow

        return int(round(T_shallow))

    def calcPeriod(self, hs, windSpd, windDir):
        """Calculate the peak wave period from significant wave height"""
        if windSpd <= 0.1:
            return 0

        fetch, depth = self.getFetchAndDepth(windDir)
        period = periodInShallowWater(windStressFactor(windSpd), fetch, depth)
        period = max(2, period)
        
        return int(round(period, 2))               
    
    def seasFromFetchLimited(self, windSpd, windDir):
        """Calculate the 'fetch limited' or full developed seas for this wind speed and direction.
    
        windSpd in knots, windDir in degrees."""
        fetch, depth = self.getFetchAndDepth(windDir)
        seas = seasFromFetchAndDepth(windSpd, fetch, depth)
        
        # take the min of the shallow water values and the deep water values (which can be less)
        deepSeas = self.seasFromFetchLimitedDeepWater(windSpd, fetch)
        seas = min(seas, deepSeas)
        
        return seas
        
    def seasFromDuration(self, windSpd, duration):
        """windSpd in knots, duration in hours."""
        return valueFromTable(self.DURATIONS, windSpd, duration)
        
    def seasFromFetchLimitedDeepWater(self, windSpd, fetch):
        """Return the Bretschneider limited value."""
        return valueFromTable(self.FETCH_TABLE, windSpd, fetch)
    
    def seasFromFetchAndDuration(self, windSpd, windDir, duration):
        """windSpd in knots, duration in hours, fetch in nm."""
        # Components needed for wave calculations. Ensure that wind speed is not zero, to avoid log(0) in GD curves.
        windSpd = np.maximum(0.1, windSpd)
    
        fromFetch = self.seasFromFetchLimited(windSpd, windDir)
        fromDuration = self.seasFromDuration(windSpd, duration)
    
        # Determine which is the least from WindWaveHgt_Fetch,WindWaveHgt_duration
        return np.minimum(fromFetch, fromDuration)
    
    
    def calcEquivDuration(self, seas, windSpd, windDir):
        """Calc the duration which would result in seas for the given windSpd and windDir (fetch from dir)."""
    
        #print "calc equiv duration", seas, windSpd, fetch
    
        if seas < 0.01:
            return 0.0
    
        # calc 'fetch limit'
        fromFetch = self.seasFromFetchLimited(windSpd, windDir)
    
        fromMaxDuration = self.seasFromDuration(windSpd, MAX_DURATION)
    
        #print 'from fetch', fromFetch
        #print 'from max duration', fromMaxDuration
    
        if seas >= fromFetch:
            # fully developed for the fetch
            return MAX_DURATION
    
        if seas >= fromMaxDuration:
            return MAX_DURATION
        
        def rtSeasFromDuration(duration):
            return self.seasFromDuration(windSpd, duration)
    
        durationFromSeas = inverse(rtSeasFromDuration)
    
        duration = durationFromSeas(seas)
        
        #print "duration", duration
        
        return duration
