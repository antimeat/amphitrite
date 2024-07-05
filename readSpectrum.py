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
import pandas as pd
import cmocean

# Set the Numba cache directory
numba_cache_dir = '/tmp/numba_cache'
os.environ['NUMBA_CACHE_DIR'] = numba_cache_dir
os.environ[ 'NUMBA_DISABLE_JIT' ] = '1'

# Create the directory if it doesn't exist
if not os.path.exists(numba_cache_dir):
    os.makedirs(numba_cache_dir)
    os.chmod(numba_cache_dir, 0o777)

def clip(ds, boundary = {'min_lon':110.88, 'min_lat':-25.68, 'max_lon':121.47,'max_lat':-16.38}):
    # clip dataset my lats and lons
    ds = ds.copy()
    
    mask_lon = (ds.longitude >= boundary['min_lon']) & (ds.longitude <= boundary['max_lon'])
    mask_lat = (ds.latitude >= boundary['min_lat']) & (ds.latitude <= boundary['max_lat'])
    cropped_ds = ds.where(mask_lon, drop=True)
    cropped_ds = ds.where(mask_lat, drop=True)
    
    return cropped_ds

def amendVariablesNames_old(filename,site):
    """changes the 'dir' variable name as it clashes with model internal names
    """
    #print(filename)
    try:
        ds = xr.open_dataset(filename,site)
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
    ws = ws.where(ws.station_name == site, drop=True)
    
    return ws

def amendVariablesNames_current(filename,site):
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
    ws = ws.where(ws.station_name == site, drop=True)
    
    return ws

def amendVariablesNames(filename, site):
    """Changes the 'dir' variable name as it clashes with model internal names
    and interpolates both direction and frequency to a finer resolution.
    """
    try:
        ds = xr.open_dataset(filename)
    except Exception as e:
        print(f"Error opening dataset: {e}")
        return None
    
    # Handle station names
    site_names = [''.join(stn.astype(str)) for stn in ds.station_name.values]
    ds['station_name'] = xr.DataArray(np.array(site_names), coords={'station': ds.station}, dims=['station'])
    
    ws = wavespectra.read_dataset(ds)
    ws['station_name'] = ds.rename({'station':'site'}).station_name
    ws = ws.where(ws.station_name == site, drop=True)
    
    # Interpolate the direction and frequency to a finer resolution
    new_freq = np.logspace(np.log10(ws.spec.freq.min()), np.log10(ws.spec.freq.max()), num=72)
    new_dir = np.arange(0, 360, 5)
    ws_efth_interp = ws.efth.sortby("dir").spec.interp(freq=new_freq, dir=new_dir, maintain_m0=True)
    
    #Create the new dataset
    new_ds = xr.Dataset(
        {
            "efth": ws_efth_interp,
            "lon": ws.lon,
            "lat": ws.lat,
            "dpt": ws.dpt,
            "wspd": ws.wspd,
            "wdir": ws.wdir,
            "station_name": ws.station_name,
        },
        coords={
            "time": ws.time,
            "site": ws.site,
            "freq": new_freq,
            "dir": new_dir,
        },
        attrs={**ws.attrs},
    )
    
    try:
        new_ws = wavespectra.read_dataset(new_ds)
    except Exception as e:
        print(f"Error creating wavespectra.SpecDataset: {e}")
        return None
    
    return new_ws.sortby(["time","dir"])

def noPartition(ws):
    """
    No partition wave statistics
    """
    #read in file
    ws_total = ws.spec.stats(["hs", "hmax", "tp", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    
    ws['hs'] = ws_total.hs
    ws['hmax'] = ws_total.hmax
    ws['tm01'] = ws_total.tm01
    ws['tm02'] = ws_total.tm02
    ws['dpm'] = ws_total.dpm
    ws['dm'] = ws_total.dm
    ws['dspr'] = ws_total.dspr
    ws['tp'] = ws_total.tp
    ws['dp'] = ws_total.dp

    # dp and tp are recalculated due to bug in wavespectra ??
    try:
        peak_stats = get_peak_stats(ws.spec.efth)
        ws["tp"].values = peak_stats.tp.values.reshape(-1,1)
        ws["dp"].values = peak_stats.dp.values.reshape(-1,1)
        ws["dpm"] = ws["dpm"].fillna(ws["dp"])
        
    except Exception as e:
        print(f"Error in recalcing tp and dp in noPartition: {e}")        
    return ws
    
def onePartition(ws, filename, site, period):
    """
    Customer single partition split function
    
    Parameters
    ----------
    ws : wavespectra
        The wavespectra dataset.    
    filename : str
        A string for the netCDF spectral file.
    site : str
        A string for the site name.
    period : int
        The wave period to split the data.

    Returns
    -------
    xarray
        An xarray object with the partitioned and total wave paramters, and spectrum"""
    
    # print(f"one_partition period: {period}")
    
    #read in file
    # ws = amendVariablesNames(filename,site)
    ws_total = ws.spec.stats(["hs", "hmax", "tp", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    
    #get sea and swell split
    #sea = ws.spec.split(fmin=1/period).chunk({"freq": -1})
    sea = ws.spec.split(fmin=1/period)
    sea_stats = sea.spec.stats(["hs", "hmax", "tp", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    # sea_stats["tp"].values = get_tp(sea.spec.oned().to_dataframe('efth').reset_index()).values        
    # swell = ws.spec.split(fmax=1/period).chunk({"freq": -1})
    swell = ws.spec.split(fmax=1/period)
    swell_stats = swell.spec.stats(["hs", "hmax", "tp", "tm01", "tm02", "dpm", "dp", "dm", "dspr"])
    # swell_stats["tp"].values = get_tp(swell.spec.oned().to_dataframe('efth').reset_index()).values        
    
    ws['hs'] = ws_total.hs
    ws['hmax'] = ws_total.hmax
    ws['tp'] = ws_total.tp
    ws['tm01'] = ws_total.tm01
    ws['tm02'] = ws_total.tm02
    ws['dpm'] = ws_total.dpm
    ws['dp'] = ws_total.dp
    ws['dm'] = ws_total.dm
    ws['dspr'] = ws_total.dspr
    
    # dp and tp are recalculated due to bug in wavespectra ??
    peak_stats = get_peak_stats(ws.efth)
    ws["tp"].values = peak_stats.tp.values.reshape(-1,1)
    ws["dp"].values = peak_stats.dp.values.reshape(-1,1)
    ws["dpm"] = ws["dpm"].fillna(ws["dp"])
    
    #append partitioned variables to file
    ws['hs_sea'] = sea_stats.hs
    ws.hs_sea.attrs['standard_name'] = ws.hs_sea.attrs['standard_name']+'_sea_partition'
    ws['hmax_sea'] = sea_stats.hmax
    ws.hmax_sea.attrs['standard_name'] = ws.hmax_sea.attrs['standard_name']+'_sea_partition'
    
    # ws['tp_sea'] = sea_stats.tp
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
    
    # dp and tp are recalculated due to bug in wavespectra ??
    peak_stats = get_peak_stats(sea)
    ws["tp_sea"].values = peak_stats.tp.values.reshape(-1,1)
    ws["dp_sea"].values = peak_stats.dp.values.reshape(-1,1)
    ws["dpm_sea"] = ws["dpm_sea"].fillna(ws["dp_sea"])
    
    # ws['tp_sw'] = swell_stats.tp
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
    
    # dp and tp are recalculated due to bug in wavespectra ??
    peak_stats = get_peak_stats(swell)
    ws["tp_sw"].values = peak_stats.tp.values.reshape(-1,1)
    ws["dp_sw"].values = peak_stats.dp.values.reshape(-1,1)
    ws["dpm_sw"] = ws["dpm_sw"].fillna(ws["dp_sw"])
    
    # print(f"ws_sea: {ws['hs_sea']}, ws_sw: {ws['hs_sw']}")
    return ws

def rangePartition(ws, start, end):
    """
    Customer single partition split function
    Parameters
    ----------
    ws : wavespectra
        The wavespectra dataset.    
    start : int
        start of the range partition period (min)
    end : int
        end of the range partition period (max)
    Returns
    -------
    xarray
        An xarray object with the partitioned and total wave paramters, and spectrum
    """
    # here we make a minor tweaks to start and end to ensure we dont end with crossover values between partitions
    end += 0.49 
    if start > 5:
        start += 0.51        
        
    try: 
        part = ws.spec.split(fmin=1/end, fmax=1/start)
        part.name ='efth'
        params = part.spec.stats(["hs", "hmax", "tm01", "tm02", "dpm", "dp", "dm", "dspr","tp"])
        #derive peak stats for period and dir
        peak_stats = get_peak_stats(part)
        # params["tp"].values = get_tp(part.spec.oned().to_dataframe('efth').reset_index()).values
        # params["dp"].values = get_dp(part.to_dataframe('efth').reset_index()).values
            
        params['tp'].values = peak_stats.tp.values.reshape(-1,1)
        params['dp'].values = peak_stats.dp.values.reshape(-1,1)
        params['station_name'] = ws.station_name
        
        # replance NaN values in dpm with values from dp
        params['dpm'] = params['dpm'].fillna(params['dp'])
        
    except Exception as e:
        print(f"Error in rangePartition: {e}")
        return None
    
    return params

def get_peak_stats(partition):
    """
    Take the partition and calculate peak stats (Tp and Dp) from the 2d Spectrum
    """
    max_dir = partition.max(dim="freq").idxmax(dim="dir")
    max_freq = partition.max(dim="dir").idxmax(dim="freq")
    max_efth = partition.max(dim=["dir", "freq"]).values.flatten()
    
    tp = (1 / max_freq).values.flatten()
    dp = max_dir.values.flatten()
    
    new = pd.DataFrame({'efth': max_efth, 'tp': tp, 'dp': dp}, index=partition.time.values)
    new.index = pd.to_datetime(new.index)
    
    return new.round(2)    

def get_tp(df, group_col='time', x_col='efth', y_col='freq'):
    """
    Get the energy with the highest value for each timestep
    and extract the corresponding frequency, then invert to seconds and create dataframe.

    Args:
        df (pd.DataFrame): Dataframe of 1D spectrum for a single site.
        group_col (str): Name of the column to group by (default: 'group').
        x_col (str): Name of the column with values to compare (default: 'x').
        y_col (str): Name of the column to extract values from (default: 'y').

    Returns:
        pd.DataFrame: Dataframe containing tp
    """
    try: 
        max_x_rows = df.loc[df.groupby(group_col)[x_col].idxmax()]
        result = max_x_rows[y_col]
        tp = pd.DataFrame(np.round(1/result, 2))
        tp.index = df[group_col].unique()
        tp.columns = ['tp']
        
    except Exception as e:
        print(f"Error in get_tp: {e}")
        return None
    
    return tp

def get_dp(df, group_col='time', x_col='efth', y_col='dir'):
    """
    Get the energy with the highest value for each timestep
    and extract the corresponding frequency, then invert to seconds and create dataframe.

    Args:
        df (pd.DataFrame): Dataframe of 1D spectrum for a single site.
        group_col (str): Name of the column to group by (default: 'group').
        x_col (str): Name of the column with values to compare (default: 'x').
        y_col (str): Name of the column to extract values from (default: 'y').

    Returns:
        pd.DataFrame: Dataframe containing dp
    """
    df_copy = df.copy()

    try:
        result = df_copy.groupby([group_col, y_col])[x_col].sum().reset_index()
        result = result.loc[result.groupby(group_col)[x_col].idxmax()]
        
        dp = pd.DataFrame(np.round(result['dir'].values, 2))
        dp.index = df[group_col].unique()
        dp.columns = ['dp']
            
    except Exception as e:
        print(f"Error in get_dp: {e}")
        return None
   
    return dp
