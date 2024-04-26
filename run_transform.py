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

def generate_output_all_sites(run_time=None, transformed=True):
    """
    Generate html and csv output for all sites in the database.
    """
    try:
        site_names = db.get_all_sites()["data"][0]
    except Exception as e:
        print(f"Error fetching sites from the database: {e}")
        return None
    for site_name in site_names:
        try:
            generate_output_from_config(site_name,run_time,transformed)
        except:
            pass

def generate_output_from_args(args):
    """
    Print out an html table and csv output from the given args.
    """
    try:
        transformer = transform.Transform(
            site_name=args.siteName,
            theta_split=args.theta_split,
            theta_1=args.theta_1,
            theta_2=args.theta_2,
            multiplier=args.multiplier,
            attenuation=args.attenuation,
            thresholds=args.thresholds
        )

        # print_html_from_config(args.siteName)
        table = get_standard_wave_table(args.siteName, args.run_time)
        df,header = transformer.process_wave_table(table)
        transformed_df = transformer.transform_df(df)
        
        if not args.nosave:
            status = transformer.save_to_file(transformed_df)
        
        html_table = transformer.transform_to_html_table(transformed_df)
        transformer.print_html_table(html_table)        
        
    except Exception as e:
        print(f"Error transforming to html output: {e}")
        return None

def generate_output_from_config(site_name, run_time=None, transformed=True):
    """
    Load the configuration from config and output html and csv.
    """
    sites_info = read_config()
    table = get_standard_wave_table(site_name, run_time)
    
    # if the site is not in the config return the standard table
    if site_name not in sites_info or transformed is False:
        transformer = transform.Transform(site_name, 360, 0, 0, 1, 1, [3,2.5,2])
        df,header = transformer.process_wave_table(table)
        transformer.save_to_file(df)
        html_table = transformer.transform_to_html_table(transformed_df)
        transformer.print_html_table(html_table)        
    
    else:
        try: 
            site_data = sites_info[site_name]
            transformer = transform.Transform(
                site_name, 
                site_data["theta_split"],
                site_data["theta_1"], 
                site_data["theta_2"], 
                site_data["multiplier"], 
                site_data["attenuation"], 
                [   
                    site_data["high_threshold"], 
                    site_data["medium_threshold"], 
                    site_data["low_threshold"]
                ]
            )
            df, header = transformer.process_wave_table(table)
            transformer.save_to_file(df)
            print(df.columns)
            
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
            site_data["theta_split"],
            site_data["theta_1"], 
            site_data["theta_2"], 
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
                "theta_split": parts[1].strip(),
                "theta_1": parts[2].strip(),
                "theta_2": parts[3].strip(),
                "multiplier": parts[4].strip(),
                "attenuation": parts[5].strip(),
                "high_threshold": parts[6].strip(),
                "medium_threshold": parts[7].strip(),
                "low_threshold": parts[8].strip(),
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
    #--all paramater should be a switch to generate all sites output from config file, default should be off
    parser.add_argument('--all', action='store_true', help='If used, generate all sites output from config file')
    parser.add_argument('--siteName', type=str, default='Dampier Salt - Cape Cuvier 7 days', help='Site Name')
    parser.add_argument('--theta_split', type=str, default='90', help='Dirction to split theta_1 and theta_2.')
    parser.add_argument('--theta_1', type=str, default='262', help='Theta 1')
    parser.add_argument('--theta_2', type=str, default='20', help='Theta 2')
    parser.add_argument('--multiplier', type=float, default=0.42, help='Multiplier')
    parser.add_argument('--attenuation', type=float, default=1.0, help='Attenuation')
    parser.add_argument('--thresholds', type=str, default="3,2.5,1.5", help='Thresholds')
    parser.add_argument('--run_time', type=str, default=None, help='Run Time: YYYYMMDDHH')
    parser.add_argument('--notrans', action='store_false', help='If used, Transformed=False')
    parser.add_argument('--nosave', action='store_false', help='If used, dont save the file to disk')

    args = parser.parse_args()
    
    # Convert the thresholds string to a list of floats
    args.thresholds = [float(val.strip(',')) for val in args.thresholds.split(",")]

    return args        

def main():
    args = parse_arguments()  
    
    if args.all:
        generate_output_all_sites(run_time=args.run_time, transformed=args.notrans)
    else:
        generate_output_from_args(args)
        # generate_output_from_config(args.siteName)
    
            
if __name__ == '__main__':
    main()