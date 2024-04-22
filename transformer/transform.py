#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    transformer.py

Author: Daz Vink
"""
import os
import pandas as pd
import numpy as np
from tabulate import tabulate

#local imports relative to amphtirite
import transformer.transformer_configs as configs

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
        swell_height_columns = [col for col in df.columns if 'sw' in col and 'ht[m]' in col and 'seasw' not in col]
        swell_direction_columns = [col for col in df.columns if 'sw' in col and 'dir[degree]' in col and 'seasw' not in col]
        swell_period_columns = [col for col in df.columns if 'sw' in col and 'pd[s]' in col and 'seasw' not in col]
        num_swells = len(swell_height_columns)

        theta1 = str(self.theta_1)
        theta2 = str(self.theta_2)
        
        # Define styles for the HTML table
        styles = [
            dict(selector='table', props=[('margin', '0 auto'), ('border', '1px solid #000')]),
            dict(selector='tr:hover', props=[('background-color', 'lightgrey')]),
            dict(selector='th', props=[('font-size', '110%'), ('text-align', 'center'), ('border', '1px solid #000')]),
            dict(selector='td', props=[('font-size', '100%'), ('text-align', 'center')]),
            dict(selector='caption', props=[('font-size', '150%'), ('font-weight', 'bold'), ('caption-side', 'top')]),
        ]

        # Create subsets for styling specific columns
        groupSubset = ['blank' + ('' if i == 0 else str(i)) for i in range(num_swells + 1)]

        attributes = 'align="center"'
        groupProperties = {'border-right': '1px solid #000', 'border-left': '1px solid #000'}
        caption = 'hs = cos((π / 180) × (dir - {})) × (hs)'.format(theta1 + ' or ' + theta2)

        # Convert columns to numeric and set NaN for errors
        df[swell_height_columns + swell_direction_columns + swell_period_columns] = df[swell_height_columns + swell_direction_columns + swell_period_columns].apply(pd.to_numeric, errors='coerce')

        # Formatting dictionaries for different column types
        formatter = {col: "{:.2f}" for col in swell_height_columns + swell_period_columns}
        formatter.update({col: "{:d}" for col in swell_direction_columns if pd.api.types.is_numeric_dtype(df[col])})

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
        styler = styler.hide_index().render()

        print(styler)

    def transform_to_html_table(self, df):
        
        # Identify swell columns by pattern
        sw_ht_columns = [col for col in df.columns if 'sw' in col and 'ht[m]' in col and 'seasw' not in col]
        sw_dir_columns = [col for col in df.columns if 'sw' in col and 'dir[degree]' in col and 'seasw' not in col]
        sw_pd_columns = [col for col in df.columns if 'sw' in col and 'pd[s]' in col and 'seasw' not in col]
        num_swells = len(sw_ht_columns) 

        # print(f"Number of swells detected: {num_swells}")

        # Selecting relevant columns and renaming
        base_columns = ['time[hrs]', 'time[UTC]', 'time[WST]', 
                        'wind_dir[degrees]', 'wind_spd[kn]', 
                        'sea_ht[m]', 'sea_dir[degree]', 'sea_pd[s]',
                        'seasw_ht[m]', 'seasw_dir[degree]', 'seasw_pd[s]'
                        ]
        columns_to_keep = base_columns + sw_ht_columns + sw_pd_columns + sw_dir_columns
        df = df[columns_to_keep].round(2).replace({0: np.nan}).fillna('')
        # Extracting day and hour from 'time[UTC]' for instance
        
        df['day'] = df['time[UTC]'].apply(lambda x: x.split()[0].split('-')[2])
        df['hour'] = df['time[UTC]'].apply(lambda x: x.split()[1].split(':')[0])
        
        #create some blank columns        
        df['blank'] = ''
        for i in range(1, num_swells + 2):
            df['blank' + str(i)] = ''
    
        #create a list of columns to use and reorder
        columns = ['day','hour','blank',
                    'sea_ht[m]', 'sea_dir[degree]', 'sea_pd[s]', 'blank1',
                    'seasw_ht[m]', 'seasw_dir[degree]', 'seasw_pd[s]'
                    ]
        for i in range(1,num_swells + 1):
            columns.append(f'blank{i+1}')
            columns.append(f'sw{i}_ht[m]')
            columns.append(f'sw{i}_pd[s]')
            columns.append(f'sw{i}_dir[degree]')
        
        df = df[columns]
        
        return df

    def transform_df(self, df):
        """
        Applies transformations to wave height columns based on wave direction,
        updates the individual height columns in the DataFrame with their transformed values,
        and adds a new column for the combined significant wave height.
        """
        transformed_df = df.copy()

        # Identify columns related to wave heights and their corresponding directions
        hs_columns = [col for col in transformed_df.columns if "ht" in col and "seasw" not in col ] 
        transformed_hs_list = []

        for hs_col in hs_columns:
            peak_dir_col = hs_col.split("_")[0] + "_dir[degree]"
            peak_pd_col = hs_col.split("_")[0] + "_pd[s]"
            hs = transformed_df[hs_col]
            peak_dir = transformed_df[peak_dir_col]
            
            # Convert peak direction to radians for trigonometric calculations
            rad_peak_dir = np.radians(peak_dir)

            # Apply cosine adjustments based on direction thresholds
            adjusted_hs = hs.copy()  # Start with original heights
            
            # Applying the bendage rules adjustment for theta_1 and theta_2
            adjusted_hs = np.where(
                ((rad_peak_dir < np.radians(self.theta_1)) & (rad_peak_dir > np.pi)),
                np.cos(rad_peak_dir - np.radians(self.theta_1)) * hs, hs
            )

            adjusted_hs = np.where(
                ((rad_peak_dir > np.radians(self.theta_2)) & (rad_peak_dir < np.pi)),
                np.cos(rad_peak_dir - np.radians(self.theta_2)) * hs, hs
            )

            #magical multiplier, attenuation
            adjusted_hs = adjusted_hs * self.multiplier
            transformed_df[peak_pd_col] = transformed_df[peak_pd_col] * self.attenuation
            
            # Update the DataFrame with transformed wave heights for each column
            transformed_df[hs_col] = np.round(adjusted_hs, 2)
            transformed_hs_list.append(adjusted_hs)
            
            #convert to transformed dir
            peak_dir = np.where(
                ((rad_peak_dir < np.radians(self.theta_1)) & (rad_peak_dir > np.pi)),
                int(self.theta_1), peak_dir
            )
            
            peak_dir = np.where(
                ((rad_peak_dir > np.radians(self.theta_2)) & (rad_peak_dir < np.pi)),
                int(self.theta_2), peak_dir
            )
            transformed_df[peak_dir_col] = peak_dir
            
        # Combine transformed heights to calculate the combined wave height metric
        if transformed_hs_list:
            hs_combined = np.sqrt(sum([np.power(hs,2) for hs in transformed_hs_list]))
            transformed_df["seasw_ht[m]"] = np.round(hs_combined * self.multiplier, 2)

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

