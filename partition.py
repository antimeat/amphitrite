#!/cws/anaconda/envs/mlenv/bin/python -W ignore

"""
Name:
    partition.py

Classes:
    Partitions(fileName)

Functions:
    single_part(*parts)
    multi_parts(*parts)
    mermaidSound()
"""
import readSpectrum
import pandas as pd
import glob, os
import time

class Partitions(object):   
    """Class of methods for bespoke swell partitions and transformations"""

    def __init__(self):
        self.dir = "/cws/data/wavewatch/"
        self.filename = self.get_latest_file()
        
    def get_latest_file(self):
        """Return current wavewatch file"""
        extn = '/cws/data/wavewatch/IDY35050_G3_??????????.nc'
        files = glob.glob(extn)
        fresh_files = []

        #dont include files older than max_hours!
        max_hours = 48*1
        for file in files:
            mtime = os.path.getmtime(file)
            time_mod = (time.time() - mtime) / 3600
            if time_mod < max_hours:
                fresh_files.append(file)

        if not fresh_files:
            print('No fresh input files!')
            exit(1)

        fresh_files = sorted(fresh_files,reverse=True)
        
        #compare size of last 2 files to determine weather its a 12/00Z run (which are larger) 
        latest = fresh_files[0]
        last = fresh_files[1]
        latest_size = os.stat(latest).st_size 
        previous_size = os.stat(last).st_size      
        
        if latest_size < previous_size:
            latest = last
        
        return latest

    def single_part(self,*parts):
        """Split the spectrum across a single partion
        
        Paramaters:
            parts (list(tuple)): single tuple has the start and end of the partition range
        Returns:
            ws (xarray): wave spectra output with extra parameters appended            
        """
        
        filename = self.filename
        
        #get the full spectrum data
        ws = readSpectrum.noPartition(filename)

        #append data variables back in
        #loop through intermediate swell partitions        
        i = 1
        part = readSpectrum.rangePartition(filename, parts[i-1][0], parts[i-1][1])

        ws['swell_{}_hs'.format(i)] = part.hs
        ws['swell_{}_hs'.format(i)].attrs['standard_name'] = ws['swell_{}_hs'.format(i)].attrs['standard_name'] +'_P{}_partition'.format(i)
        ws['swell_{}_hmax'.format(i)] = part.hmax
        ws['swell_{}_hmax'.format(i)].attrs['standard_name'] = ws['swell_{}_hmax'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tp'.format(i)] = part.tp
        ws['swell_{}_tp'.format(i)].attrs['standard_name'] = ws['swell_{}_tp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tm01'.format(i)] = part.tm01
        ws['swell_{}_tm01'.format(i)].attrs['standard_name'] = ws['swell_{}_tm01'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tm02'.format(i)] = part.tm02
        ws['swell_{}_tm02'.format(i)].attrs['standard_name'] = ws['swell_{}_tm02'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dp'.format(i)] = part.dp
        ws['swell_{}_dp'.format(i)].attrs['standard_name'] = ws['swell_{}_dp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dm'.format(i)] = part.dm
        ws['swell_{}_dm'.format(i)].attrs['standard_name'] = ws['swell_{}_dm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dspr'.format(i)] = part.dspr
        ws['swell_{}_dspr'.format(i)].attrs['standard_name'] = ws['swell_{}_dspr'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        
        return ws

    def multi_parts(self,*parts):
        """Split the spectrum across multiple partions
        
        Paramaters:
            parts (list(tuples)): each tuple has the start and end of each partition range
        Returns:
            ws (xarray): wave spectra output with extra parameters appended            
        """
        
        filename = self.filename
        
        #get the full spectrum data
        ws = readSpectrum.noPartition(filename)
        
        #append data variables back in
        #loop through intermediate swell partitions        
        for i in range(1,len(parts)+1):
            part = readSpectrum.rangePartition(filename, parts[i-1][0], parts[i-1][1])
            print(part)
        
            ws['swell_{}_hs'.format(i)] = part.hs
            ws['swell_{}_hs'.format(i)].attrs['standard_name'] = ws['swell_{}_hs'.format(i)].attrs['standard_name'] +'_P{}_partition'.format(i)
            ws['swell_{}_hmax'.format(i)] = part.hmax
            ws['swell_{}_hmax'.format(i)].attrs['standard_name'] = ws['swell_{}_hmax'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_tp'.format(i)] = part.tp
            ws['swell_{}_tp'.format(i)].attrs['standard_name'] = ws['swell_{}_tp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_tm01'.format(i)] = part.tm01
            ws['swell_{}_tm01'.format(i)].attrs['standard_name'] = ws['swell_{}_tm01'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_tm02'.format(i)] = part.tm02
            ws['swell_{}_tm02'.format(i)].attrs['standard_name'] = ws['swell_{}_tm02'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_dp'.format(i)] = part.dp
            ws['swell_{}_dp'.format(i)].attrs['standard_name'] = ws['swell_{}_dp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_dm'.format(i)] = part.dm
            ws['swell_{}_dm'.format(i)].attrs['standard_name'] = ws['swell_{}_dm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_dspr'.format(i)] = part.dspr
            ws['swell_{}_dspr'.format(i)].attrs['standard_name'] = ws['swell_{}_dspr'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        
        return ws
    
    def multi_parts_sw(self,*parts):
        """Split the spectrum across multiple partions
        
        Paramaters:
            parts (list(tuples)): each tuple has the start and end of each partition range
        Returns:
            ws (xarray): wave spectra output with extra parameters appended            
        """
         
        filename = self.filename
        
        #get the full spectrum data
        ws = readSpectrum.noPartition(filename)

        #append data variables back in
        #go through and first partition (seas)
        part = readSpectrum.onePartition(filename, parts[0][1])
        i = 0
        ws['swell_{}_hs'.format(i)] = part.hs_sea
        ws['swell_{}_hs'.format(i)].attrs['standard_name'] = ws['swell_{}_hs'.format(i)].attrs['standard_name'] +'_P{}_partition'.format(i)
        ws['swell_{}_hmax'.format(i)] = part.hmax_sea
        ws['swell_{}_hmax'.format(i)].attrs['standard_name'] = ws['swell_{}_hmax'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tp'.format(i)] = part.tp_sea
        ws['swell_{}_tp'.format(i)].attrs['standard_name'] = ws['swell_{}_tp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tm01'.format(i)] = part.tm01_sea
        ws['swell_{}_tm01'.format(i)].attrs['standard_name'] = ws['swell_{}_tm01'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tm02'.format(i)] = part.tm02_sea
        ws['swell_{}_tm02'.format(i)].attrs['standard_name'] = ws['swell_{}_tm02'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dp'.format(i)] = part.dp_sea
        ws['swell_{}_dp'.format(i)].attrs['standard_name'] = ws['swell_{}_dp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dm'.format(i)] = part.dm_sea
        ws['swell_{}_dm'.format(i)].attrs['standard_name'] = ws['swell_{}_dm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dspr'.format(i)] = part.dspr_sea
        ws['swell_{}_dspr'.format(i)].attrs['standard_name'] = ws['swell_{}_dspr'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        
        #loop through intermediate swell partitions        
        for i in range(1,len(parts)-1):
            part = readSpectrum.rangePartition(filename, parts[i][0], parts[i][1])
            ws['swell_{}_hs'.format(i)] = part.hs
            ws['swell_{}_hs'.format(i)].attrs['standard_name'] = ws['swell_{}_hs'.format(i)].attrs['standard_name'] +'_P{}_partition'.format(i)
            ws['swell_{}_hmax'.format(i)] = part.hmax
            ws['swell_{}_hmax'.format(i)].attrs['standard_name'] = ws['swell_{}_hmax'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_tp'.format(i)] = part.tp
            ws['swell_{}_tp'.format(i)].attrs['standard_name'] = ws['swell_{}_tp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_tm01'.format(i)] = part.tm01
            ws['swell_{}_tm01'.format(i)].attrs['standard_name'] = ws['swell_{}_tm01'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_tm02'.format(i)] = part.tm02
            ws['swell_{}_tm02'.format(i)].attrs['standard_name'] = ws['swell_{}_tm02'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_dp'.format(i)] = part.dp
            ws['swell_{}_dp'.format(i)].attrs['standard_name'] = ws['swell_{}_dp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_dm'.format(i)] = part.dm
            ws['swell_{}_dm'.format(i)].attrs['standard_name'] = ws['swell_{}_dm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
            ws['swell_{}_dspr'.format(i)] = part.dspr
            ws['swell_{}_dspr'.format(i)].attrs['standard_name'] = ws['swell_{}_dspr'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        
        #go through the last swell partition
        part = readSpectrum.onePartition(filename, parts[-1][0])
        i = len(parts) - 1
        ws['swell_{}_hs'.format(i)] = part.hs_sw
        ws['swell_{}_hs'.format(i)].attrs['standard_name'] = ws['swell_{}_hs'.format(i)].attrs['standard_name'] +'_P{}_partition'.format(i)
        ws['swell_{}_hmax'.format(i)] = part.hmax_sw
        ws['swell_{}_hmax'.format(i)].attrs['standard_name'] = ws['swell_{}_hmax'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tp'.format(i)] = part.tp_sw
        ws['swell_{}_tp'.format(i)].attrs['standard_name'] = ws['swell_{}_tp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tm01'.format(i)] = part.tm01_sw
        ws['swell_{}_tm01'.format(i)].attrs['standard_name'] = ws['swell_{}_tm01'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_tm02'.format(i)] = part.tm02_sw
        ws['swell_{}_tm02'.format(i)].attrs['standard_name'] = ws['swell_{}_tm02'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dp'.format(i)] = part.dp_sw
        ws['swell_{}_dp'.format(i)].attrs['standard_name'] = ws['swell_{}_dp'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dm'.format(i)] = part.dm_sw
        ws['swell_{}_dm'.format(i)].attrs['standard_name'] = ws['swell_{}_dm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        ws['swell_{}_dspr'.format(i)] = part.dspr_sw
        ws['swell_{}_dspr'.format(i)].attrs['standard_name'] = ws['swell_{}_dspr'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
        
        return ws
    
    def mermaidSound(self):
        """Mermaid sound specific partitions"""
        
        #pass an list of tuples for each period range in the required splits
        #avoid divide by zero on the first
        parts = [(0.0001,7),(7,13),(13,18),(16.5,40)]
        
        ws = self.multi_parts_test(*parts)
        return ws
    
    def to_df(self,ws):
        """Convert the wavespectra xarray to a usable dataFrame for merging into ofcast
        
        Parameters:
            ws (xarray): wave spectra
        Returns:
            df (DataFrame): modified dataframe with parametes and columns fit for purpose        
        """
        
        variables = list(ws.keys())
        variables.remove("efth")
        df = ws[variables].to_dataframe()
        
        #find how many swell partitions we have and add them to a reduced column list
        all_swell_nums = ['{}_{}'.format(n.split('_')[0],n.split('_')[1]) for n in df.columns if "swell" in n]
        unique_swell_nums = list(dict.fromkeys(all_swell_nums))

        #clean up index
        df.reset_index(inplace=True)        
                     
        #clean up some column names to match Ofcast expectations
        #df["station_name"] = df["station_name"].apply(lambda x: x.decode('utf-8'))
        df.rename(columns={"wdir":"wnd_dir","wspd":"wnd_spd","hs":"total_ht","time":"time_utc"},inplace=True)
        for n in unique_swell_nums:
            df.rename(columns={"{}_hs".format(n):"{}_ht".format(n),"{}_tm01".format(n):"{}_pd".format(n),"{}_dm".format(n):"{}_dirn".format(n)},inplace=True)
        
        #df.set_index("time_utc",inplace=True)
        #df["time_utc"] = df.index
        index = pd.DatetimeIndex(df["time_utc"].values,tz="utc")
        df.set_index(index,inplace=True)
        df["time_local"] = index.to_pydatetime()
        
        #reduced column list
        cols = ["total_ht","wnd_dir","wnd_spd"]
        for n in unique_swell_nums:
            cols.extend(["{}_ht".format(n),"{}_pd".format(n),"{}_dirn".format(n)])
            
        cols.extend(["station_name","time_local"])
        
        #round stuff
        df = df.apply(lambda x: x.round().astype(int) if "dir" in x.name else x)
        df = df.apply(lambda x: x.round(2) if "ht" in x.name else x)
        #df = df.apply(lambda x: x.round().astype(int) if "pd" in x.name else x)       
        df = df.apply(lambda x: x.round() if "pd" in x.name else x)       
        
        return df[cols]
    
    def get_sites_list(self,ws):
        """Return unique site names from the spectra
        Parameters:
            ws (xarray): wave spectra file
        Returns:
            sites (list): site names listed contained in model data
        """
        
        df = self.to_df(ws)
        sites = df["station_name"].unique()
        
        return sites
    
    def get_site(self,ws,siteName):
        """Return unique site names from the spectra
        Parameters:
            ws (xarray): wave spectra file
            siteName (string): site name that matches a listed site
        Returns:
            df_site (DataFrame): dataframe from the wave spectra of the selected site 
        """
        
        df = self.to_df(ws)
        df_site = df[df["station_name"] == siteName]
        
        return df_site
    

    