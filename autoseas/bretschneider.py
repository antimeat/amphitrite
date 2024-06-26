import numpy as np
import csv
from autoseas.lookUpTable import loadTable, valueFromTable

DEBUG = False

MAX_DURATION = 36.0  # hours

class Bretschneider(object):

    def __init__(self):
        self.FETCH_LIMITS_TABLE = None
        self.SEA_LIMITS_TABLE = None

        self.FETCH_TABLE = loadTable('autoseas/bs_fetchLimits.csv')
        self.DURATIONS = loadTable('autoseas/bs_durations.csv')

    def setSeaLimitsFile(self, fileName):
        self.SEA_LIMITS_TABLE = loadTable(fileName)
    
    def setFetchLimitsFile(self, siteName, maxFetch):
    
        self.FETCH_LIMITS_TABLE = {}
    
        with open("autoseas/fetchLimits/"+ siteName +".csv", 'r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for r in reader:
                dirn = int(r['windDir'])
                fetch = r['fetch']
                fetch = maxFetch if fetch == 'U' else float(fetch)
                if fetch > maxFetch:
                    fetch = maxFetch
                
                self.FETCH_LIMITS_TABLE[dirn] = fetch
                
    def setFetchTable(self, fetchTable):
        self.FETCH_LIMITS_TABLE = fetchTable
        
    def getFetchLimit(self, windDir):
        """Get the fetch in the table for the given windDir."""
        i = 10 * dirIndex(windDir)
        return self.FETCH_LIMITS_TABLE[i]

    def calcPeriodFromWind(self, windSpd, windDir):
        """Calculate the peak wave period from wind speed using Pierson-Moskowitz approximation"""
        wind_speed_mps = windSpd * 0.51444  # convert wind speed from knots to m/s
        alpha = 0.87  # updated alpha based on current literature
        period = alpha * wind_speed_mps
        
        return round(period, 2)        
            
    def calcPeriod(self, hs, windSpd, windDir):
        """Calculate the peak wave period from significant wave height"""
        
        period = 3.86 * (hs ** 0.5)
        period = max(1,period)
        return int(round(period, 2))               
    
    def seasFromFetchLimited(self, windSpd, windDir):
        """Calculate the 'fetch limited' or full developed seas for this wind speed and direction.
    
        windSpd in knots, windDir in degrees."""
        if self.SEA_LIMITS_TABLE is not None:
            # use the sea limits table
            return valueFromTable(self.SEA_LIMITS_TABLE, windDir, windSpd)
        else:
            # use fetch limits table
            fetch = self.getFetchLimit(windDir)
            return valueFromTable(self.FETCH_TABLE, windSpd, fetch)


    def seasFromDuration(self, windSpd, duration):
        """windSpd in knots, duration in hours."""
        return valueFromTable(self.DURATIONS, windSpd, duration)
    
    
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
    
        if seas < 0.01:
            return 0.0
    
        # calc 'fetch limit'
        fromFetch = self.seasFromFetchLimited(windSpd, windDir)
    
        fromMaxDuration = self.seasFromDuration(windSpd, MAX_DURATION)
    
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