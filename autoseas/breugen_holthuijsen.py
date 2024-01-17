import math
import numpy as np
import csv
from autoseas.lookUpTable import loadTable, valueFromTable

MAX_FETCH = 100.0  # 100nm
MAX_DURATION = 36.0  # hours
GRAVITY = 9.81  # m/s
        
def kts_to_mps(windSpd):
    windSpd_mps = windSpd / 1.94384  # Convert from knots to m/s
    return windSpd_mps
    
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

def calculate_fully_developed_wave_height(V_stc):
    """
    Calculate the fully developed wave height using Breugem and Holthuijsen (2006) formulation.
    Reference: Breugem, W., and L. Holthuijsen, 2006. "Generalized shallow water wave growth from Lake George."
            Journal of Waterway, Port, Coastal, and Ocean Engineering, 133, 173.

    Parameters:
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.
    
    Returns:
    - float: Fully developed wave height.
    """
    H_max = 0.2433 * abs(V_stc)**2 / GRAVITY
    return H_max

def calculate_depth_term(D, V_stc):
    """
    Calculate the depth term in the wave height formula.

    Parameters:
    - D (float): Water depth in meters.
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.

    Returns:
    - float: Depth term.
    """
    depth_term = math.tanh(0.343 * (GRAVITY * D / abs(V_stc)**2)**1.14)
    return depth_term

def calculate_fetch_term(F, V_stc):
    """
    Calculate the fetch term in the wave height formula.

    Parameters:
    - F (float): Fetch distance in nautical miles.
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.

    Returns:
    - float: Fetch term.
    """
    #conver fetch from nautical miles to metres
    fetch = F*1852
    fetch_term = math.tanh(0.000414 * (GRAVITY * fetch / abs(V_stc)**2)**0.79)
    return fetch_term

def calculate_wave_height(H_max, depth_term, fetch_term):
    """
    Calculate the fully developed wave height using the depth and fetch terms.

    Parameters:
    - H_max (float): Fully developed wave height.
    - depth_term (float): Depth term.
    - fetch_term (float): Fetch term.

    Returns:
    - float: Wave height.
    """
    H = H_max * (depth_term * math.tanh(fetch_term * depth_term))
    return H

def calculate_fully_developed_wave_period(V_stc):
    """
    Calculate the fully developed wave period using additional equations.
    Reference: Holthuijsen, L. H., 2007. "Waves in Oceanic and Coastal Waters." Cambridge University Press, 404 pp.

    Parameters:
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.
    
    Returns:
    - float: Fully developed wave period.
    """
    T_max = 7.69 * abs(V_stc) / GRAVITY
    return T_max

def calculate_depth_term_period(D, V_stc):
    """
    Calculate the depth term in the wave period formula.

    Parameters:
    - D (float): Water depth in meters.
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.

    Returns:
    - float: Depth term for wave period.
    """
    V_stc_safe = max(V_stc, 0.0001)
    depth_term_period = math.tanh(0.1 * (GRAVITY * D / abs(V_stc_safe)**2)**2.01)
    return depth_term_period

def calculate_fetch_term_period(F, V_stc):
    """
    Calculate the fetch term in the wave period formula.

    Parameters:
    - F (float): Fetch distance in nautical miles.
    - V_stc (float): Sustained wind speed at 10-meter height in m/s.

    Returns:
    - float: Fetch term for wave period.
    """
    fetch = F*1852
    V_stc_safe = max(V_stc, 0.0001)
    fetch_term_period = math.tanh(0.000000277 * (GRAVITY * fetch / abs(V_stc_safe)**2)**1.45)
    return fetch_term_period

def calculate_wave_period(T_max, depth_term_period, fetch_term_period):
    """
    Calculate the fully developed wave period using the depth and fetch terms.

    Parameters:
    - T_max (float): Fully developed wave period.
    - depth_term_period (float): Depth term for wave period.
    - fetch_term_period (float): Fetch term for wave period.

    Returns:
    - float: Wave period.
    """
    T = T_max * (depth_term_period * math.tanh(fetch_term_period * depth_term_period))**0.18
    return T

class BreugenHolthuijsen():

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
        
        return fetchAndDepth

    def seasFromFetchLimited(self, windSpd, windDir):
        """Calculate the 'fetch limited' or full developed seas for this wind speed and direction.
    
        windSpd in knots, windDir in degrees."""
        fetch, depth = self.getFetchAndDepth(windDir)
        #seas = seasFromFetchAndDepth(windSpd, fetch, depth)
        
        #deep seas uses kts
        deepSeas = self.seasFromFetchLimitedDeepWater(windSpd, fetch)
        
        #this one uses mps
        H_max = calculate_fully_developed_wave_height(kts_to_mps(windSpd))
        seas = calculate_wave_height(H_max, depth, fetch)
        
        # take the min of the shallow water values and the deep water values (which can be less)
        seas = min(seas, deepSeas)
        
        return seas
    
    def seasFromFetchLimitedDeepWater(self, windSpd, fetch):
        """Return the Bretschneider limited value."""
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
    
        #print "calc equiv duration", seas, windSpd, fetch
    
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
        
        return duration

    def calcPeriodFromWind(self, windSpd, windDir):
        """Calculate the period from the seas"""
        
        #windSpd in knots, windDir in degrees
        fetch, depth = self.getFetchAndDepth(windDir)
        
        windSpd_ms = kts_to_mps(windSpd)
        pd_max = calculate_fully_developed_wave_period(windSpd_ms)
        depth_term_period = calculate_depth_term_period(depth, windSpd_ms)
        fetch_term_period = calculate_fetch_term_period(fetch, windSpd_ms)
        wave_period = calculate_wave_period(pd_max, depth_term_period, fetch_term_period)
        
        return wave_period
