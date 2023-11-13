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
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)

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
        ws['swell_{}_dpm'.format(i)] = part.dpm
        ws['swell_{}_dpm'.format(i)].attrs['standard_name'] = ws['swell_{}_dpm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
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
            ws['swell_{}_dpm'.format(i)] = part.dpm
            ws['swell_{}_dpm'.format(i)].attrs['standard_name'] = ws['swell_{}_dpm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
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
        ws['swell_{}_dpm'.format(i)] = part.dpm_sea
        ws['swell_{}_dpm'.format(i)].attrs['standard_name'] = ws['swell_{}_dpm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
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
            ws['swell_{}_dpm'.format(i)] = part.dpm
            ws['swell_{}_dpm'.format(i)].attrs['standard_name'] = ws['swell_{}_dpm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
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
        ws['swell_{}_dpm'.format(i)] = part.dpm_sw
        ws['swell_{}_dpm'.format(i)].attrs['standard_name'] = ws['swell_{}_dpm'.format(i)].attrs['standard_name']+'_P{}_partition'.format(i)
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