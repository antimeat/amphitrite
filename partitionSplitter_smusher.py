#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    partitionSplitter.py

Classes:
    PartitionSplitter(origin,destination)

Functions:    
"""
import os
os.environ[ 'NUMBA_CACHE_DIR' ] = '/tmp/numba_cache'
os.environ[ 'NUMBA_DISABLE_JIT' ] = '1'

# os.environ[ 'CONDA_DEFAULT_ENV' ] = 'mlenv'

# import swellSmusher
import partition
import pandas as pd
from io import StringIO
from tabulate import tabulate
import argparse
import logging
import smusher
import autoseas.auto_seas as auto_seas
import gfe

#package imports
import database as db
import models

BASE_DIR = "/cws/op/webapps/er_ml_projects/davink/amphitrite"

# Configure logging
LOG_FILENAME = os.path.join(BASE_DIR,"logfile.log")

# Configure logging
try:
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)
    logging.basicConfig(
        filename=LOG_FILENAME, 
        level=logging.INFO,
        format='%(asctime)s:%(levelname)s:%(message)s'
    )
    logging.info("Logging initialized successfully.")
except Exception as e:
    print(f"Logging setup failed: {e}")

class PartitionSplitter(object):   
    """Class of methods to breed a mongrel mix of wave spectra, transformations and Ofcast forecasts"""

    def __init__(self):
        self.partition = partition.Partitions()
        self.config_file = os.path.join(BASE_DIR,"site_config.txt")
        self.site_tables = self.load_config_file(self.config_file)
        self.latest_run_time = self.partition.get_latest_run_time()
        
    def transform_site_name(self,site_name):
        """Reformat the site name to api friendly"""
        site_name = site_name.replace(" - ","_-_").replace(" ","_")
        return site_name
    
    def get_site_config(self,site_name):
        """Get the table config related to the siteName
        Paramaters:
            site_name: ofcast site name
        Returns:
            the auswave table name and partition splits related to the site
        """
        print(self.site_tables)
        return self.site_tables[site_name]

    def get_site_config_db(self,site_name):
        """Get the table config related to the site_name from the database"""
        session = db.get_session()
        try:
            site = session.query(models.Site).filter(models.Site.site_name == site_name).first()
            if site:
                return {"success": True, "message": f"'{site_name} data found", "data": site.to_json()}
            else:
                return {"success": False, "message": f"Site with name '{site_name}' not found"}
        except Exception as e:
            return {"success": False, "message": str(e)}
        finally:
            session.close()
        
        
    def load_config_file(self,config_file):
        """
        Get the table name and partition ranges related to the siteName
        Parameters:
            siteName: ofcast site name
        Returns:
            a dictionary with the table name and partition ranges
        """
        site_tables = {}
        with open(config_file, 'r') as file:
            for line in file:
                # Skip comment lines
                if line.startswith('#'):
                    continue

                parts = line.strip().split(', ')
                if len(parts) < 3:
                    continue  # Skip malformed lines

                site = parts[0]
                table = parts[1]
                # Parse all split ranges
                split_ranges = [tuple(map(float, part.split('-'))) for part in parts[2:]]

                site_tables[site] = {"table": table, "parts": split_ranges}

        
        return site_tables
       
    def to_ofcast_df(self,ws):
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
        #df["location"] = df["location"].apply(lambda x: x.decode('utf-8'))
        df.rename(columns={"wdir":"wind_dir","wspd":"wind_spd","hs":"total_ht","time":"time_utc"},inplace=True)
        for n in unique_swell_nums:
            df.rename(columns={"{}_hs".format(n):"{}_ht".format(n),"{}_tm01".format(n):"{}_pd".format(n),"{}_dm".format(n):"{}_dirn".format(n)},inplace=True)
        
        #df.set_index("time_utc",inplace=True)
        #df["time_utc"] = df.index
        index = pd.DatetimeIndex(df["time_utc"].values,tz="utc")
        df.set_index(index,inplace=True)
        df["time_local"] = index.to_pydatetime()
        
        #reduced column list
        cols = ["total_ht","wind_dir","wind_spd"]
        for n in unique_swell_nums:
            cols.extend(["{}_ht".format(n),"{}_pd".format(n),"{}_dirn".format(n)])
            
        cols.extend(["location","time_local"])
        
        #round stuff
        df = df.apply(lambda x: x.round().astype(int) if "dir" in x.name else x)
        df = df.apply(lambda x: x.round(2) if "ht" in x.name else x)
        #df = df.apply(lambda x: x.round().astype(int) if "pd" in x.name else x)       
        df = df.apply(lambda x: x.round(1) if "pd" in x.name else x)       
        
        return df[cols]
    
    def get_sites_list(self,ws):
        """Return unique site names from the spectra
        Parameters:
            ws (xarray): wave spectra file
        Returns:
            sites (list): site names listed contained in model data
        """
        
        df = self.to_ofcast_df(ws)
        sites = df["location"].unique()
        
        return sites
    
    def get_ofcast_site(self,ws,siteName):
        """Return unique site names from the spectra
        Parameters:
            ws (xarray): wave spectra file
            siteName (string): site name that matches a listed site
        Returns:
            df_site (DataFrame): dataframe from the wave spectra of the selected site 
        """
        
        df = self.to_ofcast_df(ws)
        df_site = df[df["location"] == siteName]
        
        return df_site 

    def to_api_df(self, ws):
        """
        Convert the wavespectra xarray to a DataFrame for an ofcast api.
        
        Parameters:
            ws (xarray.Dataset): wave spectra.
            
        Returns:
            df (pandas.DataFrame): Modified dataframe with parameters and columns fit for purpose.
        """
        
        variables = list(ws.keys())
        variables.remove("efth")
        df = ws[variables].to_dataframe()
        
        #find how many swell partitions we have and add them to a reduced column list
        all_swell_nums = ['{}'.format(n.split('_')[1]) for n in df.columns if "swell" in n]
        unique_swell_nums = list(dict.fromkeys(all_swell_nums))

        #clean up index
        df.reset_index(inplace=True)        

        # Set index to UTC time and add local time column
        df.set_index(pd.DatetimeIndex(df["time"], tz='utc'), inplace=True)
        df["run_time"] =  df.index[0].tz_localize(None)   
        df["time_local"] = df.index.tz_convert('Australia/Perth').tz_localize(None)
        
        # Group by 'location' and use cumcount to count each group
        df['fcst_hrs'] = df.groupby('station_name').cumcount()
        df['fcst_hrs'] = df['fcst_hrs'].astype(str).str.zfill(3)
        
        col_mapping = {
            "run_time": "run_time",
            "station_name": "location",
            "fcst_hrs": "time[hrs]",
            "time": "time[UTC]",
            "time_local": "time[WST]",
            "wdir": "wind_dir[degrees]",
            "wspd": "wind_spd[kn]",
            "hs": "seasw_ht[m]",
            "dp": "seasw_dir[degree]",
            "tp": "seasw_pd[s]",            
        }

        # Dynamically generate swell column mappings based on the swells present
        dir_type = 'dp'
        swell_prefix_mapping = {}
        for i,n in enumerate(unique_swell_nums):
            if f"swell_{n}_hs" in df.columns:  # Check if the swell column actually exists
                if i == 0:
                    swell_prefix_mapping.update({
                        f"swell_1_hs": "sea_ht[m]",
                        f"swell_1_{dir_type}": "sea_dir[degree]",
                        f"swell_1_tp": "sea_pd[s]",
                    })
                else:
                    new_prefix = f'sw{i}_'
                    swell_prefix_mapping.update({
                        f"swell_{i+1}_hs": f"{new_prefix}ht[m]",
                        f"swell_{i+1}_{dir_type}": f"{new_prefix}dir[degree]",
                        f"swell_{i+1}_tp": f"{new_prefix}pd[s]",
                    })

        # Rename columns according to mappings and use values for out cols
        col_mapping.update(swell_prefix_mapping)
        df.rename(columns=col_mapping, inplace=True)
        
        # Rounding logic applied to columns based on their dtype
        df = df.apply(lambda x: x.round(2) if 'ht' in x.name else x)
        df = df.apply(lambda x: x.round().astype('Int64') if 'dir' in x.name else x)
        df = df.apply(lambda x: x.round().astype('Int64') if 'spd' in x.name else x)
        df = df.apply(lambda x: x.round(1).astype('Int64') if 'pd' in x.name else x)
        
        cols = col_mapping.values()
        
        df = df[cols]
        
        return df
    
    def get_api_site(self,ws,site_name):
        """Return unique site names from the spectra
        Parameters:
            ws (xarray): wave spectra file
            siteName (string): site name that matches a listed site
        Returns:
            df_site (DataFrame): dataframe from the wave spectra of the selected site 
        """
        
        df = self.to_api_df(ws)
        df_site = df[df["location"] == site_name]
        
        return df_site
    
    def get_gfe_winds(self,site_name):
        """Return winds from GFE
        Args:
            site_name (_str_): the site name
        """
        issue = "op + smoothed"
        df = gfe.load(site_name,issue)
        
        return df
    
    def get_winds(self,site_name):
        """Return winds from GFE
        Args:
            site_name (_str_): the site name
        """
        df = self.get_gfe_winds(site_name)
        df.set_index(pd.DatetimeIndex(df["time"]),inplace=True)
        df = df[["wnd_dir","wnd_spd"]]
        df.dropna(inplace=True)  # Remove rows with NaN values

        # calc the hour difference between each time step in hours
        df['diff'] = df.index.to_series().diff().dt.total_seconds() / 3600 

        # Backfilling only the first NaN value in the 'diff' column
        df['diff'] = df['diff'].fillna(method='bfill', limit=1)
        
        df = df.apply(lambda x: x.round().astype(int))
        
        return df
    
    def get_auswave_winds(self,df):
        """Return winds from GFE
        Args:
            df (_DataFrame_): dataframe containing the wind data
            site_name (_str_): the site name
        """
        df = df.copy()
        df.dropna(inplace=True)  # Remove rows with NaN values

        # calc the hour difference between each time step in hours
        df['diff'] = df.index.to_series().diff().dt.total_seconds() / 3600 

        # Backfilling only the first NaN value in the 'diff' column
        df['diff'] = df['diff'].fillna(method='bfill', limit=1)
        
        df = df.apply(lambda x: x.round().astype(int))
    
        return df
    
    def get_autoseas(self,site_name):
        """Return autoseas data from GFE
        Parameters:
            siteName (string): site name that matches a listed site
        Returns:
            df_autoseas (DataFrame): dataframe of the autoseas data from GFE
        """
        
        #derive autoseas from wind
        df_wind = self.get_winds(site_name)
        wind = df_wind.values.tolist()
        
        autoseas_seas = auto_seas.autoSeas(
            siteName = self.transform_site_name(site_name), 
            winds = wind, 
            firstSeas = False, 
            maxFetch = auto_seas.MAX_FETCH,
            windWeights = [0.25,0.75],            
            debug = False,
            returnDir = False,
            returnPdDir = True,
            calcType = "new",
            averageFetch = True,
            varyDecreaseFactors = False,
        )
        
        #now lets create a dataframe to smush
        autoseas_seas_df = pd.DataFrame(autoseas_seas, columns=["seas_ht", "seas_pd", "seas_dir"])
        autoseas_seas_df = autoseas_seas_df.apply(lambda x: x.round(2) if "ht" in x.name else x)
        autoseas_seas_df = autoseas_seas_df.apply(lambda x: x.round().astype(int) if "pd" in x.name else x)
        autoseas_seas_df = autoseas_seas_df.apply(lambda x: x.round().astype(int) if "dir" in x.name else x)
        
        #should always have the same number of rows/timesteps
        autoseas_seas_df.index = df_wind.index
        merged_df = df_wind.join(autoseas_seas_df)
        merged_df.drop("diff",axis=1,inplace=True)
        
        return merged_df
    
    def smush_seas(self,site_name):
        """Smush the seas together with the partitioned data
        Parameters:
            site_name (string): site name that matches a listed site
            df_parts (DataFrame): dataframe of the 
        Returns:
            df_smushed (DataFrame): dataframe of smushed seas
        """
        # get the partitioned table data
        partition = db.get_site_partitions_from_db(site_name)["data"][0][1]
        table = db.get_wavetable_from_db(site_name)["data"]
        col_names = ["time[hrs]", "time[UTC]", "time[WST]", "wind_dir[degrees]", "wind_spd[kn]", "seasw_ht[m]", "seasw_dir[degree]", "seasw_pd[s]", "swell_1_ht", "swell_1_dir", "swell_1_pd"]
        df_table = pd.read_csv(StringIO(table), comment="#", names=col_names, usecols=range(len(col_names)), header=None)
    
        # select seas data
        df_table_seas = df_table[["time[UTC]", "swell_1_ht", "swell_1_dir", "swell_1_pd"]].copy()
        df_table_seas["time[UTC]"] = pd.to_datetime(df_table_seas["time[UTC]"])
        df_table_seas.set_index("time[UTC]", inplace=True)
        
        # generate the autoseas data
        df_autoseas = self.get_autoseas(site_name)
        df_autoseas = df_autoseas.rename_axis("time[UTC]", axis="index")
        df_autoseas.index = pd.to_datetime(df_autoseas.index)
    
        # smush
        df_merged = df_table_seas.merge(df_autoseas, left_index=True, right_index=True, how='inner')
        
        print(df_table_seas)
        print(df_autoseas)
        print(df_merged)
        
        simplified = smusher.SimpleSwell(siteName=self.transform_site_name(site_name), periodSplit=partition)
        df_smushed = simplified.calculate_simpleSwell(df_merged,seas=True)
        df_smushed = simplified.finalFormatting(df_smushed)

        return df_smushed        
    
    def get_site_partitions_df(self,site,*parts):
        """Return the wave spectra partions from site
        Paramaters:
            site (str): Ofcast site name
            parts (list(tuples)): each tuple has the start and end of each partition range
        Returns:
            df (DataFrame): dataframe ready to merge with an Ofcast forecast
         """
        ws = self.partition.multi_parts(*parts)
        df = self.get_api_site(ws,site)

        return df
    
    def format_df(self,df, location, *parts):
        """
        Formats a DataFrame into a custom table format for forecast data.

        Parameters:
        - df (pandas.DataFrame): The DataFrame to be formatted.
        - location (str): The location string.
       
        Returns:
        - str: A formatted string representing the table.
        """

        table = df["location"].iloc[0]
        start_datetime = df["time[UTC]"].iloc[0]
        start_timestamp = int(start_datetime.timestamp())
        start_utc = start_datetime.strftime("%Y%m%d %H%M")
        
        #truncate the seconds 
        df["time[WST]"] = df["time[WST]"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
        df["time[UTC]"] = df["time[UTC]"].apply(lambda x: x.strftime("%Y-%m-%d %H:%M"))
        
        #remove the location for the purposes of api output
        df.drop("location",axis=1,inplace=True)        
        df.drop("run_time",axis=1,inplace=True)        
        fields = ", ".join(df.columns)
        
        # Creating header
        header = "### AUSWAVE Partition Forecast ###\n"
        header += f"# Location:  {location}\n"
        header += f"# Table:  {table}\n"
        header += f"# StartTime: {start_timestamp}\n"
        header += f"# StartUTC:  {start_utc}\n"
        header += f"# Partitions:  {', '.join(str(part) for part in parts)}\n"
        header += f"# Fields:    {fields}\n"
        header += "###\n"
        
        #insert commas and remove the last comma
        formatted_df = df.astype(str)
        formatted_df = formatted_df.apply(lambda x: x + ", ", axis=1)
        formatted_df.iloc[:,-1] = formatted_df.iloc[:,-1].str.rstrip(", ")
        
        # Creating table body
        table_body = tabulate(formatted_df, headers=[], tablefmt='plain', showindex=False)
    
        # Concatenating the header, table body, and footer
        final_output = header + table_body

        return final_output

    def generate_all_sites_to_db(self):
        """Generate the partition splits for all sites and save to the database"""
        site_names = db.get_all_sites()["data"][0]
        logging.info(f"Model run_time: {self.latest_run_time}")
        logging.info(f"Site list: {', '.join(site_names)}")
        for site_name in site_names:
            try:
                self.generate_site_to_db(site_name=site_name)
            except:
                pass

    def generate_site_to_db(self,site_name):
        """Generate the partition splits for all sites and save to the database"""
        
        try:
            table_config = self.get_site_config_db(site_name)
            
            #exit stage left if no data
            if not table_config["success"]:
                logging.warning(table_config["message"])
                return
            # all the site parms from the database
            site_name = table_config["data"]["site_name"]    
            table_name = table_config["data"]["table"]        
            partitions = table_config["data"]["partitions"]    
            
            #generate our table output
            partitioned_df = self.get_site_partitions_df(table_name,*partitions)
            run_time = partitioned_df["run_time"].iloc[0]
            run_time = run_time.to_pydatetime()
            table_output = self.format_df(partitioned_df,site_name,*partitions)
            
            #update the database and printout results
            wave_table = db.add_wavetable_to_db(site_name, run_time, table_output)
            logging.info(f"Saved {site_name} to database")
                
            return wave_table
        
        except Exception as e:
            logging.warning(f"Not able to save {site_name} to database. Exception: {str(e)}")
            return None

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--site",dest="site_name",nargs="?", default="all",help="the forecast site name from Ofcast",required=False)
    args = parser.parse_args()
    site_name=args.site_name
    
    toolbox = PartitionSplitter()
    
    table_config = toolbox.get_site_config_db(site_name)
    
    #exit stage left if no data
    if not table_config["success"]:
        logging.warning(table_config["message"])
        return
    # all the site parms from the database
    site_name = table_config["data"]["site_name"]    
        
    df_smushed = toolbox.smush_seas(args.site_name)
    
    print(df_smushed.head(50))
            
if __name__ == '__main__':
    main()