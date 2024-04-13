#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    transformer.py

Author: Daz Vink
"""
import os
import pandas as pd
import numpy as np
import argparse
from transformer import transformer_configs as configs
import database as db
from tabulate import tabulate

BASE_DIR = configs.BASE_DIR

class Transform:
    """
    Class for generating modified wave/swell tables from an API source.
    """
    
    def __init__(self, site_name='Dampier Salt - Cape Cuvier 7 days', theta_1=260, theta_2=20, multiplier=1.0, attenuation=1.0, thresholds=[0.3, 0.2, 0.15]):
        """
        Initialize the WaveTable object with site details and processing parameters.
        """
        self.site_name = site_name
        self.theta_1 = float(theta_1)
        self.theta_2 = float(theta_2)
        self.multiplier = float(multiplier)
        self.attenuation = float(attenuation)
        self.thresholds = [float(x) for x in thresholds]
        self.output_file = os.path.join(BASE_DIR,'tables/{}_data.csv'.format(self.site_name.replace(' ', '_').replace('-', '')))

    def transform_to_table(self, df, header):
        """
        Transforms the DataFrame into a formatted table for output.

        Args:
            df (DataFrame): the transfomed DataFrame
            header (list(str)): the header information from the original table
        """
        #take the first 9 lines of the header and join them together
        header = "\n".join(header) + "\n"
        
        #insert commas and remove the last comma
        formatted_df = df.astype(str)
        formatted_df = formatted_df.apply(lambda x: x + ", ", axis=1)
        formatted_df.iloc[:,-1] = formatted_df.iloc[:,-1].str.rstrip(", ")
        
        # Creating table body
        table_body = tabulate(formatted_df, headers=[], tablefmt='plain', showindex=False)
    
        # Concatenating the header, table body, and footer
        final_output = header + table_body

        return final_output
    
    def transform_df(self, df):
        """
        Applies a transformation to each wave height column based on peak wave direction, updates the individual
        height columns in the DataFrame with their transformed values, and adds a new column for the combined
        significant wave height data.

        Parameters:
            df (pd.DataFrame): DataFrame containing wave data with height and direction columns.

        Returns:
            pd.DataFrame: Updated DataFrame including the individual transformed wave heights and the combined
                        significant wave height data.
        """
        transformed_df = df.copy()

        # Identify columns related to wave heights and their corresponding direction
        hs_columns = [col for col in transformed_df.columns if "ht" in col]
        transformed_hs_list = []

        for hs_col in hs_columns:
            
            peak_dir_col = hs_col.split("_")[0] + "_dir[degree]"
            hs = transformed_df[hs_col]
            peak_dir = transformed_df[peak_dir_col]

            # Convert peak direction to radians for accurate trigonometric calculations
            rad_peak_dir = np.radians(peak_dir)

            # Apply adjustments for directions based on the same criteria
            adjusted_dir = np.where(
                (rad_peak_dir < np.radians(self.theta_1)) & (rad_peak_dir >= np.pi),
                self.theta_1, peak_dir
            )
            adjusted_dir = np.where(
                (rad_peak_dir > np.radians(self.theta_2)) & (rad_peak_dir < np.pi),
                self.theta_2, adjusted_dir
            )

            # Update the DataFrame with transformed wave heights for each column
            transformed_df[peak_dir_col] = np.array(adjusted_dir, dtype=int)
            
            #ignore the total hs column
            if hs_col != "seasw_ht[m]":
            
                # Apply cosine adjustments based on direction
                adjusted_hs = np.where(
                    (rad_peak_dir < np.radians(self.theta_1)) & (rad_peak_dir >= np.pi),
                    np.cos(rad_peak_dir - np.radians(self.theta_1)) * hs, hs
                )

                adjusted_hs = np.where(
                    (rad_peak_dir > np.radians(self.theta_2)) & (rad_peak_dir < np.pi),
                    np.cos(rad_peak_dir - np.radians(self.theta_2)) * adjusted_hs, adjusted_hs
                )
                
                transformed_df[hs_col] = np.round(adjusted_hs,2)
                transformed_hs_list.append(pd.Series(np.round(adjusted_hs,2), index=hs.index))

        # Combine transformed heights to calculate the combined wave height metric
        hs_combined = pd.concat(transformed_hs_list, axis=1)

        # Calculate the sum of squares of transformed heights, take the square root, and apply the multiplier
        transformed_df["seasw_ht[m]"] = np.round((hs_combined.pow(2).sum(axis=1).pow(0.5)) * self.multiplier,2)

        return transformed_df

    def process_wave_table(self,formatted_table):
        """
        Processes a formatted wave data table from the database and passes to a pandas DataFrame.
        Handles a dynamic number of swells (sw#) in the data.
        """
        lines = formatted_table.split("\n")
        
        # Separate header and data based on the "#" at the start of header lines
        header = [line for line in lines if line.startswith("#")]
        
        #inject some transformed header information
        header_text = f", Transformed with \u03B8 west: {int(self.theta_1)}, \u03B8 east: {int(self.theta_2)}, multiplier: {self.multiplier}, attenuation: {self.attenuation}" 
        header = [line + header_text if "Table:" in line else line for line in header]

        data_lines = [line for line in lines if not line.startswith("#") and line.strip()]
        data = [line.split(",") for line in data_lines if data_lines]
       
        # Assuming the data starts with certain columns before dynamic swell columns
        initial_columns = ["time[hrs]", "time[UTC]", "time[WST]", "wind_dir[degrees]", 
                        "wind_spd[kn]", "seasw_ht[m]", "seasw_dir[degree]", "seasw_pd[s]",
                        "sea_ht[m]", "sea_dir[degree]", "sea_pd[s]"]
        num_columns = len(data[0])  # Total number of columns in the first row of data
        swell_columns = num_columns - len(initial_columns)  # Number of swell columns
        
        # Generate dynamic column names for swells
        swell_column_names = []
        for i in range(1, swell_columns // 3 + 1):  # Assuming each swell has 3 columns (height, period, direction)
            swell_column_names.extend([f"sw{i}_ht[m]", f"sw{i}_dir[degree]", f"sw{i}_pd[s]"])

        columns = initial_columns + swell_column_names
        df = pd.DataFrame(data, columns=columns)

        # Convert columns to appropriate data types, handle missing values, etc.
        for col in columns:
            if "dir" in col or "spd" in col or "ht" in col or "pd" in col:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        return df, header
    
    def save_to_file(self, df):
        """
        Saves the processed DataFrame to a CSV file.
        """
        df.to_csv(self.output_file, index=False)
        print(f"Data saved to {self.output_file}")    

def load_from_config(site_name, run_time=None, transformed=True):
    """
    Load the configuration parameters from the configuration file.
    """
    sites_info = read_config()
    table = get_standard_wave_table(site_name, run_time)
    
    # if the site is not in the config return the standard table
    if site_name not in sites_info or transformed is False:
        return table
    
    try: 
        site_data = sites_info[site_name]
        transformer = Transform(
            site_name, 
            site_data["western_theta"], 
            site_data["eastern_theta"], 
            site_data["multiplier"], 
            site_data["attenuation"], 
            [   
                site_data["high_threshold"], 
                site_data["medium_threshold"], 
                site_data["low_threshold"]
            ]
        )
        
        df,header = transformer.process_wave_table(table)
        transformed_df = transformer.transform_df(df)
        transformed_table = transformer.transform_to_table(transformed_df, header)
        
        return transformed_table
    except Exception as e:
        print(f"Error loading from config: {e}")
        return None
                
def read_config():
    """
    Read the configuration file from "transformer_site_config.txt".
    """
    
    try: 
        config_file = os.path.join(BASE_DIR, "transformer_site_config.txt")
        with open(config_file, "r") as f:
            config = [line.strip() for line in f if line.strip() and not line.strip().startswith("#")]
        
        #create a json object from each line of the config file
        sites = {
            parts[0].strip(): {  # Use the "site" value as the key
                "western_theta": parts[1].strip(),
                "eastern_theta": parts[2].strip(),
                "multiplier": parts[3].strip(),
                "attenuation": parts[4].strip(),
                "high_threshold": parts[5].strip(),
                "medium_threshold": parts[6].strip(),
                "low_threshold": parts[7].strip(),
            }
            for line in config
            for parts in [line.split(",")]  # Split once and use multiple times, then strip whitespace
        }
        return sites
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return None
    
def get_standard_wave_table(site_name, run_time=None):
    """
    Fetches wave data from the database and returns the formatted table data.
    """
    try:
        result = db.get_wavetable_from_db(site_name, run_time) if run_time else db.get_wavetable_from_db(site_name)
        data = result["data"]
        return data
    except Exception as e:
        print(f"Error fetching wave data from the database: {e}")
        return None
    
def parse_arguments():
    '''
    Parse args from the command line and provide some defaults
    '''
    parser = argparse.ArgumentParser(description='Process WaveTable parameters.')
    
    # Add all of your parameters here as arguments.
    parser.add_argument('--siteName', type=str, default='Dampier Salt - Cape Cuvier 7 days', help='Site Name')
    parser.add_argument('--theta_1', type=str, default='260', help='Theta 1')
    parser.add_argument('--theta_2', type=str, default='020', help='Theta 2')
    parser.add_argument('--multiplier', type=float, default=1.0, help='Multiplier')
    parser.add_argument('--attenuation', type=float, default=1.0, help='Attenuation')
    parser.add_argument('--thresholds', type=str, default="3,2.5,1.5", help='Thresholds')

    args = parser.parse_args()
    
    # Convert the thresholds string to a list of floats
    args.thresholds = [float(val.strip(',')) for val in args.thresholds.split(",")]

    return args        

def main():
    args = parse_arguments()  # Ensure this function is updated to use the refactored class attributes
    
    # transformer = Transform(
    #     site_name=args.siteName,
    #     theta_1=args.theta_1,
    #     theta_2=args.theta_2,
    #     multiplier=args.multiplier,
    #     attenuation=args.attenuation,
    #     thresholds=args.thresholds
    # )

    table = load_from_config(args.siteName)
    # table = transformer.get_standard_wave_table()
    # print(table)
    # df,header = transformer.process_wave_table(table)
    # transformed_df = transformer.transform_df(df)
    # transformed_table = transformer.transform_to_table(transformed_df, header)
    # print(transformed_table)
    
    # print(df)        
    print(table)
    # print(transformed_df.head(50))        
            
if __name__ == '__main__':
    main()