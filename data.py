import numpy as np


def dir2uv(df):

    if 'wnd_dir' in df:
        df['u'] = np.cos(np.radians(df.wnd_dir))
        df['v'] = np.sin(np.radians(df.wnd_dir))
        df = df.drop(['wnd_dir'], axis='columns')
    return df
    

def uv2dir(df):

    if 'u' in df and 'v' in df:
        df['wnd_dir'] = np.degrees(np.arctan2(df.v, df.u)) % 360.0
        df = df.drop(['u', 'v'], axis='columns')    

    return df
    
    
def interpolate_values(df):

    df = df.set_index('time')
    df = dir2uv(df)
    df = df.resample('1h').interpolate(method='index')
    df = uv2dir(df)
    df = df.round(1)
    df = df.reset_index()
    
    return df


def round_wnd_dir(df):

    df['wnd_dir'] = np.round(df['wnd_dir'] / 10.0) * 10.0

    return df
    
def fix_wnd(df):
    """
    Fix the wnd_spd < 3 to be 3, and let 0 = 360 
    """
    
    df["wnd_spd"].mask(df["wnd_spd"] < 3,3,inplace=True)
    df["wnd_dir"].mask(df["wnd_dir"] == 0,360,inplace=True)
    
    return df
    
def fudge_residuals(df):
    """
    Fudge the residual swells to build shoulders around high and low values.
    """
    
    df["wnd_spd"].mask(df["wnd_spd"] < 3,3,inplace=True)
    df["wnd_dir"].mask(df["wnd_dir"] == 0,360,inplace=True)
    
    return df
    

