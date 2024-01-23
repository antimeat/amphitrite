#!/cws/anaconda/envs/mlenv/bin/python -W ignore

##################################################################
#
#   Name: readSpectrum
#   Author: Leo Peach
#   Purpose: To read wave spectrum file into wave parameters
#   Version: v0.1
#
###################################################################

import xarray as xr
import numpy as np
import wavespectra

import os
os.environ[ 'NUMBA_CACHE_DIR' ] = '/tmp/numba_cache'
os.environ[ 'NUMBA_DISABLE_JIT' ] = '1'

def clip(ds, boundary = {'min_lon':110.88, 'min_lat':-25.68, 'max_lon':121.47,'max_lat':-16.38}):
    # clip dataset my lats and lons
    ds = ds.copy()
    
    mask_lon = (ds.longitude >= boundary['min_lon']) & (ds.longitude <= boundary['max_lon'])
    mask_lat = (ds.latitude >= boundary['min_lat']) & (ds.latitude <= boundary['max_lat'])
    cropped_ds = ds.where(mask_lon, drop=True)
    cropped_ds = ds.where(mask_lat, drop=True)
    
    return cropped_ds

def amendVariablesNames_old(filename):
    """changes the 'dir' variable name as it clashes with model internal names
    """
    #print(filename)
    try:
        ds = xr.open_dataset(filename)
        #ds = clip(ds)
    except:
        ds = filename
        return ds
    #ds = ds.rename({'dir':'tm_dir'})
    siteNames = []
    for stn in ds.station_name.values:
        decoded = [s.decode('UTF-8') for s in stn.flatten()]
        #print(''.join(decoded))
        siteNames.append(''.join(decoded))
    
    me = xr.DataArray(np.array(siteNames), coords={'station': ds.station},dims=['station'])
    ds['station_name'] = me
    ws = wavespectra.read_dataset(ds)
    ws['station_name'] = ds.rename({'station':'site'}).station_name
    return ws

def amendVariablesNames(filename):
    """changes the 'dir' variable name as it clashes with model internal names
    """
    try:
        ds = xr.open_dataset(filename)
    except:
        ds = filename
        return ds
    #ds = ds.rename({'dir':'tm_dir'})
    siteNames = []
    for stn in ds.station_name.values:
        siteNames.append(''.join(stn.astype(str)))
    me = xr.DataArray(np.array(siteNames), coords={'station': ds.station},dims=['station'])
    ds['station_name'] = me
    ws = wavespectra.read_dataset(ds)
    ws['station_name'] = ds.rename({'station':'site'}).station_name
    return ws

def noPartition(filename):
    """no partition wave statistics
    """
    
    #read in file
    ws = amendVariablesNames(filename)
    ws_total = ws.spec.stats(["hs", "hmax", "tp", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    
    ws['hs'] = ws_total.hs
    ws['hmax'] = ws_total.hmax
    ws['tp'] = ws_total.tp
    ws['tm01'] = ws_total.tm01
    ws['tm02'] = ws_total.tm02
    ws['tp'] = ws_total.tp
    ws['dpm'] = ws_total.dpm
    ws['dp'] = ws_total.dp
    ws['dm'] = ws_total.dm
    ws['dspr'] = ws_total.dspr
    
    return ws
    

def onePartition(filename, period = 9):
    """
    Customer single partition split function
    
    Parameters
    ----------
    filename : str
        A string for the netCDF spectral file.
    period : int
        The wave period to split the data

    Returns
    -------
    xarray
        An xarray object with the partitioned and total wave paramters, and spectrum"""
    
    # print(f"one_partition period: {period}")
    
    #read in file
    ws = amendVariablesNames(filename)
    ws_total = ws.spec.stats(["hs", "hmax", "tp", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    
    #get sea and swell split
    sea = ws.spec.split(fmin=1/period).chunk({"freq": -1})
    sea_stats = sea.spec.stats(["hs", "hmax", "tp", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    swell = ws.spec.split(fmax=1/period).chunk({"freq": -1})
    swell_stats = swell.spec.stats(["hs", "hmax", "tp", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    
    ws['hs'] = ws_total.hs
    ws['hmax'] = ws_total.hmax
    ws['tp'] = ws_total.tp
    ws['tm01'] = ws_total.tm01
    ws['tm02'] = ws_total.tm02
    ws['tp'] = ws_total.tp
    ws['dpm'] = ws_total.dpm
    ws['dp'] = ws_total.dp
    ws['dm'] = ws_total.dm
    ws['dspr'] = ws_total.dspr
    
    #append partitioned variables to file
    ws['hs_sea'] = sea_stats.hs
    ws.hs_sea.attrs['standard_name'] = ws.hs_sea.attrs['standard_name']+'_sea_partition'
    ws['hmax_sea'] = sea_stats.hmax
    ws.hmax_sea.attrs['standard_name'] = ws.hmax_sea.attrs['standard_name']+'_sea_partition'
    ws['tp_sea'] = sea.spec.tp(smooth=False).fillna(1 / sea.freq.min())
    ws.tp_sea.attrs['standard_name'] = ws.tp_sea.attrs['standard_name']+'_sea_partition'
    ws['tm01_sea'] = sea_stats.tm01
    ws.tm01.attrs['standard_name'] = ws.tm01.attrs['standard_name']+'_sea_partition'
    ws['tm02_sea'] = sea_stats.tm02
    ws.tm02.attrs['standard_name'] = ws.tm02.attrs['standard_name']+'_sea_partition'
    ws['dpm_sea'] = sea_stats.dpm
    ws.dpm_sea.attrs['standard_name'] = ws.dpm_sea.attrs['standard_name']+'_sea_partition'
    ws['dp_sea'] = sea_stats.dp
    ws.dp_sea.attrs['standard_name'] = ws.dp_sea.attrs['standard_name']+'_sea_partition'
    ws['dm_sea'] = sea_stats.dm
    ws.dm_sea.attrs['standard_name'] = ws.dm_sea.attrs['standard_name']+'_sea_partition'
    ws['dspr_sea'] = sea_stats.dspr
    ws.dspr.attrs['standard_name'] = ws.dspr_sea.attrs['standard_name']+'_sea_partition'
    
    ws['hs_sw'] = swell_stats.hs
    ws.hs_sw.attrs['standard_name'] = ws.hs_sw.attrs['standard_name']+'_swell_partition'
    ws['hmax_sw'] = swell_stats.hmax
    ws.hmax_sw.attrs['standard_name'] = ws.hmax_sw.attrs['standard_name']+'_swell_partition'
    ws['tp_sw'] = swell.spec.tp(smooth=False).fillna(1 / swell.freq.max())
    ws.tp_sw.attrs['standard_name'] = ws.tp_sw.attrs['standard_name']+'_swell_partition'
    ws['tm01_sw'] = swell_stats.tm01
    ws.tm01_sw.attrs['standard_name'] = ws.tm01_sw.attrs['standard_name']+'_swell_partition'
    ws['tm02_sw'] = swell_stats.tm02
    ws.tm02_sw.attrs['standard_name'] = ws.tm02_sw.attrs['standard_name']+'_swell_partition'
    ws['dpm_sw'] = swell_stats.dpm
    ws.dpm_sw.attrs['standard_name'] = ws.dpm_sw.attrs['standard_name']+'_swell_partition'
    ws['dp_sw'] = swell_stats.dp
    ws.dp_sw.attrs['standard_name'] = ws.dp.attrs['standard_name']+'_swell_partition'
    ws['dm_sw'] = swell_stats.dm
    ws.dm_sw.attrs['standard_name'] = ws.dm_sw.attrs['standard_name']+'_swell_partition'
    ws['dspr_sw'] = swell_stats.dspr
    ws.dspr_sw.attrs['standard_name'] = ws.dspr_sw.attrs['standard_name']+'_swell_partition'
    
    # print(f"ws_sea: {ws['hs_sea']}, ws_sw: {ws['hs_sw']}")
    return ws
    
def rangePartition(filename, start, end):
    """
    Customer single partition split function
    
    Parameters
    ----------
    filename : str
        A string for the netCDF spectral file.
    start : int
        start of the range partition period (min)
    end : int
        end of the range partition period (max)
        
    Returns
    -------
    xarray
        An xarray object with the partitioned and total wave paramters, and spectrum
        
        
    Example
    -------
    
    rangePartition(filename, 8, 16)
    
    """
    # a fudge factor that was discovered through trial and error to match hs from def onePartition()
    if start > 5:
        start += 0.59
        
    #read in file
    ws = amendVariablesNames(filename)
        
    #get sea and swell split
    part = ws.spec.split(fmin=1/end, fmax=1/start ).chunk({"freq": -1})
    params = part.spec.stats(["hs", "hmax", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    
    #we do a fudge with tp depending on which end of the partition to push low energy
    tp = part.spec.tp(smooth=False).fillna(1 / part.freq.min())
    
    #if its a swell partition push low energy tp to the start
    if start > 5:
        tp = part.spec.tp(smooth=False).fillna(1 / part.freq.max())
        
    params['tp'] = tp
    params['station_name'] = ws.station_name
    
    return params

def singlePartition(filename, period):
    """Placeholder"""
    return
    