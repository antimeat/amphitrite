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
import xarray as xr
import pandas as pd
import numpy as np
import glob
import os
import time
import warnings
import datetime

warnings.filterwarnings("ignore", category=RuntimeWarning)

# os.environ[ 'NUMBA_CACHE_DIR' ] = '/tmp/numba_cache'
# os.environ[ 'NUMBA_DISABLE_JIT' ] = '1'

class Partitions(object):   
    """Class of methods for bespoke swell partitions and transformations"""

    def __init__(self):
        self.dir = "/cws/data/wavewatch/"
        self.filename = self.get_latest_file_new()
        self.set_latest_run_time(self.filename)
            
    def get_latest_run_time(self):
        return self.latest_run_time
    
    def set_latest_run_time(self,filename):
        date_string = filename.split("/")[-1].split("_")[2].split(".")[0]
        print(date_string)
        self.latest_run_time = datetime.datetime.strptime(date_string,"%Y%m%d%H")
    
    def generate_table_names(self):
        """Generate a file of all the table names in the netcdf file"""
        netcdf_name = self.filename
        output_file = "./nc_table_names.txt"
        table_names = self.table_names_from_netcdf(netcdf_name)
        
        with open(output_file, "w") as file:
            for table in table_names:
                file.write(table + "\n")
        
        return table_names
        
    def table_names_from_netcdf(self,file_name):
        """Return all the table names from the netcdf file"""
        ds = xr.open_dataset(file_name)
        table_names = []
        
        #loop through each site
        for site_num in ds.station.values:
            site = ds.sel(station=site_num)[["station_name","latitude","longitude"]]
            site_name = ''.join(site.station_name.values.astype(str))            
            lat = np.round(float(site.latitude.values[0]),4)
            lon = np.round(float(site.longitude.values[0]),4)

            #format the output for name and lat,lon
            table_names.append(f"{site_name}, {lat:.4f}, {lon:.4f}")

        return table_names
    
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
        #at least stage we are only using the larger runs: 12Z/00Z
        latest = fresh_files[0]
        last = fresh_files[1]
        latest_size = os.stat(latest).st_size 
        previous_size = os.stat(last).st_size      
        
        if latest_size < previous_size:
            latest = last
        
        return latest

    def get_latest_file_new(self):
        """
        Return the path to the most relevant wavewatch file by selecting the two most recent files.

        Returns:
        str: The file path to the most relevant wavewatch NetCDF file.
        """
        extn = '/cws/data/wavewatch/IDY35050_G3_??????????.nc'
        files = glob.glob(extn)

        # Filter out files older than max_hours and sort by modification time
        max_hours = 48
        fresh_files = [file for file in files if (time.time() - os.path.getmtime(file)) / 3600 < max_hours]
        fresh_files.sort(key=os.path.getmtime, reverse=True)

        if len(fresh_files) < 2:
            print('No fresh input files!')
            exit(1)

        # Pass the two most recent files to create_combined_file for further processing
        return self.create_combined_file(fresh_files[0], fresh_files[1])

    def create_combined_file(self, latest_file, previous_file):
        """
        Create a new file combining data from the latest and previous files if necessary.
        """
        latest_file_string = latest_file.split("/")[-1]
        previous_file_string = previous_file.split("/")[-1]
        new_file_path = f"/tmp/wavewatch/{latest_file_string}"

        try:
            # Ensure the /tmp/wavewatch directory exists
            os.makedirs(os.path.dirname(new_file_path), exist_ok=True)
            
            # Delete existing files in the directory
            existing_files = glob.glob(f"/tmp/wavewatch/*")
            for file in existing_files:
                os.remove(file)

            latest_size = os.stat(latest_file).st_size 
            previous_size = os.stat(previous_file).st_size

            if latest_size < previous_size:
                # Open the datasets for concatenation
                with xr.open_dataset(latest_file, chunks={}) as latest_ds, xr.open_dataset(previous_file, chunks={}) as previous_ds:
                    max_time_latest = latest_ds.time.max()
                    additional_data = previous_ds.sel(time=previous_ds.time > max_time_latest)
                    combined_ds = xr.concat([latest_ds, additional_data], dim='time')

                    # Assign attributes and variables from the previous dataset
                    combined_ds.attrs['stop_date'] = previous_ds.attrs['stop_date']
                    combined_ds['station'] = previous_ds['station']
                    combined_ds['string16'] = previous_ds['string16']
                    combined_ds['station_name'] = previous_ds['station_name']
                    
                    # Write the combined dataset to a new file
                    combined_ds.to_netcdf(new_file_path)
                    
                    # Set proper file permissions
                    os.chmod(new_file_path, 0o666)  # Make it writable by others (rw-rw-rw-)

                return new_file_path
            else:
                # Use the latest file if it is larger or equal in size
                return latest_file
        
        except Exception as e:
            print(f"Problem combining model runs from files: {latest_file_string} and {previous_file_string}: {str(e)}")
        
    def single_part(self, site, *parts):
        """Split the spectrum across a single partion
        
        Paramaters:
            parts (list(tuple)): single tuple has the start and end of the partition range
        Returns:
            ws (xarray): wave spectra output with extra parameters appended            
        """
        
        filename = self.filename
        
        #get the full spectrum data
        ws = readSpectrum.noPartition(filename,site)

        #append data variables back in
        #loop through intermediate swell partitions        
        i = 1
        part = readSpectrum.rangePartition(filename, parts[i-1][0], site, parts[i-1][1])

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

    def multi_parts(self, site, *parts):
        """Split the spectrum across multiple partions
        
        Paramaters:
            parts (list(tuples)): each tuple has the start and end of each partition range
        Returns:
            ws (xarray): wave spectra output with extra parameters appended            
        """
        
        filename = self.filename
        
        #get the full spectrum data
        ws = readSpectrum.noPartition(filename,site)
        
        #append data variables back in
        #loop through intermediate swell partitions        
        for i in range(1,len(parts)+1):
            part = readSpectrum.rangePartition(filename, site, parts[i-1][0], parts[i-1][1])
        
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
    
    def multi_parts_sw(self, site, *parts):
        """Split the spectrum across multiple partions
        
        Paramaters:
            parts (list(tuples)): each tuple has the start and end of each partition range
        Returns:
            ws (xarray): wave spectra output with extra parameters appended            
        """
         
        filename = self.filename
        
        #get the full spectrum data
        ws = readSpectrum.noPartition(filename,site)

        #append data variables back in
        #go through and first partition (seas)
        part = readSpectrum.onePartition(filename, site, parts[0][1])
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
            part = readSpectrum.rangePartition(filename, site, parts[i][0], parts[i][1])
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
        part = readSpectrum.onePartition(filename, site, parts[-1][0])
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
    
    def mermaidSound(self,site="Woodside - Mermaid Sound 7 days"):
        """Mermaid sound specific partitions"""
        
        #pass an list of tuples for each period range in the required splits
        #avoid divide by zero on the first
        parts = [(0.1,7),(7,13),(13,18),(16.5,40)]
        
        ws = self.multi_parts_test(site,*parts)
        return ws   
    
if __name__ == "__main__":
    parts = Partitions()
    print(parts.get_latest_run_time())
    table_names = parts.generate_table_names()
    print(table_names)