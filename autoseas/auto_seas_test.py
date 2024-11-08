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
MAX_FETCH = 60.0  # 100km
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


def auto_seas(site_name, winds, src="smush", first_seas=0, max_fetch=MAX_FETCH,
              max_duration=MAX_DURATION, wind_weights=[0.25, 0.75], return_dir=False,
              return_pd_dir=False, calc_type='new', debug=False, average_fetch=True,
              vary_decrease_factors=False, use_direction_weights=True):
    """
    Calculate sea conditions based on wind data for a specified site.

    Args:
        site_name (str): The name of the site for which sea conditions are calculated.
        winds (list): A list of tuples representing wind direction, speed, and duration.
        src (str): Source identifier for the type of calculation. Default is "smush".
        first_seas (float): The initial sea condition (height). Default is 0.
        max_fetch (float): The maximum fetch distance. Default is 60.0 nautical miles.
        max_duration (float): The maximum duration for calculation. Default is 36.0 hours.
        wind_weights (list): A list of weights for averaging wind conditions. Default is [0.25, 0.75].
        return_dir (bool): Flag to return direction of seas. Default is False.
        return_pd_dir (bool): Flag to return period and direction of seas. Default is False.
        calc_type (str): Type of sea calculation ('new', 'deep', 'mixed', 'shallow'). Default is 'new'.
        debug (bool): Flag to enable debug mode. Default is False.
        average_fetch (bool): Flag to average the fetch values. Default is True.
        vary_decrease_factors (bool): Flag to vary the decrease factors. Default is False.
        use_direction_weights (bool): Flag to use directional weights. Default is True.

    Returns:
        list: Calculated sea conditions based on the provided wind data.
    """
    bin_deltas, bin_weights = determine_bin_weights(use_direction_weights)
    
    fetch_table, depth_table, unlimited_fetch_table, note = load_fetch_and_depth_tables(site_name, max_fetch)
    fetch_for_decrease_factor = prepare_fetch_for_decrease_factor(unlimited_fetch_table)
    
    if average_fetch:
        fetch_table = calc_average_fetches(fetch_table)
    
    sea_calc = select_sea_calculation_model(calc_type, site_name, fetch_table, depth_table)

    decrease_factor = determine_decrease_factor(vary_decrease_factors, fetch_for_decrease_factor)

    if debug or SHOW_TABLE:
        print_debug_info(unlimited_fetch_table, fetch_table, decrease_factor)

    sea_bins = initialize_sea_bins(first_seas, sea_calc, winds, bin_deltas, bin_weights)

    m_seas = calculate_seas(sea_bins, winds, sea_calc, decrease_factor, bin_deltas, bin_weights, 
                            return_dir, return_pd_dir, debug)

    return format_sea_output(m_seas, return_dir, return_pd_dir)

def determine_bin_weights(use_direction_weights):
    """
    Determine the bin deltas and weights based on whether direction weights are used.

    Args:
        use_direction_weights (bool): Flag indicating whether to use directional weights.

    Returns:
        tuple: A tuple containing two lists - bin deltas and bin weights.
    """
    if use_direction_weights:
        bin_deltas = DIRECTION_WEIGHTED_BIN_DELTAS
        bin_weights = [cos_squared_speed_adjust(b) for b in bin_deltas]
    else:
        bin_deltas = BIN_DELTAS
        bin_weights = BIN_WEIGHTS

    return bin_deltas, bin_weights

def cos_squared_speed_adjust(offset):
    """
    Reduce the wind speed for bins either side of the wind direction using a cosine squared adjustment.

    Args:
        offset (int): The bin offset from the central wind direction.

    Returns:
        float: The adjustment factor based on the cosine squared of the angle.
    """
    angle = offset * 10.0
    return pow(cos(radians(angle)), 2)

import csv

def load_fetch_and_depth_tables(site_name, max_fetch):
    """
    Load fetch and depth tables for a given site from a CSV file.

    Args:
        site_name (str): The name of the site.
        max_fetch (float): The maximum fetch value to be considered.

    Returns:
        tuple: A tuple containing fetch table, depth table, unlimited fetch table, and notes.
    """
    fetches = {}
    depths = {}
    unlimited_fetches = {}
    note = ''

    try:
        with open(f"autoseas/fetchLimits/{site_name}.csv", mode='r') as csvfile:
            reader = csv.DictReader(csvfile, delimiter=',', quotechar='"')
            for row in reader:
                if row['windDir'] == 'note':
                    note = row['fetch']
                    continue

                dirn = int(row['windDir'])
                fetch = row['fetch']
                depth = row['depth']

                # Process fetch
                unlimited_fetches[dirn] = float(fetch) if fetch != 'U' else 'U'
                fetch = max_fetch if fetch == 'U' else min(float(fetch), max_fetch)
                fetches[dirn] = fetch

                # Process depth
                if depth:
                    depths[dirn] = float(depth)

    except FileNotFoundError:
        raise Exception(f"Fetch and depth table file not found for site '{site_name}'.")

    # Fill missing depth values with a default value (e.g., 60.0)
    for dirn in fetches:
        if dirn not in depths:
            depths[dirn] = 60.0

    return fetches, depths, unlimited_fetches, note

def prepare_fetch_for_decrease_factor(unlimited_fetch_table):
    """
    Prepare fetch values for the calculation of decrease factors.

    Args:
        unlimited_fetch_table (dict): A dictionary containing fetch data for various directions.

    Returns:
        dict: A dictionary with processed fetch values for decrease factor calculation.
    """
    fetch_for_decrease_factor = {}
    for direction, fetch in unlimited_fetch_table.items():
        if fetch == 'U':  # Handle 'unlimited' fetch case
            fetch = 400.0  # Assuming 400 as a large fetch value for 'unlimited'
        fetch_for_decrease_factor[direction] = fetch
    
    return fetch_for_decrease_factor

def calc_average_fetches(fetch_table):
    """
    Calculate the average fetch for each direction in the fetch table.

    Args:
        fetch_table (dict): A dictionary containing fetch data for various directions.

    Returns:
        dict: A dictionary with averaged fetch values.
    """
    averaged_fetch = {}
    directions = sorted(fetch_table.keys())  # Ensure directions are sorted

    for dir in directions:
        # Fetch values for adjacent directions
        adjacent_dirs = [(dir - 10) % 360, dir, (dir + 10) % 360]
        adjacent_fetches = [fetch_table.get(adj_dir, 0) for adj_dir in adjacent_dirs]

        # Calculate the weighted average
        average = sum(adjacent_fetches) / len(adjacent_fetches)
        averaged_fetch[dir] = average

    return averaged_fetch

def select_sea_calculation_model(calc_type, site_name, fetch_table, depth_table):
    """
    Select and configure the sea calculation model based on calculation type.

    Args:
        calc_type (str): The type of calculation ('new', 'deep', 'mixed', 'shallow').
        site_name (str): The name of the site.
        fetch_table (dict): The fetch table for the site.
        depth_table (dict): The depth table for the site.

    Returns:
        object: An instance of the selected sea calculation model.
    """
    if calc_type in ['deep', 'mixed']:
        sea_calc = Bretschneider()
        if calc_type == "mixed":
            sea_calc.set_sea_limits_file(f"autoseas/seaLimits/{site_name}.csv")
        else:
            sea_calc.set_fetch_table(fetch_table)

    elif calc_type == "shallow":
        sea_calc = ShallowWaterSeas()
        sea_calc.set_fetch_and_depth_tables(fetch_table, depth_table)

    else:  # Default to 'new' or handle other types here
        sea_calc = BreugenHolthuijsen()
        sea_calc.set_fetch_and_depth_tables(fetch_table, depth_table)

    return sea_calc

def determine_decrease_factor(vary_decrease_factors, fetch_for_decrease_factor):
    """
    Determine the decrease factor for sea conditions based on fetch data.

    Args:
        vary_decrease_factors (bool): Flag indicating whether to vary the decrease factors.
        fetch_for_decrease_factor (dict): Fetch data for calculating decrease factors.

    Returns:
        numpy.array: An array of decrease factors for each direction.
    """
    if vary_decrease_factors:
        decrease_factor = calc_varying_decrease_factor(fetch_for_decrease_factor)
    else:
        decrease_factor = calc_standard_decrease_factor()

    return decrease_factor

def calc_varying_decrease_factor(fetch_for_decrease_factor):
    """
    Calculate varying decrease factors based on fetch data.

    Args:
        fetch_for_decrease_factor (dict): Fetch data for calculating decrease factors.

    Returns:
        numpy.array: An array of varying decrease factors.
    """
    # Implementation for varying decrease factor calculation
    # Example: based on fetch data, calculate different decrease factors
    # This is a placeholder for your specific logic
    factors = []
    for direction, fetch in fetch_for_decrease_factor.items():
        factor = some_complex_calculation_based_on_fetch(fetch)  # Placeholder
        factors.append(factor)
    
    return np.array(factors)

def calc_standard_decrease_factor():
    """
    Calculate a standard decrease factor to be used when decrease factors are not varied.

    Returns:
        numpy.array: An array of standard decrease factors.
    """
    standard_factor = 0.7  # Example standard factor
    return np.full(36, standard_factor)  # Assuming 36 directions (0-350 in steps of 10)

def some_complex_calculation_based_on_fetch(fetch):
    """
    Placeholder function for complex decrease factor calculation based on fetch.

    Args:
        fetch (float): The fetch value for which to calculate the decrease factor.

    Returns:
        float: The calculated decrease factor.
    """
    # Placeholder for actual logic
    return 0.7  # Example: return a constant value for simplicity

def print_debug_info(unlimited_fetch_table, fetch_table, decrease_factor):
    """
    Print debug information including fetch tables and decrease factors.

    Args:
        unlimited_fetch_table (dict): A dictionary containing unlimited fetch data.
        fetch_table (dict): A dictionary containing fetch data.
        decrease_factor (numpy.array): An array of decrease factors for each direction.
    """
    print("Debug Information:")
    print("------------------")
    print("Angle   Fetch   Unlimited Fetch   Decrease Factor")
    for direction in range(0, 360, 10):
        fetch = fetch_table.get(direction, 'N/A')
        unlimited_fetch = unlimited_fetch_table.get(direction, 'N/A')
        factor = decrease_factor[int(direction / 10)]  # Assuming decrease_factor array is indexed by direction/10
        print(f"{direction:3d}°{fetch:>10}{unlimited_fetch:>18}{factor:>17.2f}")

    print("\n")

import numpy as np

def initialize_sea_bins(first_seas, sea_calc, winds, bin_deltas, bin_weights):
    """
    Initialize the sea bins based on the first sea conditions and the provided wind data.

    Args:
        first_seas (float): The initial sea condition (height).
        sea_calc (object): An instance of the sea calculation model.
        winds (list): A list of tuples representing wind direction, speed, and duration.
        bin_deltas (list): A list of bin deltas for calculation.
        bin_weights (list): A list of bin weights for calculation.

    Returns:
        numpy.array: An array representing the initialized sea bins.
    """
    sea_bins = np.zeros(36)  # Assuming 36 bins (one for each 10 degrees of direction)

    initial_wind = winds[0]
    if first_seas == 0:
        # Initialize sea bins from wind data if no initial sea condition is provided
        duration = 4.0  # Example duration, adjust as necessary
        sea_bins = init_seas_from_wind(sea_calc, sea_bins, initial_wind, duration, bin_deltas, bin_weights)
    else:
        # Initialize sea bins from the provided first sea condition
        sea_bins = init_seas_from_first_seas(sea_calc, sea_bins, initial_wind, first_seas, bin_deltas, bin_weights)

    return sea_bins

def init_seas_from_wind(sea_calc, sea_bins, wind, duration, bin_deltas, bin_weights):
    """
    Initialize sea bins based on wind data.

    Additional implementation details...
    """

    # Placeholder for actual logic
    return sea_bins

def init_seas_from_first_seas(sea_calc, sea_bins, wind, first_seas, bin_deltas, bin_weights):
    """
    Initialize sea bins based on the first sea conditions.

    Additional implementation details...
    """

    # Placeholder for actual logic
    return sea_bins

def calculate_seas(sea_bins, winds, sea_calc, decrease_factor, bin_deltas, bin_weights, 
                   return_dir, return_pd_dir, debug):
    """
    Calculate sea conditions based on provided winds and sea calculation model.

    Args:
        sea_bins (numpy.array): An array representing initial sea bins.
        winds (list): A list of tuples representing wind direction, speed, and duration.
        sea_calc (object): An instance of the sea calculation model.
        decrease_factor (numpy.array): An array of decrease factors for each direction.
        bin_deltas (list): A list of bin deltas for calculation.
        bin_weights (list): A list of bin weights for calculation.
        return_dir (bool): Flag to return direction of seas.
        return_pd_dir (bool): Flag to return period and direction of seas.
        debug (bool): Flag to enable debug mode.

    Returns:
        list: A list of calculated sea conditions.
    """
    m_seas = []
    for i, wind in enumerate(winds):
        w, duration = get_wind(wind, winds, i, wind_weights)

        sea_bins = update_bins(sea_calc, sea_bins, w, duration, decrease_factor, bin_deltas, bin_weights)

        if debug:
            print_wind_and_sea_bins(w, duration, sea_bins)
        
        if return_pd_dir:
            m_seas.append(get_seas_with_pd(sea_calc, sea_bins, w))
        elif return_dir:
            m_seas.append(get_seas_with_dir(sea_bins))
        else:
            m_seas.append(get_max_seas(sea_bins))

    return m_seas

# Placeholder for auxiliary functions used within calculate_seas.
def get_wind(current_wind, winds, index, wind_weights):
    """
    Calculate the effective wind for the current time step.

    Additional implementation details...
    """
    # Placeholder for actual logic
    return current_wind

def update_bins(sea_calc, sea_bins, wind, duration, decrease_factor, bin_deltas, bin_weights):
    """
    Update sea bins based on the current wind and sea calculation model.

    Additional implementation details...
    """
    # Placeholder for actual logic
    return sea_bins

def print_wind_and_sea_bins(wind, duration, sea_bins):
    """
    Print wind and sea bin information for debugging purposes.

    Additional implementation details...
    """
    # Placeholder for actual logic

def get_seas_with_pd(sea_calc, sea_bins, wind):
    """
    Get sea conditions with period and direction.

    Additional implementation details...
    """
    # Placeholder for actual logic
    return []

def get_seas_with_dir(sea_bins):
    """
    Get sea conditions with direction.

    Additional implementation details...
    """
    # Placeholder for actual logic
    return []

def get_max_seas(sea_bins):
    """
    Get the maximum sea height from the sea bins.

    Additional implementation details...
    """
    # Placeholder for actual logic
    return max(sea_bins)

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
        if f == 'U':
            f = 400.0
        fetchForDecreaseFactor[d] = f
    fetchForDecreaseFactor = calcAverageFetches(fetchForDecreaseFactor)
            
    if averageFetch:
        fetchTable = calcAverageFetches(fetchTable)
    
    if calcType in ['deep', 'mixed'] or depthTable is None:
        
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
    
    mSeas = [getSeasToReturn(seaBins, returnDir)]
    
    if returnPdDir:
        windSpd = winds[0][1]
        windDir = winds[0][0]
        mSeas = [get_seas(SeaCalc, seaBins, windSpd, windDir, returnDir, returnPdDir)]
                
    for i in range(1, len(winds)):

        # update sea bins
        if DEBUG: print("pre update bins\n"), np.round(seaBins, 2)

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

        if DEBUG: print("updated seaBins for", w[0], round(w[1]))
        #print np.round(seaBins, 1)
        if DEBUG: print(np.max(seaBins))
        
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
        sea_pd = SeaCalc.calcPeriodFromWind(windSpd, avDir)
        
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



#
# Fetch and depth information
#

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
            unlimitedFetches[dirn] = float(fetch) if fetch != 'U' else 'U'
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
                depths[dirn] = 30.0
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
            fetch = maxFetch if fetch == 'U' else float(fetch)
            if fetch > maxFetch:
                fetch = maxFetch
            fetches[dirn] = fetch

            # Turn depth into a number if it exists
            if r['depth'] != '':
                depth = float(r['depth'])
                depths[dirn] = depth
            else:
                depths[dirn] = 60
            
    # check for any depth values
    if depths.keys():
        for dirn in fetches.keys():
            if dirn not in depths:
                depths[dirn] = 30.0
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


# def test_calcEquivDuration():

#     print("15 knots, 100 nm fetch, 5 hours => 0.8m")
#     print("seas", seasFromFetchAndDuration(15, 5.0, 100.0))

#     dur = calcEquivDuration(0.8, 15.0, 100.0)
#     print("duration", dur)


# def test_calcSeaFromGDCurves():

#     tests = [
#         # (speed, duration, fetch)
#         (10.0, 3.0, 185),
#     ]

#     for speed, duration, fetch in tests:
    
#         print("speed: {}, duration: {}, fetch: {}, seas: {}".format(
#             speed,
#             duration,
#             fetch,
#             calcSeaFromGDCurves(speed, duration, fetch)
#             ))
        
#     exit()

#####################################################################################

#test_calcEquivDuration()

#print autoSeas('Enfield and Vincent', WINDS)