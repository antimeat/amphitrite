#!/cws/anaconda/envs/mlenv/bin/python -W ignore

######################################################################
#   1D spectral plotting
#   By: Daz Vink
#   Date: 05/07/2024
######################################################################

import glob
import os
import wavespectra
import datetime
import time
import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import argparse
import amphitrite_configs as configs
import urllib.request
import json

# Set the Numba cache directory
numba_cache_dir = '/tmp/numba_cache'
os.environ['NUMBA_CACHE_DIR'] = numba_cache_dir
os.environ[ 'NUMBA_DISABLE_JIT' ] = '1'

# Set the umask to 0 to ensure that no permissions are masked
os.umask(0)

BASE_DIR = configs.BASE_DIR
BASE_URL = configs.BASE_URL

# Base URL for the iframe and image sources
BASE_URL_GHPLOTS = "http://wa-vw-er.bom.gov.au/webapps/vwave/plots/"
BASE_URL_IMAGES = "http://wa-vw-er.bom.gov.au/webapps/vwave/plotsSpec/"
BASE_URL_TABLES = BASE_URL + "/transformer/tables/"  

OUTPUT_DIR = os.path.join(BASE_DIR, "plots/spectral/")
TABLES = {}

class WavespectraHighRes(object):
    def __init__(self,ws=None):
        self.ws = ws
        self.dir = "/cws/data/wavewatch/"
        self.filename = self.get_latest_file_new()
        self.latest_run_time = self.set_latest_run_time(self.filename)
        self.cache_filename = "cached_runtime.txt"
                
    def get_site_spectra(self,site):
        """if we dont already have a wavespectra object, create one"""
        self.ws = self.interpolate_wavespectra(site)
        return self.ws
            
    def get_latest_run_time(self):
        return self.latest_run_time

    def set_latest_run_time(self,filename):
        date_string = filename.split("/")[-1].split("_")[2].split(".")[0]
        print(date_string)
        latest_run_time = datetime.datetime.strptime(date_string,"%Y%m%d%H")
        return latest_run_time

    def check_runtime_cache(self,latest_runtime):
        """check cached run info"""
        with open(self.cache_filename) as f:
            old_runtime = f.read()
        if old_runtime == latest_runtime:
            return True
        return False

    def update_runtime_cache(self,latest_runtime):
        """check cached run info"""
        with open(self.cache_filename) as f:
            f.write(latest_runtime)
        
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

    def clip(self, ds, boundary = {'min_lon':110.88, 'min_lat':-25.68, 'max_lon':121.47,'max_lat':-16.38}):
        """clip dataset my lats and lons"""
        ds = ds.copy()
        
        mask_lon = (ds.longitude >= boundary['min_lon']) & (ds.longitude <= boundary['max_lon'])
        mask_lat = (ds.latitude >= boundary['min_lat']) & (ds.latitude <= boundary['max_lat'])
        cropped_ds = ds.where(mask_lon, drop=True)
        cropped_ds = ds.where(mask_lat, drop=True)
        
        return cropped_ds

    def interpolate_wavespectra(self, site):
        """Changes the 'dir' variable name as it clashes with model internal names
        and interpolates both direction and frequency to a finer resolution.
        """
        try:
            ds = xr.open_dataset(self.filename)
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

def load_tables():
    """
    Load tables from the API
    """
    global TABLES  
    url = BASE_URL + "/api.cgi?get=list_json"  
    response = urllib.request.urlopen(url)
    data = response.read().decode("utf-8")
    TABLES = json.loads(data)

def spec_plot(latest_runtime, oned,site_name,partitions=None):
    """
    plot the 1D spectrum for a site
    """
    file_name = site_name.lower().replace(' ', '_').replace('-', '') + ".png"
    try:
        fig, ax = plt.subplots(figsize=(15, 5))
        oned.T.plot(ax=ax, cmap=plt.cm.turbo, robust=True)
        ax.set_ylabel('Period (s)')
        
        # If we have partitions, plot them as red dashed lines with labels
        if partitions is not None:
            for part in partitions:
                line = float(part[0])
                if line < 1:
                    continue
                ax.axhline(y=line, color='red', linestyle='--')
                
                # Add the label along the y-axis on the right side
                x_position = ax.get_xlim()[1] + 0.1  # Slightly to the right of the plot
                ax.text(x=x_position, y=line, s=f'{str(line)}s', color='red', va='center', ha='left', fontsize=10, backgroundcolor='white')    
                
        plt.title(f"Site: {site_name}\n Model run: {latest_runtime}")
        plt.savefig(os.path.join(OUTPUT_DIR, f"{file_name}"), bbox_inches = "tight")
        plt.close(fig)
        print(f"Saved spectral output to: {file_name}")
    except Exception as e:
        print(f"Error plotting: {e}")
    
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--site",dest="site_name",nargs="?", default="all",help="the forecast site name from Ofcast",required=False)
    args = parser.parse_args()
    
    ws_hires = WavespectraHighRes()
    latest_runtime = f"{ws_hires.get_latest_run_time().strftime('%Y-%m-%d %HZ')}"
    load_tables()
        
    if args.site_name == "all":
        for site_name in TABLES:
            table_name = TABLES[site_name]['table']
            partitions = TABLES[site_name]['parts']
            site_ws = ws_hires.get_site_spectra(table_name)
            site_ws['freq'] = 1/site_ws.freq
            oned = site_ws.spec.oned()
            spec_plot(latest_runtime, oned, site_name,partitions)
    else:
        site_name = args.site_name
        table_name = TABLES[site_name]['table']
        partitions = TABLES[site_name]['parts']
        site_ws = ws_hires.get_site_spectra(table_name)
        site_ws['freq'] = 1/site_ws.freq
        print(site_ws)
        exit()
        oned = site_ws.spec.oned()
        spec_plot(latest_runtime, oned, site_name, partitions)
        
if __name__ == "__main__":
    main()    
    