#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    partition_smusher.py

Author: Daz Vink

Classes:
    PartitionSmusher(origin,destination)


Functions:    

"""
import os

# import swellSmusher
import pandas as pd
from io import StringIO
from tabulate import tabulate
import argparse
import logging
import smusher
import autoseas.auto_seas as auto_seas
import gfe

#package imports
import run_transform
import database as db
import models
import amphitrite_configs as configs

BASE_DIR = configs.BASE_DIR

# Configure logging
LOG_FILENAME = os.path.join(BASE_DIR,"autoseas_logfile.log")

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

class PartitionSmusher(object):   
    """Class of methods to breed a mongrel mix of wave spectra, transformations and Ofcast forecasts"""

    def __init__(self,site_name="Woodside - Scarborough 10 Days",first_time_step=None,df_index=None):
        self.site_name = site_name
        self.df_index = df_index
        self.first_time_step = first_time_step
        self.config_file = os.path.join(BASE_DIR,"site_config.txt")
        self.site_tables = self.load_config_file(self.config_file)
        
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
        
        
    def load_config_file(self, config_file):
        """
        Get the table name and partition ranges related to the siteName
        Parameters:
            siteName: ofcast site name
        Returns:
            a dictionary with the table name and partition ranges
        """
        site_tables = {}
        try:
            with open(config_file, 'r') as file:
                for line in file:
                    # processing logic here
                    pass
        except FileNotFoundError:
            logging.error(f"Config file not found: {config_file}")
            raise
        except IOError as e:
            logging.error(f"Error reading config file: {e}")
            raise
        return site_tables
   
    def get_gfe_winds(self, site_name):
        """
        Return winds from GFE.
        Args:
            site_name (str): The site name.
        Returns:
            DataFrame: DataFrame containing wind data from GFE.
        """
        issue = "op + smoothed"
        try:
            df = gfe.load(site_name, issue)
            if df.empty:
                logging.warning(f"No wind data returned for site: {site_name}")
            return df
        except Exception as e:
            logging.error(f"Error loading wind data from GFE for site '{site_name}': {e}")
            raise

    def get_winds(self,site_name,df=None):
        """Return winds from GFE
        Args:
            site_name (_str_): the site name
        """
        try:
            if df is None:
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
        except Exception as e:
            logging.info(f"Error getting winds: {e}")
            raise
            
    def get_auswave_winds(self,df):
        """Return winds from df
        Args:
            df (_DataFrame_): dataframe containing the wind data
            site_name (_str_): the site name
        """
        try: 
            df = df.copy()
            df.dropna(inplace=True)  # Remove rows with NaN values

            # calc the hour difference between each time step in hours
            df['diff'] = df.index.to_series().diff().dt.total_seconds() / 3600 

            # Backfilling only the first NaN value in the 'diff' column
            df['diff'] = df['diff'].fillna(method='bfill', limit=1)
            
            df = df.apply(lambda x: x.round().astype(int))
        
            return df
    
        except Exception as e:
            logging.info(f"Error getting winds: {e}")
            raise
    
    def get_autoseas(self,site_name,df_wind,calc="new"):
        """Return autoseas data from GFE
        Parameters:
            siteName (string): site name that matches a listed site
            df_wind (DataFrame): dataframe of winds [wind_dir, wind_spd, diff]
        Returns:
            df_autoseas (DataFrame): dataframe of the autoseas data from GFE
        """
        try: 
            # list of winds in the format [wnd_spd,wnd_dir,time_period]
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
                calcType = calc,
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
        
        except Exception as e:
            logging.info(f"Error getting autoseas: {e}")
            raise
    
    def smush_seas(self,site_name,df_wind,calc):
        """Smush the seas together with the partitioned data
        Parameters:
            site_name (string): site name that matches a listed site
        Returns:
            df_smushed (DataFrame): dataframe of smushed seas
        """
        try: 
            #derive autoseas from wind
            df_wind = self.get_winds(site_name,df_wind)
            
            # get the partitions from database
            df_table_seas, sea_partition = self.seas_partition_df(site_name)
            
            # generate the autoseas data
            df_autoseas = self.get_autoseas(site_name,df_wind,calc)
            df_autoseas = df_autoseas.rename_axis("time[UTC]", axis="index")
            df_autoseas.index = pd.to_datetime(df_autoseas.index)
            
            # lets get together
            df_merged = df_table_seas.merge(df_autoseas, left_index=True, right_index=True, how='right')
            
            # smush
            smush = smusher.SwellSmusher(siteName=self.transform_site_name(site_name), periodSplit=sea_partition)
            df_smushed = smush.calculate_simpleSwell(df_merged,seas=True)
            df_smushed = smush.finalFormatting(df_smushed)

            # print("\n\n-------------------df_merged-----------------\n")
            #print(df_smushed)
            
            return df_smushed        
        
        except Exception as e:
            logging.info(f"Error smushing seas: {e}")
            raise
    
    def get_seas_partition_timeadjusted_df(self,site_name):
        """Get the partition df with the required first time and index values
        Parameters:
            site_name (string): site name that matches a listed site
        Returns:
            df_partition (DataFrame): dataframe of time adjusted index values    
        """
        try: 
            # get the partitions from database
            df_table_seas, sea_partition = self.seas_partition_df(site_name)
            df_table_seas = self.zero_pad_df(df_table_seas)            
            filtered_df = df_table_seas.loc[df_table_seas.index.intersection(self.df_index)]
            return filtered_df
        
        except Exception as e:
            logging.info(f"Error getting time adjusted partition: {e}")
            raise
        
    def seas_partition_df(self,site_name):
        """Smush the seas together with the partitioned data
        Parameters:
            site_name (string): site name that matches a listed site
        Returns:
            df_table_seas (DataFrame), sea_partition (int): dataframe of partitioned seas, sea partion value in secs (eg: 9)
        """
        try: 
            # get the partitions from database
            response = db.get_site_partitions_from_db(site_name)
            
            if not response["success"]:
                print(response["message"])
                exit()
                
            partitions = response["data"]
            sea_partition = partitions[0][1]
            num_swells = len(partitions)         
            
            # base columns, seas columns and swells, generate swell columns dynamically from num_swells
            base_col_names = ["time[hrs]","time[UTC]","time[WST]","wind_dir[degrees]","wind_spd[kn]","seasw_ht[m]","seasw_dir[degree]","seasw_pd[s]"]
            sea_col_names = ["sea_ht[m]","sea_dir[degree]","sea_pd[s]"]
            swell_col_names = [f"sw{i}_{suffix}" for i in range(1, num_swells) for suffix in ("ht[m]","dir[degree]","pd[s]")]
            col_names = base_col_names + sea_col_names + swell_col_names
            
            #get the data from database
            #transformed_table = db.get_wavetable_from_db(site_name)["data"]
            transformed_table = run_transform.load_from_config(site_name)
            df_table_all = pd.read_csv(StringIO(transformed_table), comment="#", names=col_names, header=None)
            
            # select just seas data
            df_table_seas = df_table_all[["time[UTC]", "sea_ht[m]", "sea_dir[degree]", "sea_pd[s]"]].copy()
            df_table_seas["time[UTC]"] = pd.to_datetime(df_table_seas["time[UTC]"])
            df_table_seas.set_index("time[UTC]", inplace=True)
            
            # rename for smushing purposes
            df_table_seas.rename({
                "sea_ht[m]": "swell_1_ht",
                "sea_dir[degree]": "swell_1_dir",
                "sea_pd[s]": "swell_1_pd"
            }, axis=1, inplace=True)
            
            #reorganise the order in the df to match autoseas output
            df_table_seas = df_table_seas[["swell_1_ht","swell_1_pd","swell_1_dir"]]
                    
            return df_table_seas, sea_partition        
        
        except Exception as e:
            logging.info(f"Error getting sesa partition dataframe: {e}")
            raise
        
    def zero_pad_df(self,df):
        """If first_time_step is before the first time step of the seas partition, prepend the seas with zeros
        Parameters:
            df (DataFrame): dataframe of the partitioned seas
            first_time_step (datetime): the first time step
        Returns:
            df (DataFrame): dataframe of the partitioned seas with the first time step prepended
        """
        first_time_step = self.first_time_step
        
        if first_time_step < df.index[0]:
            try:
                time_index = pd.date_range(start=first_time_step, end=df.index[0], freq="1H")
                df_new = pd.DataFrame(index=time_index, columns=df.columns)
                df_new = df_new.fillna(0)
                df = pd.concat([df_new, df])
            except Exception as e:
                return df
        return df
        
def main():
    
    parser = argparse.ArgumentParser()
    parser.add_argument("--site",dest="site_name",nargs="?", default="all",help="the forecast site name from Ofcast",required=False)
    parser.add_argument("--calc",dest="calc",nargs="?", default="new",help="the calculation used by Autoseas",required=False)
    args = parser.parse_args()
    site_name=args.site_name
    calc = args.calc

    toolbox = PartitionSmusher()
    table_config = toolbox.get_site_config_db(site_name)
    
    #exit stage left if no data
    if not table_config["success"]:
        logging.warning(table_config["message"])
        return
    # all the site parms from the database
    site_name = table_config["data"]["site_name"]    
    winds = toolbox.get_winds(site_name)    
    print(winds)
    df_smushed = toolbox.smush_seas(args.site_name,winds,calc)
    
    print(df_smushed.head(50))
    print(df_smushed.tail(50))
    
            
if __name__ == '__main__':
    main()