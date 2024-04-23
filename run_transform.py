#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    transformer.py

Author: Daz Vink
"""
import os
import argparse
from transformer import transformer_configs as configs
from transformer import transform
import database as db

BASE_DIR = configs.BASE_DIR

def print_html_from_args(args):
    """
    Print out an html table from the given args.
    """
    try:
        transformer = transform.Transform(
            site_name=args.siteName,
            theta_1=args.theta_1,
            theta_2=args.theta_2,
            multiplier=args.multiplier,
            attenuation=args.attenuation,
            thresholds=args.thresholds
        )

        # print_html_from_config(args.siteName)
        table = get_standard_wave_table(args.siteName)
        df,header = transformer.process_wave_table(table)
        transformed_df = transformer.transform_df(df)
        status = transformer.save_to_file(transformed_df)
        html_table = transformer.transform_to_html_table(transformed_df)
        transformer.print_html_table(html_table)        
        
    except Exception as e:
        print(f"Error transforming to html output: {e}")
        return None

def print_html_from_config(site_name, run_time=None, transformed=True):
    """
    Load the configuration parameters from the configuration file, if none exist print the standard table to file.
    """
    sites_info = read_config()
    table = get_standard_wave_table(site_name, run_time)
    
    # if the site is not in the config return the standard table
    if site_name not in sites_info or transformed is False:
        transformer = transform.Transform(site_name, 180, 180, 1, 1, [3,2.5,2])
        df,header = transformer.process_wave_table(table)
        transformer.save_to_file(df)
        html_table = transformer.transform_to_html_table(transformed_df)
        transformer.print_html_table(html_table)        
    
    else:
        try: 
            site_data = sites_info[site_name]
            transformer = transform.Transform(
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
            transformer.save_to_file(df)
            transformed_df = transformer.transform_df(df)
            html_table = transformer.transform_to_html_table(transformed_df)
            transformer.print_html_table(html_table)        
        
        except Exception as e:
            print(f"Error reading site transfomer info: {e}")            

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
        transformer = transform.Transform(
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
    parser.add_argument('--theta_1', type=str, default='262', help='Theta 1')
    parser.add_argument('--theta_2', type=str, default='20', help='Theta 2')
    parser.add_argument('--multiplier', type=float, default=0.42, help='Multiplier')
    parser.add_argument('--attenuation', type=float, default=1.0, help='Attenuation')
    parser.add_argument('--thresholds', type=str, default="3,2.5,1.5", help='Thresholds')

    args = parser.parse_args()
    
    # Convert the thresholds string to a list of floats
    args.thresholds = [float(val.strip(',')) for val in args.thresholds.split(",")]

    return args        

def main():
    args = parse_arguments()  # Ensure this function is updated to use the refactored class attributes
    
    print_html_from_args(args)
    # print_html_from_config(args.siteName)
    
            
if __name__ == '__main__':
    main()