"""
Module for loading and processing data from OFCAST sources.

Authors: Rabi Rivett, Jim Richardson, Daz Vink
"""

from datetime import datetime
import os
import pandas as pd
import scipy.signal
import numpy as np
import re

import data

DIR_PATH = "/net/wa-aifs-local/srv/local/web/ofcastData/gfe_data/point_data/"
FILE_PATH = DIR_PATH + "latest_{}.csv"


def get_issues():
    """
    Get a list of issues for the given sources.

    Returns:
        A list of issues.
    """
    
    issues = []

    for src in ['op', 'backup']:

        fp = FILE_PATH.format(src)

        if os.path.isfile(fp):
            mtime = os.path.getmtime(fp)
            mtime = datetime.fromtimestamp(mtime).strftime('%Y-%m-%d %H:%M:%S')

            issues.append("{} + {}".format(src, mtime))
            issues.append("{} + smoothed + {}".format(src, mtime))
            issues.append("{} + special_sauce + {}".format(src, mtime))

    return issues


def smooth_max(df):
    """
    Apply a Savitzy Golay smoothing function to P5's and max on wind speed and hs.

    Args:
        df (pandas.DataFrame): The dataframe to be smoothed.

    Returns:
        pandas.DataFrame: The smoothed dataframe.
    """
    
    cols = ["wnd_spd", "total_ht"]
    
    if 'total_ht' not in df:
        cols = ["wnd_spd"]
    
    for col in cols:
        s = df[col].values
        if 'max' in col:
            filtered = scipy.signal.savgol_filter(s,15,2,mode='nearest')
        elif 'air_temp' in col:
            filtered = scipy.signal.savgol_filter(s,15,2,mode='nearest')
        else:
            filtered = scipy.signal.savgol_filter(s,9,2,mode='nearest')
        df[col] = filtered

    return df


def special_sauce(df,**kwargs):
    '''
    Apply a special sauce multiplier.

    Args:
        df (pandas.DataFrame): The dataframe to be processed.
        **kwargs: Keyword arguments for special sauce calculator.

    Returns:
        pandas.DataFrame: The processed dataframe.
    '''
   
    wnd_limit = 12
    wnd_multi = 1.1
    hs_limit = 1.5
    hs_multi = 1.15
    
    if kwargs:
        wnd_limit = int(kwargs['wnd_limit'])
        wnd_multi = float(kwargs['wnd_multi'])
        hs_limit = float(kwargs['hs_limit'])
        hs_multi = float(kwargs['hs_multi'])
    
    cols = ["wnd_spd", "total_ht"]
    
    if 'total_ht' not in df:
        cols = ["wnd_spd"]
    
    for col in cols:
        s = df[col].values
        if 'max' in col:
            filtered = scipy.signal.savgol_filter(s,15,2,mode='nearest')
        elif 'air_temp' in col:
            filtered = scipy.signal.savgol_filter(s,15,2,mode='nearest')
        else:
        
            if col == 'wnd_spd':
                s = np.where(s > wnd_limit, s.astype(float)*wnd_multi, s.astype(float))
            else:
                s = np.where(s > hs_limit, s.astype(float)*hs_multi, s.astype(float))
                    
            filtered = scipy.signal.savgol_filter(s,5,2,mode='nearest')
        
        df[col] = filtered

    return df

def shorten_site_name(site_name):
    """Get rid of any trailing numbers of days in the site name"""
    match = re.search(r'\d+', site_name)
    name = site_name
    if match:
        start_index = match.start()
        return name[:start_index].rstrip()  # rstrip() removes trailing whitespace
    else:
        return name  # Return original name if no number found


def load_file(site, issue):
    """
    Load data from a CSV file for the given site and issue.

    Args:
        site (str): The name of the site.
        issue (str): The name of the issue.

    Returns:
        pandas.DataFrame: The loaded dataframe.
    """
    fp = FILE_PATH.format(issue)
    
    # shorten our site names
    site = shorten_site_name(site)
    
    try:
        df = pd.read_csv(fp)
        df['name'] = df['name'].apply(lambda x: shorten_site_name(x))
        df = df[df["name"] == site].copy()
        
        df['time'] = pd.to_datetime(df['time'], format='%Y-%m-%d %H:%M:%S')
    
    except IOError:
        # no file
        df = None

    return df

def load(site, issue):
    """
    Load data for the given site and issue.

    Args:
        site (str): The name of the site.
        issue (str): The name of the issue.
        **kwargs: Keyword arguments for special_sauce function.

    Returns:
        pandas.DataFrame: The loaded dataframe.
    """
    
    src = issue.split(' + ')[0]    
    df = load_file(site, src)
    
    if df is not None:

        # make wnd_spd and wnd_dir columns
        df = df[['time', 'field', 'value']].pivot(index='time', columns='field', values='value').reset_index()
        df = df.rename(columns={'Wind_Dir': 'wnd_dir', 'Wind_Mag': 'wnd_spd', 'SigWaveHgt': 'total_ht', 'T': 'air_temp'})

        if 'total_ht' in df:
            df['total_ht'] = df['total_ht'].interpolate(method='linear')

        if 'smoothed' in issue:
            df = smooth_max(df)
        
        data.round_wnd_dir(df)
        data.fix_wnd(df)

    return df


if __name__ == "__main__":

    site = 'Woodside - North Rankin 2 days'
    issue = 'op + smoothed'
    df = load(site,issue)

    #print(df.to_json(orient='records'))
    print(df)
    #print(df.columns)

