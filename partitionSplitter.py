#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    partitionSplitter.py

Classes:
    PartitionSplitter(origin,destination)

Functions:    
"""
import os
# os.environ[ 'NUMBA_CACHE_DIR' ] = '/tmp/'
#os.environ[ 'CONDA_DEFAULT_ENV' ] = 'mlenv'

# import swellSmusher
import partition
import pandas as pd
from tabulate import tabulate
import argparse
import logging

#package imports
import database as db

class PartitionSplitter(object):   
    """Class of methods to breed a mongrel mix of wave spectra, transformations and Ofcast forecasts"""

    def __init__(self):
        self.partition = partition.Partitions()
        self.dir_path = "/cws/op/webapps/er_ml_projects/davink/amphitrite"
        self.config_file = os.path.join(self.dir_path,'site_config.txt')
        self.site_tables = self.load_config_file(self.config_file)
        
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
            site = session.query(db.Site).filter_by(site_name=site_name).first()
            if site:
                return {"success": True, "message": f"'{site_name} data found", "data": site.to_json()}
            else:
                return {"success": False, "message": f"Site with name '{site_name}' not found"}
        except Exception as e:
            # Log the exception as needed
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
            
        cols.extend(["location","time_local"])
        
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
            "wdir": "wnd_dir[degrees]",
            "wspd": "wnd_spd[kn]",
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
        df = df.apply(lambda x: x.round().astype('Int64') if 'pd' in x.name else x)
        
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
    
    def get_ofcast_forecast(self,site):
        """Return the Ofcast forecast from site
        Paramaters:
            site (str): Ofcast site name            
        Returns:
            df (DataFrame): dataframe of forecast from Ofcast 
         """
    
        df = pd.DataFrame()
        df = self.smusher.get_archived_forecast()[0]
        index = self.smusher.get_archived_forecast()[1]
        index = pd.DatetimeIndex(index.values,tz="Australia/Perth")
        df.index = index
        df["time_local"] = index.to_pydatetime()

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
        
        #remove the location for the purposes of api output
        df.drop("location",axis=1,inplace=True)        
        df.drop("run_time",axis=1,inplace=True)        
        fields = ",".join(df.columns)
        
        # Creating header
        header = "### AUSWAVE Partition Forecast ###\n"
        header += f"# Location:  {location}\n"
        header += f"# Table:  {table}\n"
        header += f"# StartTime: {start_timestamp}\n"
        header += f"# StartUTC:  {start_utc}\n"
        header += f"# Partitions:  {','.join(str(part) for part in parts)}\n"
        header += f"# Fields:    {fields}\n"
        header += "###\n"
        
        # Creating table body
        table_body = tabulate(df, headers='keys', tablefmt='plain', showindex=False)

        # Concatenating the header, table body, and footer
        final_output = header + table_body

        return final_output

    def generate_all_sites_to_db(self):
        """Generate the partition splits for all sites and save to the database"""
        site_names = db.get_all_sites()["data"]
        logging.info(site_names)
        for site_name in site_names:
            logging.info(site_name)
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
                print(table_config["message"])
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
            logging.info(f"successfly saved {site_name} to database")
                
            return wave_table
        
        except Exception as e:
            logging.warning(f"Not able to save {site_name} to database. Exception: {str(e)}")
            return None

def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--site",dest="site_name",nargs="?", default="all",help="the forecast site name from Ofcast",required=False)
    args = parser.parse_args()
    
    toolbox = PartitionSplitter()
    
    if args.site_name.strip().lower() == 'all':
        toolbox.generate_all_sites_to_db()
    else:
        wave_table = toolbox.generate_site_to_db(site_name=args.site_name)
        table = wave_table["data"]
        print(table)
            
if __name__ == '__main__':
    main()