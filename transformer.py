#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    transformer.py

Author: Daz Vink
"""
import os
import pandas as pd
import argparse
import amphitrite_configs as configs
import requests
import pandas as pd
import argparse

BASE_DIR = configs.BASE_DIR

class WaveTable:
    """
    Class for generating modified wave/swell tables from an API source.
    """
    
    def __init__(self, site_name='Dampier Salt - Cape Cuvier 7 days', table_name='Cape_Cuvier_Offshore', 
                 theta_1=260, theta_2=20, multiplier=1.0, attenuation=1.0, model='long', 
                 thresholds=[0.3, 0.2, 0.15]):
        """
        Initialize the WaveTable object with site details and processing parameters.
        """
        self.site_name = site_name
        self.table_name = table_name
        self.theta_1 = theta_1
        self.theta_2 = theta_2
        self.multiplier = multiplier
        self.attenuation = attenuation
        self.model = model
        self.thresholds = thresholds
        self.api_url = f"{os.path.join(BASE_DIR,"api.cgi?get=site&site_name=",self.site_name.replace(' ', '%20'))}"
        
        # Output file setup from configurations would go here
        self.output_file = 'path_to_save/{}_data.csv'.format(self.site_name.replace(' ', '_').replace('-', ''))

    def get_wave_table(self):
        """
        Fetches wave table data from the API and processes it into a pandas DataFrame.
        Handles a dynamic number of swells (sw#) in the data.
        """
        response = requests.get(self.api_url)
        if response.status_code != 200:
            raise Exception("API request failed with status code {}".format(response.status_code))

        # Process the text output into a DataFrame
        lines = response.text.split("\n")[9:]  # Skip headers
        data = [line.split(",") for line in lines if line]

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
        
        df["time[UTC]"] = pd.to_datetime(df["time[UTC]"], format='%Y-%m-%d %H:%M', errors='coerce')
        df["time[WST]"] = pd.to_datetime(df["time[WST]"], format='%Y-%m-%d %H:%M', errors='coerce')

        return df
    
    def save_to_file(self, df):
        """
        Saves the processed DataFrame to a CSV file.
        """
        df.to_csv(self.output_file, index=False)
        print(f"Data saved to {self.output_file}")    

def parse_arguments():
    '''
    Parse args from the command line and provide some defaults
    '''
    parser = argparse.ArgumentParser(description='Process WaveTable parameters.')
    
    # Add all of your parameters here as arguments.
    parser.add_argument('--siteName', type=str, default='Dampier Salt - Cape Cuvier 7 days', help='Site Name')
    parser.add_argument('--tableName', type=str, default='Cape_Cuvier_Offshore', help='Table Name')
    parser.add_argument('--theta_1', type=str, default='260', help='Theta 1')
    parser.add_argument('--theta_2', type=str, default='020', help='Theta 2')
    parser.add_argument('--multiplier', type=float, default=1.0, help='Multiplier')
    parser.add_argument('--attenuation', type=float, default=1.0, help='Attenuation')
    parser.add_argument('--model', type=str, default='long', help='Model')
    parser.add_argument('--thresholds', type=str, default="3,2.5,1.5", help='Thresholds')

    args = parser.parse_args()
    
    # Convert the thresholds string to a list of floats
    args.thresholds = [float(val.strip(',')) for val in args.thresholds.split(",")]

    return args        

def main():
    args = parse_arguments()  # Ensure this function is updated to use the refactored class attributes
    
    wave_table = WaveTable(
        site_name=args.siteName,
        table_name=args.tableName,
        theta_1=args.theta_1,
        theta_2=args.theta_2,
        multiplier=args.multiplier,
        attenuation=args.attenuation,
        model=args.model,
        thresholds=args.thresholds
    )

    df = wave_table.get_wave_table()
    wave_table.save_to_file(df)
    
            
if __name__ == '__main__':
    main()