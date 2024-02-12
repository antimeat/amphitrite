"""
Authors: Rabi Rivett and Daz Vink

This script contains functions to extract data from the OfCast product page 
and parse it into a Pandas DataFrame. The functions include:

    - get_issues(): Returns a list of issues.
    - getProductsPrevious(userID, label): Extracts previously sent forecast links 
      from the OfCast product page.
    - getProductFileAndTime(userID, label): Extracts the configuration file name 
      and the 'current' issue time from the OfCast products page.
    - getProductFileName(userID, label): Gets the file name of the product.
    - getProductSession(userID, label): Gets the session number for the 'next' 
      forecast product.
    - getArchiveProductSession(userID, label, archive): Gets the session number 
      for the archived forecast product.
    - getArchiveProductUrl(userID, label, archive): Gets the URL for the archived 
      forecast product.
    - notSeparator(css): Checks whether the CSS is a separator.
    - parseCell(txt): Parses a table cell containing data.
    - parseModelCell(txt): Parses a table cell containing model data.
"""
# Import required modules
from urllib.parse import parse_qs
import numpy as np
from datetime import timedelta
from datetime_modulo import datetime
import pandas as pd
from bs4 import BeautifulSoup
from scipy.signal import savgol_filter
import requests
import re

DEBUG = False

#setup for op/dev servers
SERVER_OP = "http://wa-cws-op.bom.gov.au"
SERVER_DEV = "http://cws-01.bom.gov.au"
SERVER = SERVER_DEV

# Set URL for the table
TABLE_URL = SERVER + "/ofcast/cgi-bin/pct_view.pl?s={}&v=vtable&vc=2"

# Set time zones
TIME_ZONES = {
    'WST': timedelta(hours=8),
    'CST': timedelta(hours=9.5),
    'CXT': timedelta(hours=7),
    'UTC': timedelta(hours=0),
    'EST': timedelta(hours=10),
    'EDT': timedelta(hours=11)
}

# Set map of model fields
MODEL_FIELD_MAP = {
    # First is sectionless part of the table
    'First': dict(
        list({'Date': 'mdl_date'}.items()) + \
        list({'Time ({})'.format(tz): 'mdl_hour_{}'.format(tz) for tz in list(TIME_ZONES.keys())}.items())
    ),
    'Wind': {
        # most
        'Direction (deg)': 'mdl_wnd_dir',
        'Speed (kn)': 'mdl_wnd_spd',

        # with upper bound
        'Direction (degrees) (deg)': 'mdl_wnd_dir',
        'Speed (10m) (kn)': 'mdl_wnd_spd',
        'Upper bound (5%) (kn)': 'mdl_wnd_spd_95',

    },
    'Total Wave': {
        'Sig Ht (m)': 'mdl_total_ht',
        'Sig. Height (m)': 'mdl_total_ht',
        'Sig Height (m)': 'mdl_total_ht',
        'Upper bound (5%) (m)': 'mdl_total_ht_95'
    },
    'Sea/Swell': {
        'Sig Ht (m)': 'mdl_total_ht',
        'Sig Height (m)': 'mdl_total_ht',
    },
    'Seas': {
        'Sig. Height (m)': 'mdl_seas_ht',
        'Peak Period (sec)': 'mdl_seas_pd',
        'Peak Dir (degrees)': 'mdl_seas_dirn'        
    },
    'Sea Wave': {
        'Sig. Height (m)': 'mdl_seas_ht',
        'Peak Period (sec)': 'mdl_seas_pd',
        'Peak Dir (degrees)': 'mdl_seas_dirn'        
    },
    'Swell': {
        'Sig. Height (m)': 'mdl_swell_ht',
        'Peak Period (sec)': 'mml_swell_pd',
        'Peak Dir (degrees)': 'mdl_swell_dirn',        
        'Period (sec)': 'mdl_swell_pd',
        'Direction (deg)': 'mdl_swell_dirn'        
    },
}

for i in [1, 2, 3, 4]:
    MODEL_FIELD_MAP['Swell #{}'.format(i)] = {
        'Sig. Height (m)': 'mdl_swell_{}_ht'.format(i),
        'Peak Period (sec)': 'mdl_swell_{}_pd'.format(i),
        'Peak Dir (degrees)': 'mdl_swell_{}_dirn'.format(i),
        'Period (sec)': 'mdl_swell_{}_pd'.format(i),
        'Direction (deg)': 'mdl_swell_{}_dirn'.format(i),        
    }

FIELD_MAP = {
    # First is sectionless part of the table
    'First': dict(
        list({'Date': 'date'}.items()) + \
        list({'Time ({})'.format(tz): 'hour_{}'.format(tz) for tz in list(TIME_ZONES.keys())}.items())
    ),
    'Wind': {
        # most
        'Direction (deg)': 'wnd_dir',
        'Speed (kn)': 'wnd_spd',

        # with upper bound
        'Direction (degrees) (deg)': 'wnd_dir',
        'Speed (10m) (kn)': 'wnd_spd',
        'Upper bound (5%) (kn)': 'wnd_spd_95',

    },
    'Total Wave': {
        'Sig Ht (m)': 'total_ht',
        'Sig Height (m)': 'total_ht',
        'Sig. Height (m)': 'total_ht',
        'Upper bound (5%) (m)': 'total_ht_95'
    },
    'Sea/Swell': {
        'Sig Ht (m)': 'total_ht',
        'Sig Height (m)': 'total_ht',
        'Max Ht (m)': 'max_ht'
    },
    'Seas': {
        'Sig. Height (m)': 'seas_ht',
        'Peak Period (sec)': 'seas_pd',
        'Peak Dir (degrees)': 'seas_dirn',        
        'Period (sec)': 'seas_pd',
        'Direction (deg)': 'seas_dirn'        
    },
    'Sea Wave': {
        'Sig. Height (m)': 'seas_ht',
        'Peak Period (sec)': 'seas_pd',
        'Peak Dir (degrees)': 'seas_dirn',        
        'Period (sec)': 'seas_pd',
        'Direction (deg)': 'seas_dirn'        
    },
    'Swell': {
        'Sig. Height (m)': 'swell_1_ht',
        'Peak Period (sec)': 'swell_1_pd',
        'Peak Dir (degrees)': 'swell_1_dirn',        
        'Period (sec)': 'swell_1_pd',
        'Direction (deg)': 'swell_1_dirn'        
    },
}

for i in [1, 2, 3, 4]:
    FIELD_MAP['Swell #{}'.format(i)] = {
        'Sig. Height (m)': 'swell_{}_ht'.format(i),
        'Peak Period (sec)': 'swell_{}_pd'.format(i),
        'Peak Dir (degrees)': 'swell_{}_dirn'.format(i),
        'Period (sec)': 'swell_{}_pd'.format(i),
        'Direction (deg)': 'swell_{}_dirn'.format(i),        
    }


def changeServer(server):
    """Chance the ofcast server from dev to ops

    Args:
        server (_str_): either "dev" or "ops"
    """
    if "dev" in server.lower():
        SERVER = SERVER_DEV
    else:
        SERVER = SERVER_OP
            
    TABLE_URL = SERVER + "/ofcast/cgi-bin/pct_view.pl?s={}&v=vtable&vc=2"
    
    return SERVER, TABLE_URL
    
def get_issues():
    """Returns a list of issues to be addressed."""
    return ['raw','smoothed','special_sauce']

def getProductsPrevious(userID, label):
    """From the ofcast product page, extract the previously sent forecast links.

    Args:
        userID (str): The user ID.
        label (str): The forecast name in the OfCast product page.

    Returns:
        list: A list of tuples with session IDs and their corresponding session strings.
    """
    #keep track of previous sessionIDs
    sessionIDs = []

    pid = getProductFileName(userID, label)
    #print(pid)
    
    # label is the forecast name in the OfCast product page.
    url = SERVER + "/ofcast/cgi-bin/ctl_productdetail.pl?pid={}&l={}".format(pid,userID)		

    #get the htmlpage
    html = requests.get(url, timeout=5).content.decode('utf-8')
    soup = BeautifulSoup(html, "html.parser")

    #find the recent editions table
    recent_editions = soup.find(text='Recent Editions:')
    #print(recent_editions)
    table = soup.findAll('table')[3]
    #print(table)
    rows = table.findAll('tr')
    
    #look through each recent editions and if it was issued then add it to a list
    for tr in rows:
        #get the sessionID for the href link 
        sessionID = tr.find('a')
        
        #only keep issues that were sent
        sent_flag = tr.find(text='not sent')
        if sessionID and not sent_flag:
            sessionID = str(sessionID)
            sessionID = sessionID.split('/')[1].split("',")[0]
            sessionString = datetime.fromtimestamp(int(sessionID)).strftime('%d/%m %H:%M')
            sessionIDs.append((int(sessionID),sessionString))
   
       
    return sessionIDs        
       
    
def getProductFileAndTime(userID, label):
    """From the ofcast products page, extract the config file name and the 'current' issue time.

    Args:
        userID (str): The user ID.
        label (str): The forecast name in the OfCast product page.

    Returns:
        tuple: A tuple containing the file name and the 'current' issue time.
    """
    # label is the forecast name in the OfCast product page.
    url = SERVER + "/ofcast/cgi-bin/ctl_products.pl?l={}".format(userID)		

    page = requests.get(url, timeout=5).content.decode('utf-8')
        
    # Throw away everything after "Inactive Products"
    page = page.split("Inactive Products")[0]
    
    bs = BeautifulSoup(page.encode("utf-8"), "html.parser")
    
    for i, tbl in enumerate(bs.findAll("table")):
        # skip first table
        if i < 1:
            continue

        for j, tr in enumerate(tbl.findAll('tr')):

            tds = [td for _, td in enumerate(tr.findAll("td"))]

            if len(tds) == 1:
                # blank or header
                continue

            elif tds:
                # is a product row

                # get label for this row
                thisLabel = tds[0].text.strip().split(' (')[0]

                if thisLabel == label:

                    # work out the status
                    status = tds[-1].text

                    if status in ["Due", "OK", "OK (Outbox)"]:
                        # Not opened yet, use the Last issue
                        idx = 1

                    else:
                        # Forecast opened, use the new one
                        idx = 2

                    # product file name
                    href = tds[0].find('a', href=True)
                    q = parse_qs(href['href'].split('?')[1])
                    fileName = q['pid'][0]

                    # href from the issue we want
                    href = tds[idx].find('a', href=True)

                    nextTime = str(href).split('/')[1].split("'")[0]

                    return fileName, nextTime                    

    return None

def getProductFileName(userID, label):
    """Get the file name of the product.

    Args:
        userID (str): The user ID.
        label (str): The forecast name in the OfCast product page.

    Returns:
        str: The file name of the product.
    """
    fileName, productTime = getProductFileAndTime(userID, label)
        
    return fileName

def getProductSession(userID, label):
    """Get the session number for the 'next' forecast product.

    Args:
        userID (str): The user ID.
        label (str): The forecast name in the OfCast product page.

    Returns:
        str: The session number for the 'next' forecast product.
    """
    fileName, productTime = getProductFileAndTime(userID, label)

    if DEBUG:
        print(fileName, productTime)

    url = SERVER + "/ofcast/cgi-bin/pct_open.pl?p={}/{}&l={}".format(fileName, productTime, userID)

    if DEBUG:
        print('url', url)

    page = requests.get(url, timeout=5).content.decode('utf-8')

    if 'session_id' in page:
        sessionID = page.split("\n")[6].split("'")[1]
    else:
        sessionID = ''

    return sessionID

def getArchiveProductSession(userID, label, archive):
    """Get the session number for the 'next' forecast product in the archive.

    Args:
        userID (str): The user ID.
        label (str): The forecast name in the OfCast product page.
        archive (int): The number of the archive.

    Returns:
        list: A list containing the session ID and the product string.
    """

    archive = int(archive)
    
    if archive == 0:
        fileName, productTime = getProductFileAndTime(userID, label)
        productString = 'current'
    else:
        fileName = getProductFileName(userID, label)
        productTimes = getProductsPrevious(userID, label)
        
        if archive >= len(productTimes):
            productTime = None
        else:
            productTime = productTimes[archive][0]
            productString = productTimes[archive][1]  
        
    if DEBUG:
        print(fileName, productTime)

    url = SERVER + "/ofcast/cgi-bin/pct_open.pl?p={}/{}&l={}".format(fileName, productTime, userID)

    if DEBUG:
        print('url', url)

    page = requests.get(url, timeout=5).content.decode('utf-8')

    if 'session_id' in page:
        sessionID = page.split("\n")[6].split("'")[1]
    else:
        sessionID = ''

    return [sessionID,productString]

def getArchiveProductUrl(userID, label, archive):
    """Get the URL for the 'next' forecast product in the archive.

    Args:
        userID (str): The user ID.
        label (str): The forecast name in the OfCast product page.
        archive (int): The number of the archive.

    Returns:
        list: A list containing the URL and the product string.
    """

    archive = int(archive)

    if archive == 0:
        fileName, productTime = getProductFileAndTime(userID, label)
        productString = 'current'
    else:
        fileName = getProductFileName(userID, label)
        productTimes = getProductsPrevious(userID, label) 
        
        if archive >= len(productTimes):
            productTime = None
        else:
            productTime = productTimes[archive][0]
            productString = productTimes[archive][1]
    
    if DEBUG:
        print(fileName, productTime)

    url = SERVER + "/ofcast/cgi-bin/pct_open.pl?p={}/{}&l={}".format(fileName, productTime, userID)

    if DEBUG:
        print('url', url)

    page = requests.get(url, timeout=5).content.decode('utf-8')

    if 'session_id' in page:
        sessionID = page.split("\n")[6].split("'")[1]
    else:
        sessionID = ''

    return [url,productString]

def notSeparator(css):
    """Check if the CSS is a separator.

    Args:
        css (str): The CSS to check.

    Returns:
        bool: True if the CSS is not a separator, False otherwise.
    """
    return css != 'pdcolsep'


def parseCell(txt):
    """Parse the text in a cell.

    Args:
        txt (str): The text to parse.

    Returns:
        str: The parsed text.
    """
    # if square brackets in, take only what is before the first square bracket
	# if a minus sign with spaces around it, then no model data to put in square brackets so a ' - ' is used instead
    txt = txt.replace(' - ', '').split('[')[0]

    # remove white space
    txt = txt.strip()

    return txt

def parseModelCell(txt):
    """Parse the text in a model cell.

    Args:
        txt (str): The text to parse.

    Returns:
        str: The parsed text.
    """
    # if square brackets in, take only what is before the first square bracket
	# if a minus sign with spaces around it, then no model data to put in square brackets so a ' - ' is used instead
    
    try:
        txt = txt.replace(' - ', '').split('[')[1].split(']')[0]
    except:
        txt = txt.replace(' - ', '').split('[')[0] 

    # remove white space
    txt = txt.strip()

    return txt


def parseTable(tbl,data_type):
    """
    Parses a HTML table and returns a pandas DataFrame with the data.

    Args:
        tbl: The HTML table to be parsed.
        data_type: A string that indicates the type of data to be parsed.
                   Must be either 'model' or 'forecast'.

    Returns:
        A pandas DataFrame with the parsed data.
    """
    data = {}

    section = 'First'

    for row in tbl.findAll('tr'):

        first = row.find('td')
        field = first.text.strip()

        if 'sechdr' in first['class']:
            section = field

        # ignore if no map for this section
        if section not in FIELD_MAP:
            continue

        if field in FIELD_MAP[section]:

            if 'forecast' in data_type:
                vals = [parseCell(cell.text) for cell in row.find_all('td', class_=notSeparator)]
                # don't need the first val because it is the row header
                vals = vals[1:]
                data[FIELD_MAP[section][field]] = vals
            
            else:
                model_vals = [parseModelCell(cell.text) for cell in row.find_all('td', class_=notSeparator)]
                model_vals = model_vals[1:]
                data[FIELD_MAP[section][field]] = model_vals

    df = pd.DataFrame(data)

    return df


def getIssueTime(bs):
    """
    Extracts the issue time from a BeautifulSoup object containing a BOM weather forecast HTML page.

    Args:
        bs: The BeautifulSoup object.

    Returns:
        A datetime object representing the issue time.
    """
    text = bs.find("td", class_="pghead").text

    timeStr = text.strip().split("\n")[-1].strip()

    timeStr = timeStr.split("Issued ")[-1]
    #timeStr = '2000 WST, Wednesday 15 June 2016'

    for tz in TIME_ZONES:
        timeStr = timeStr.replace(tz, '')

    dt = datetime.strptime(timeStr, '%H%M , %A %d %B %Y')

    return dt


def extractData(html,data_type):
    """
    Extracts the weather data from a BOM weather forecast HTML page.

    Args:
        html: The HTML page to extract data from.
        data_type: A string that indicates the type of data to be extracted.
                   Must be either 'model' or 'forecast'.

    Returns:
        A pandas DataFrame containing the extracted data.
    """
    bs = BeautifulSoup(html, "html.parser")

    data = []

    # get issued time
    issueTime = getIssueTime(bs)

    tablesToSkip = 1
    if '<p><b>Likelihood of exceedance</b></p>' in html:
        tablesToSkip = 2

    # need to parse all tables where the first cell is 'Date'
    for i, tbl in enumerate(bs.findAll("table")):

        # skip the header table
        if i < tablesToSkip:
            continue

        # If the first td has Date at the text, then its a table to parse
        firstCell = tbl.find("td").text.strip()
        if firstCell == 'Date':
            data.append(parseTable(tbl,data_type))

    df = pd.concat(data)
    
    dayAndMonths = df['date'].apply(lambda d: d.split(' ')[1])

    days = dayAndMonths.apply(lambda d: d.split('/')[0]).astype(int)
    months = dayAndMonths.apply(lambda d: d.split('/')[1]).astype(int)

    years = days * 0 + issueTime.year

    # If months is less than issueTime month, then its the next year
    years[months < issueTime.month] = issueTime.year + 1

    df['day'] = days
    df['month'] = months
    df['year'] = years

    # find utc offset from the hour_* field
    utcoffset = None
    for tz in list(TIME_ZONES.keys()):
        col = "hour_{}".format(tz)
        if col in df:
            utcoffset = TIME_ZONES[tz]
            df = df.rename(columns={col: 'hour'})

    df['hour'] = (df['hour'].astype(int) / 100).astype(int)

    df['time_local'] = df.apply(lambda r: datetime(r.year, r.month, r.day, r.hour), axis='columns')

    # apply utc offset
    df['time_utc'] = df['time_local'] - utcoffset

    df = df[df.columns.difference(['day', 'month', 'year', 'hour', 'date'])]

    for col in df.columns:
        if col in ['time_local', 'time_utc', 'seas_pd', 'swell_1_pd', 'swell_2_pd', 'swell_3_pd', 'swell_4_pd']:
            continue
                
        df[col] = pd.to_numeric(df[col])

    return df

def smooth_max(df):
    """
    Apply a Savitzy Golay smoothing function to P5's and max on wind speed and hs

    Parameters
    ----------
    df : pandas DataFrame
        The DataFrame containing the wind and wave data

    Returns
    -------
    pandas DataFrame
        The DataFrame with the smoothed and maxed data
    """
    
    cols = ["wnd_spd", "wnd_spd_95", "total_ht", "total_ht_95"]
    
    if '95' not in df:
        cols = ["wnd_spd", "total_ht"]
        if 'total_ht' not in df:
            cols = ["wnd_spd"]
    elif 'total_ht' not in df:
        cols = ["wnd_spd", "wnd_spd_95"] 
    
    for col in cols:
        s = df[col].values
        if '95' in col:
            filtered = savgol_filter(s,9,2,mode='nearest')
        elif 'air_temp' in col:
            filtered = savgol_filter(s,9,2,mode='nearest')
        else:
            filtered = savgol_filter(s,9,2,mode='nearest')
        df[col] = filtered

    return df

def special_sauce(df,**kwargs):
    """
    Apply a special sauce multiplier

    Parameters
    ----------
    df : pandas DataFrame
        The DataFrame containing the wind and wave data
    **kwargs : dict
        Dictionary containing the parameters to pass on to special sauce calculator if issue = special_sauce 
        (wnd_limit, wnd_multi, hs_limit, hs_multi)

    Returns
    -------
    pandas DataFrame
        The DataFrame with the special sauce multiplier applied
    """
    wnd_limit = 12
    wnd_multi = 1.1
    hs_limit = 1.5
    hs_multi = 1.15
    
    if kwargs:
        wnd_limit = int(kwargs['wnd_limit'])
        wnd_multi = float(kwargs['wnd_multi'])
        hs_limit = float(kwargs['hs_limit'])
        hs_multi = float(kwargs['hs_multi'])
    
    cols = ["wnd_spd", "wnd_spd_95", "total_ht", "total_ht_95"]
    
    if '95' not in df:
        cols = ["wnd_spd", "total_ht"]
        if 'total_ht' not in df:
            cols = ["wnd_spd"]
    elif 'total_ht' not in df:
        cols = ["wnd_spd", "wnd_spd_95"] 
    
    for col in cols:
        s = df[col].values
        if 'air_temp' in col:
            filtered = savgol_filter(s,15,2,mode='nearest')
        else:
        
            if 'wnd_spd' in col:
                s = np.where(s > wnd_limit, s.astype(float)*wnd_multi, s.astype(float))
            else:
                s = np.where(s > hs_limit, s.astype(float)*hs_multi, s.astype(float))
                    
            filtered = savgol_filter(s,5,2,mode='nearest')
        
        df[col] = filtered

    return df

def load(userID, forecastName, archive, data_type='forecast', issue='raw'):
    """
    Load an Ofcast forecast and return a DataFrame with the data

    Parameters
    ----------
    userID : str
        The userID from the Ofcast session
    forecastName : str
        The name of the forecast
    archive : int
        The number of previous issues to get (0 = current)
    data_type : str, optional
        Either 'forecast' data or the 'model' data contained in the form, by default 'forecast'
    issue : str, optional
        Whether to get the raw forecast data, the smoothed data or the special sauce data, by default 'raw'

    Returns
    -------
    pandas DataFrame
        A DataFrame containing the wind and wave data from the forecast
    """
    sessionID,sessionString = getArchiveProductSession(userID, forecastName, archive)

    html = requests.get(TABLE_URL.format(sessionID), timeout=5).content.decode('utf-8')
    view_url = SERVER + "/ofcast/cgi-bin/pct_view.pl?s={}&v=vpdf"
    url = view_url.format(sessionID)
    

    if "System Error" not in html:
        df = extractData(html,data_type)
        
        if 'smoothed' in issue and data_type != 'forecast':
            df = smooth_max(df)
    
    df['url'] = url
    df['issueTime'] = sessionString
         
    return df


def load_archive(userID, server, forecastName, archive, data_type='forecast', issue='raw', **kwargs):
    """
    Load an archived ofcast forecast

    Parameters
    ----------
    userID : str
        The userID from the Ofcast session
    forecastName : str
        The name of the forecast
    archive : int
        The number of previous issues to get (0 = current)
    data_type : str, optional
        Either 'forecast' data or the 'model' data contained in the form, by default 'forecast'
    issue : str, optional
        Whether to get the raw forecast data, the smoothed data or the special sauce data, by default 'raw'
    **kwargs : dict
        Dictionary containing the parameters to pass on to special sauce calculator if issue = special_sauce 
        (wnd_limit, wnd_multi, hs_limit, hs_multi)

    Returns
    -------
    pandas DataFrame
        A DataFrame containing the wind and wave data from the forecast
    """
    SERVER, TABLE_URL = changeServer(server)
    
    try:
        sessionID,sessionString = getArchiveProductSession(userID, forecastName, archive)
        html = requests.get(TABLE_URL.format(sessionID), timeout=5).content.decode('utf-8')
        view_url = SERVER + "/ofcast/cgi-bin/pct_view.pl?s={}&v=vpdf"
        url = view_url.format(sessionID)
    
    except:
        print('Session ID timed out ?')
        return {'wnd_spd':'no session id', 'total_ht': 'no session id'}
    
    if "System Error" not in html:
        df = extractData(html,data_type)
        
        if 'smoothed' in issue and data_type != 'forecast':
            df = smooth_max(df)
        elif 'special' in issue and data_type != 'forecast':
            df = special_sauce(df,**kwargs)
        
    df['url'] = url
    df['issueTime'] = sessionString
    df['time'] = df['time_utc'] 
         
    return df

def get_url_issueTime(sessionID, sessionString):
    """
    Get the URL and issue time for an archived Ofcast forecast

    Parameters
    ----------
    sessionID : str
        The session ID for the forecast
    sessionString : str
        The session string for the forecast

    Returns
    -------
    str
        The URL for the forecast
    str
        The issue time for the forecast
    """
    view_url = SERVER + "/ofcast/cgi-bin/pct_view.pl?s={}&v=vpdf"
    url = view_url.format(sessionID)
    issue = sessionString
    
    return issue

def load_view(userID, forecastName, archive, view):
    """
    Load the html and filename of an archived Ofcast forecast

    Parameters
    ----------
    userID : str
        The userID from the Ofcast session
    forecastName : str
        The name of the forecast
    archive : int
        The number of previous issues to get (0 = current)
    view : str
        The view to load ('pdf', 'xml', or 'html')

    Returns
    -------
    dict
        A dictionary containing the URL and issue time for the forecast
    """
    view = view.lower()
    sessionID,sessionString = getArchiveProductSession(userID, forecastName, archive)
    view_url = SERVER + "/ofcast/cgi-bin/pct_view.pl?s={}&v=v{}"

    #html = requests.get(view_url.format(sessionID), timeout=5).content.decode('utf-8')
    html = None
    
    issue = {'url':view_url.format(sessionID,view),'issueTime':sessionString}
    
    return issue

def get_title(userID, forecastName, archive):
    """

    Return
    ------
        The tile of the Ofcast forecast
    """
    
    sessionID = getArchiveProductSession(userID, forecastName, archive)[0]
    view_url = SERVER + "/ofcast/cgi-bin/pct_view.pl?s={}&v=vhtml&vc=2"

    html = requests.get(view_url.format(sessionID), timeout=5).content.decode('utf-8')

    soup = BeautifulSoup(html, 'html.parser')
    title = soup(text=re.compile('Prepared for'))
    
    return title[0][13:]

if __name__ == '__main__':

    userID = 'davink64875'
    label = 'Woodside - Pluto 10 days'
    archive = 0
    data_type = 'model'
    DEBUG = False
    #print(getArchiveProductSession(userID,label,archive))
    df = load_archive(userID, label, archive, data_type)
    print('-------------------------\n{}\n-------------------------'.format(data_type))
    print(df)
    print(df.time_utc)
    print(df.columns)
    #print(load_view(userID,label,archive,'pdf'))
    #print(getProductsPrevious(userID,label))
