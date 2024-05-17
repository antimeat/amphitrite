#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    transformer.py

Author: Daz Vink
"""
import os
import sys
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
sys.path.append(parent_dir)

import pandas as pd
import numpy as np
from tabulate import tabulate
import argparse

#local imports relative to amphtirite
from transformer import transformer_configs as configs

# Set the umask to 0 to ensure that no permissions are masked
os.umask(0)

BASE_DIR = configs.BASE_DIR

class Transform:
    """
    Class for generating modified wave/swell tables from an API source.
    """
    
    def __init__(self, site_name='Dampier Salt - Cape Cuvier 7 days', theta_split=90,theta_1=262, theta_2=20, multi_short=1.0, multi_long=1.0, attenuation=1.0, thresholds=[0.3, 0.2, 0.15]):
        """
        Initialize the WaveTable object with site details and processing parameters.
        """
        self.site_name = site_name
        self.theta_split = float(theta_split)
        self.theta_1 = float(theta_1)
        self.theta_2 = float(theta_2)
        self.multi_short = float(multi_short)
        self.multi_long = float(multi_long)
        self.attenuation = float(attenuation)
        self.thresholds = [float(x) for x in thresholds]
        self.output_file = os.path.join(BASE_DIR,'tables/{}_data.csv'.format(self.site_name.replace(' ', '_').replace('-', '')))
        self.theta_min = 80
        self.config = self.check_config()

    def check_config(self):
        """
        Check the configuration settings are valid for the transformer.
        """
        # first check form thetas = 0 (default value to bail the transformer)
        if self.theta_1 == self.theta_2 == 0:
            return False
        
        # now we set thetas to the reference setup and check if they are valid
        theta_rot = self.rotation_theta()
        
        # Rotate theta_1 and theta_2, and replace 0 with 360
        rot_theta_1 = np.mod(self.theta_1 + theta_rot, 360)
        rot_theta_1 = 360 if rot_theta_1 == 0 else rot_theta_1

        rot_theta_2 = np.mod(self.theta_2 + theta_rot, 360)
        rot_theta_2 = 360 if rot_theta_2 == 0 else rot_theta_2
        
        rot_theta_split = np.mod(self.theta_split + theta_rot, 360)
        rot_theta_split = 360 if rot_theta_split == 0 else rot_theta_split
        
        #check if thetas are valid
        if (rot_theta_1 <= rot_theta_2) or (rot_theta_1 <= rot_theta_split) or (rot_theta_2 >= rot_theta_split):
            return False       
        
        return True
        
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

    def deg(self,deg):
        '''
        Caculate met view of ocean directions
        '''
        while deg < 0 or deg >= 360:
        
            if deg < 0:
                deg = deg + 360
            if deg >= 360:
                deg = deg - 360
            
        return deg

    def highlightHsColor(self, s):
        '''
        Set the background colour to use for a Hs value in a css style tag
        :param s: the Hs
        :type s: int/float
        :return: background-color to use for a css style
        :rtype: string
        '''
        if s is None or not s:
            s = '0'
         
        data = float(s)
        
        try:
            thresholds = self.thresholds
            if not isinstance(thresholds, (list, tuple)) or len(thresholds) != 3:
                raise ValueError("Expected get_thresholds() to return a list/tuple of 3 values.")
            
            if data <= float(thresholds[2]):
                col = ''
            elif data <= float(thresholds[1]):
                col = 'LightGreen'
            elif data <= float(thresholds[0]):
                col = 'Gold'
            elif data <= 10:
                col = 'Red'
            else:
                col = ''

        except Exception as e:
            print(f"Exception in highlightHsColor: {type(s)}<br>")
            col = ''

        return 'background-color: {}'.format(col)


    def highlightDnColor(self,s):
        '''
        Set the background colour to use for a Dn value in a css style tag
            :param s: the Dn
            :type s: int/float
            :return: background-color to use for a css style
            :rtype: string
        '''
        try:		
            data = int(s)
            col = 'mintcream'
        except:
            col = ''
        
        return 'background-color: {}'.format(col)

    def highlightTimeColor(self,s):
        '''
        Set the border formatting to EST
            :param s: the row series
            :type s: string/float/int
            :return: array of border settings to use for a css style
            :rtype: array
        '''
        zTime = 12
        borders = []

        try:
            hour = int(s['hour'])
        except:
            hour = 0
	
        if (hour == zTime):
            borders.append('border-bottom: 1px solid #000')
            x  = range(1,len(s))
            for i in x:
                borders.append('border-bottom: 1px solid #000')

        else:
            x  = range(0,len(s))
            for i in x:
                borders.append('border-bottom: none')

        return borders
		
    def print_html_table(self, df):
        '''
        Print out an HTML version of the table with styles and formatting, dynamically adjusting to the number of swells.
        '''
        # Dynamically calculate the number of swells from the column names
        swell_height_columns = [col for col in df.columns if 'ht' in col]
        swell_direction_columns = [col for col in df.columns if 'dir' in col]
        swell_period_columns = [col for col in df.columns if 'pd' in col]
        num_swells = len(swell_height_columns) - 2

        # Define styles for the HTML table
        styles = [
            dict(selector='table', props=[('margin', '0 auto'), ('border', '1px solid #000')]),
            dict(selector='tr', props=[('position', 'relative'), ('transition', 'background-color 0.1s ease')]),  # Added relative positioning here
            dict(selector='tr:hover', props=[('background-color', 'lightgrey'), ('z-index', '1')]),  # Applying a higher z-index on hover

            dict(selector='td', props=[('font-size', '100%'), ('text-align', 'center')]),
            dict(selector='caption', props=[('font-size', '150%'), ('font-weight', 'bold'), ('caption-side', 'top')]),
            dict(selector='thead th',props=[('position', 'sticky'), ('top', '0px'), ('background-color', '#fff'), ('z-index', '2'), ('font-weight', 'bold'),('text-align', 'center'),('border', '1px solid #000')]),
            
            # Set the first two columns to be sticky
            dict(selector='th:nth-child(1)', props=[('position', 'sticky'), ('top', '0px'), ('left', '0px'), ('background-color', 'cornsilk'), ('z-index', '3'), ('font-weight', 'bold'),('text-align', 'center')]),
            dict(selector='td:nth-child(1)', props=[('position', 'sticky'), ('top', '0px'), ('left', '0px'), ('background-color', 'cornsilk'), ('z-index', '2'), ('font-weight', 'bold'),('text-align', 'center')]),
            dict(selector='th:nth-child(2)', props=[('position', 'sticky'), ('top', '0px'), ('left', '29px'), ('background-color', 'cornsilk'), ('z-index', '3'), ('font-weight', 'bold'),('text-align', 'center')]),
            dict(selector='td:nth-child(2)', props=[('position', 'sticky'), ('top', '0px'), ('left', '29px'), ('background-color', 'cornsilk'), ('z-index', '2'), ('font-weight', 'bold'),('text-align', 'center')]),
        ]

        # Create subsets for styling specific columns
        groupSubset = ['blank' + ('' if i == 0 else str(i)) for i in range(num_swells + 1)]

        attributes = 'align="center"'
        groupProperties = {'border-right': '1px solid #000', 'border-left': '1px solid #000'}
        
        # Set the caption for the table depending on transformed or not
        caption = self.site_name
        if self.config:
            caption += f", Transformed with \u03B8 west: {int(self.theta_1)}, \u03B8 east: {int(self.theta_2)}, multi_short: {self.multi_short}, multi_long: {self.multi_long}, attenuation: {self.attenuation}"         
        
        # Convert columns to numeric and set NaN for errors
        df[swell_height_columns + swell_direction_columns + swell_period_columns] = df[swell_height_columns + swell_direction_columns + swell_period_columns].apply(pd.to_numeric, errors='coerce')

        # Formatting dictionaries for different column types
        formatter = {col: "{:.2f}" for col in swell_height_columns}
        formatter.update({col: "{:d}" for col in swell_period_columns if pd.api.types.is_numeric_dtype(df[col])})
        formatter.update({col: "{:03d}" for col in swell_direction_columns if pd.api.types.is_numeric_dtype(df[col])})

        # Styling and formatting the DataFrame for HTML
        styler = df.style
        styler = styler.applymap(self.highlightHsColor, subset=swell_height_columns)
        styler = styler.applymap(self.highlightDnColor, subset=swell_direction_columns)
        styler = styler.apply(self.highlightTimeColor, axis=1)
        styler = styler.set_table_styles(styles)
        styler = styler.set_table_attributes(attributes)
        styler = styler.set_caption(caption)
        styler = styler.set_properties(**groupProperties, subset=groupSubset)
        styler = styler.format(formatter, na_rep="")
        styler = styler.hide(axis='index').to_html()

        print(styler)
        
        # Save the HTML table to a file
        file_name = self.output_file.replace('.csv', '.html')
        with open(file_name, 'w') as f:
            f.write(styler)

        # Set permissions to 666 (read and write for user, group, and others)
        # os.chmod(file_name, 0o666)
        
    def transform_to_html_table(self, df):
        
        # Ensure 'time[UTC]' is in datetime format and set as index
        df['time[UTC]'] = pd.to_datetime(df['time[UTC]'])
        df.set_index('time[UTC]', inplace=True)

        # Resample the DataFrame to 3-hour intervals
        df = df.resample('3H').first()
        
        # Identify swell columns by pattern
        sw_ht_columns = [col for col in df.columns if 'sw' in col and 'ht[m]' in col and 'seasw' not in col]
        sw_dir_columns = [col for col in df.columns if 'sw' in col and 'dir[degree]' in col and 'seasw' not in col]
        sw_pd_columns = [col for col in df.columns if 'sw' in col and 'pd[s]' in col and 'seasw' not in col]
        num_swells = len(sw_ht_columns) 

        # print(f"Number of swells detected: {num_swells}")

        # Selecting relevant columns and renaming
        base_columns = ['wind_dir[degrees]', 'wind_spd[kn]', 
                        'sea_ht[m]', 'sea_dir[degree]', 'sea_pd[s]',
                        'seasw_ht[m]', 'seasw_dir[degree]', 'seasw_pd[s]'
                        ]
        columns_to_keep = base_columns + sw_ht_columns + sw_pd_columns + sw_dir_columns
        df = df[columns_to_keep].round(2).replace({0: np.nan}).fillna('')

        # Extract day and hour from index
        df['day'] = df.index.day.astype(str)
        df['hour'] = df.index.hour.astype(str)

        # Extracting day and hour from 'time[UTC]' for instance
        # df['day'] = df['time[UTC]'].apply(lambda x: x.split()[0].split('-')[2])
        # df['hour'] = df['time[UTC]'].apply(lambda x: x.split()[1].split(':')[0])
        
        #create some blank columns        
        df['blank'] = ''
        for i in range(1, num_swells + 2):
            df['blank' + str(i)] = ''            
    
        #create a list of columns to use and reorder
        columns = ['day','hour',
                    'seasw_ht[m]', 'seasw_dir[degree]', 'seasw_pd[s]', 'blank',
                    'sea_ht[m]', 'sea_pd[s]', 'sea_dir[degree]',
                    ]
        new_columns = ['day','hour',
                    'seasw_ht', 'seasw_pd', 'seasw_dir', 'blank',
                    'sea_ht', 'sea_pd', 'sea_dir',
                    ]
        
        for i in range(1,num_swells + 1):
            columns.append(f'blank{i}')
            new_columns.append(f'blank{i}')
            columns.append(f'sw{i}_ht[m]')
            new_columns.append(f'sw{i}_ht')
            columns.append(f'sw{i}_pd[s]')
            new_columns.append(f'sw{i}_pd')
            columns.append(f'sw{i}_dir[degree]')
            new_columns.append(f'sw{i}_dir')

        
        # Renaming columns by removing the units directly in the DataFrame
        rename_dict = {col: col.split('[')[0] for col in df.columns if '[' in col and 'time' not in col}
        df.rename(columns=rename_dict, inplace=True)
        df.reset_index(inplace=True)
        
        return df[new_columns]

    def rotation_theta(self):
        """
        Determine the angle to rotate everything such that we have a reference of theta_2 = 10 deg
        """
        theta = np.abs(360 - self.theta_2) + 10
        return theta
    
    def rotate_dirs(self, dirs, theta_rot):
        """
        Take the peak directions and rotate them by the angle determined by theta_rot.

        Args:
            dirs (pd.Series): directions to rotate
        """
        # Rotate directions and wrap around using modulo 360
        rot_dirs = np.mod(dirs + theta_rot, 360)
        
        # Replace 0 with 360 directly using numpy where function
        rot_dirs = np.where(rot_dirs == 0, 360, rot_dirs).astype(int)
        
        # Rotate theta_1 and theta_2, and replace 0 with 360
        rot_theta_1 = np.mod(self.theta_1 + theta_rot, 360)
        rot_theta_1 = 360 if rot_theta_1 == 0 else rot_theta_1

        rot_theta_2 = np.mod(self.theta_2 + theta_rot, 360)
        rot_theta_2 = 360 if rot_theta_2 == 0 else rot_theta_2
        
        rot_theta_split = np.mod(self.theta_split + theta_rot, 360)
        rot_theta_split = 360 if rot_theta_split == 0 else rot_theta_split
        
        return rot_dirs, rot_theta_split, rot_theta_1, rot_theta_2

    def get_num_swells(self, columns):
        """
        Get the number of swells in the DataFrame based on the column names.
        """
        num_swells = len([col for col in columns if "ht" in col and "seasw" not in col])
        return num_swells
    
    def get_interpolated_multiplier(self, num_swells, swell_index):
        """
        Calculate the interpolated multiplier based on the upper and lower bounds,
        """
        if swell_index == 0:
            return self.multi_short
        
        swell_index -= 1  # Convert 1-based index to 0-based index for internal calculation
        multiplier = self.multi_short + (self.multi_long - self.multi_short) * (swell_index / (num_swells - 1))
        return multiplier

    def transform_df(self, df):
        """
        Applies transformations to wave height columns based on wave direction,
        updates the individual height columns in the DataFrame with their transformed values,
        and adds a new column for the combined significant wave height.
        """
        
        # this is our last chance to bail if thetas are not valid, return the df as is if not valid
        if not self.config:
            print("<h4>Not transforming this table</h4>")
            return df
        
        transformed_df = df.copy()
        
        # Set the number of swells based on the DataFrame columns
        num_swells = self.get_num_swells(transformed_df.columns)
        
        # Identify columns related to wave heights and their corresponding directions
        hs_columns = [col for col in transformed_df.columns if "ht" in col] 
        total_peak_dir = transformed_df["seasw_dir[degree]"].replace(0, 360)
        transformed_hs_list = []

        for hs_col in hs_columns:
            peak_dir_col = hs_col.split("_")[0] + "_dir[degree]"
            peak_pd_col = hs_col.split("_")[0] + "_pd[s]"
            hs = transformed_df[hs_col]
            peak_dir = transformed_df[peak_dir_col]
            adjusted_hs = hs.copy()
            
            #pull the swell # from the column name
            swell_str = hs_col.split("_")[0]
            swell_num = 1
            
            if swell_str == "seasw":
                swell_num = 0
            elif swell_str == "sea":
                swell_num = 1
            else:
                swell_num = int(swell_str[-1]) + 1
                
            # print(f"Processing swell {swell_num} with {hs_col}")
            # print(f"multiplier for {swell_num} is {self.get_interpolated_multiplier(num_swells, swell_num)}")
            
            #rotate all the dirs to our reference setup using theta_2 = 10
            theta_rotate = self.rotation_theta()
            peak_dir_rotated, theta_split_rotated, theta_1_rotated, theta_2_rotated = self.rotate_dirs(peak_dir, theta_rotate)
            
            # Condition 1: Peak direction between theta_1 and theta_split_rotated
            condition_1 = ((peak_dir_rotated < theta_1_rotated) & (peak_dir_rotated > theta_split_rotated))
            peak_dir_rotated = np.where(condition_1 & ((theta_1_rotated - peak_dir_rotated) >= self.theta_min), theta_1_rotated - self.theta_min, peak_dir_rotated)
            adjusted_hs = np.where(condition_1, np.cos(np.radians(theta_1_rotated - peak_dir_rotated)) * hs, adjusted_hs)
            peak_dir_rotated = np.where(condition_1, theta_1_rotated, peak_dir_rotated)
                                    
            # Condition 2: Peak direction between theta_2 and theta_split_rotated
            condition_2 = (peak_dir_rotated > theta_2_rotated) & (peak_dir_rotated < theta_split_rotated)
            peak_dir_rotated = np.where(condition_2 & ((peak_dir_rotated - theta_2_rotated) >= self.theta_min), theta_2_rotated + self.theta_min, peak_dir_rotated)
            adjusted_hs = np.where(condition_2, np.cos(np.radians(peak_dir_rotated - theta_2_rotated)) * hs, adjusted_hs)
            peak_dir_rotated = np.where(condition_2, theta_2_rotated, peak_dir_rotated)
            
            #unrotate the dirs back to the original setup
            peak_dir, theta_split, theta_1, theta_2 = self.rotate_dirs(peak_dir_rotated, -theta_rotate)
            
            # finalise the dirs
            transformed_df[peak_dir_col] = peak_dir

            #dont include the total_hs to a few calcs
            if "seasw" not in hs_col:
                #magical attenuation and multiplier for period and hs
                adjusted_hs = adjusted_hs * self.get_interpolated_multiplier(num_swells, swell_num)
                transformed_df[hs_col] = np.round(adjusted_hs, 2)
                transformed_hs_list.append(adjusted_hs)
            else:
                transformed_df[hs_col] = np.round(hs, 2)
            
            transformed_df[peak_pd_col] = transformed_df[peak_pd_col] * self.attenuation
            
            # finalise some rounding
            transformed_df[peak_dir_col] = transformed_df[peak_dir_col].astype(int)
            transformed_df[peak_pd_col] = transformed_df[peak_pd_col].astype(int)
        
        # Combine transformed heights to calculate the combined wave height metric
        if transformed_hs_list:
            
            #sort out the hs total
            hs_combined = np.sqrt(sum([np.power(hs,2) for hs in transformed_hs_list]))
            transformed_df["seasw_ht[m]"] = np.round(hs_combined, 2)            
        
        return transformed_df

    def process_wave_table(self,formatted_table):
        """
        Processes a formatted wave data table from the database and passes to a pandas DataFrame.
        Handles a dynamic number of swells (sw#) in the data.
        """
        lines = formatted_table.split("\n")
        
        # Separate header and data based on the "#" at the start of header lines
        header = [line for line in lines if line.startswith("#")]
        
        #inject some transformed header information if config is valid
        header_text = f", Transform ignored and standard table returned."
        if self.config:
            header_text = f", Transformed with \u03B8 west: {int(self.theta_1)}, \u03B8 east: {int(self.theta_2)}, multi_short: {self.multi_short}, multi_long: {self.multi_long}, attenuation: {self.attenuation}" 
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
        try:
            df.to_csv(self.output_file)
            status = f"Data saved to {self.output_file}"
            
            # Set permissions to 666 (read and write for user, group, and others)
            # os.chmod(self.output_file, 0o666)
            
        except Exception as e:
            status = f"Error saving data: {e}"
        
        return status  