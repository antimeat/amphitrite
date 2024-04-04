#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import bs4 as bs
import urllib.request
import ssl
import pandas as pd
import numpy as np
from datetime import datetime,timedelta
import argparse
import os
import transformer_configs as configs

class WaveTable(object):
    '''
    Class for generating modified sigwave/swell tables
    '''
    
    def __init__(self,siteName='Dampier Salt - Cape Cuvier 7 days',tableName='Cape_Cuvier_Offshore', theta_1='260', theta_2='020', multiplier=1, attenuation=1, model='long',thresholds=[0.3,0.2,0.15]):
        self.siteName = siteName
        self.tableName = tableName
        self.theta_1 = int(theta_1)
        self.theta_2 = int(theta_2)
        self.multiplier = float(multiplier)
        self.attenuation = float(attenuation)
        self.model = model
        self.thresholds = thresholds        
        #self.table_url = 'http://aifs-qld.bom.gov.au/local/qld/rfc/pages/marine/waves/auswave.php?state=wa&site={}&model={}'.format(self.tableName, self.model)
        self.table_url = 'https://wa-aifs-local.bom.gov.au/waves/spectra_viewer/auswave_new.php?state=wa&site={}&model={}'.format(self.tableName, self.model)
        self.output_file = os.path.join(configs.BASE_DIR,f"tables/{self.siteName}_data.csv".replace(' ','_').replace('-',''))
                
    def get_siteName(self):
        return self.siteName 
    
    def get_tableName(self):
        return self.tableName 
        
    def get_theta_1(self):
        return self.theta_1 
    
    def get_theta_2(self):
        return self.theta_2 
    
    def get_multiplier(self):
        return self.multiplier 
    
    def get_attenuation(self):
        return self.attenuation 
    
    def get_thresholds(self):
        return self.thresholds

    def get_model(self):
        return self.model

    def get_table_url(self):
        return self.table_url

    def get_output_file(self):
        return self.output_file

    def scrapeWaveTable(self):
        '''
        Scrape the web-based tables 
        '''

        #get all we need
        theta1 = self.get_theta_1()    
        theta2 = self.get_theta_2()
        multiplier = self.get_multiplier()
        attenuation = self.get_attenuation()
        model = self.get_model()
        url = self.get_table_url()
        
        #setup model ranges
        num_swells = 6
        if 'ec' in model:
            num_swells = 4
        
        #beautiful soup for scraping our table url
        context = ssl._create_unverified_context()
        source = urllib.request.urlopen(url, context=context).read()
        #source = urllib.request.urlopen(url).read()
        soup = bs.BeautifulSoup(source,'lxml')

        table = soup.find('table', id='data')
        table_rows = table.find_all('tr')

        tr_head = table_rows[0]
        td_head = tr_head.find_all('tr_head')
        head = [tr.text for tr in td_head]

        rows = []

        for i in range(1, len(table_rows)):
            tr = table_rows[i]
            td = tr.find_all('td')
            row = [tr.text for tr in td]
            rows.append(row)

        df = pd.DataFrame(rows)
        df = df.reset_index(drop=True)
        
        #create the correct about of swells for given model
        columns = ['D','H','Hs','n','x']
        for i in range(1,num_swells + 1):
            columns.append('Hs_sw{}'.format(i))
            columns.append('Tp_sw{}'.format(i))
            columns.append('Dn_sw{}'.format(i))
        
        df.columns = columns

        #print(df)

        for i in range(1, num_swells + 1):

            df['Hs_sw' + str(i)] = np.where(df['Hs_sw' + str(i)] == ' ', np.nan, df['Hs_sw' + str(i)])
            df['Tp_sw' + str(i)] = np.where(df['Tp_sw' + str(i)] == ' ', np.nan, df['Tp_sw' + str(i)])
            df['Dn_sw' + str(i)] = np.where(df['Dn_sw' + str(i)] == ' ', np.nan, df['Dn_sw' + str(i)])

            df['Hs_sw' + str(i)] = pd.to_numeric(df['Hs_sw' + str(i)], errors='coerce')
            df['Tp_sw' + str(i)] = pd.to_numeric(df['Tp_sw' + str(i)], errors='coerce')
            df['Dn_sw' + str(i)] = pd.to_numeric(df['Dn_sw' + str(i)], errors='coerce')

            df['Dn_sw' + str(i)] = df['Dn_sw' + str(i)] - 180
            df['Dn_sw' + str(i)] = df['Dn_sw' + str(i)].apply(lambda x: self.deg(x))

            #apply the magical attenuation!
            df['Tp_sw' + str(i)] = df['Tp_sw' + str(i)].apply(lambda x: x*attenuation)
            
            #apply the magical multiplier!
            df['Hs_sw' + str(i)] = df['Hs_sw' + str(i)].apply(lambda x: x*multiplier)
            
            #theta 1
            df['Hs_sw' + str(i)] = np.where(((df['Dn_sw' + str(i)] < theta1) & (df['Dn_sw' + str(i)] >= 180)), np.cos((np.pi/180)*(df['Dn_sw' + str(i)] - theta1))*df['Hs_sw' + str(i)], df['Hs_sw' + str(i)])  

            #theta 2
            df['Hs_sw' + str(i)] = np.where((df['Dn_sw' + str(i)] > theta2) & (df['Dn_sw' + str(i)] < 180), np.cos((np.pi/180)*(df['Dn_sw' + str(i)] - theta2))*df['Hs_sw' + str(i)], df['Hs_sw' + str(i)])  
            
            # clean up anything that has nan for dir or hs        
            df['Hs_sw' + str(i)] = np.where(df['Hs_sw' + str(i)].isna(), 0, df['Hs_sw' + str(i)])
            df['Hs_sw' + str(i)] = np.where(df['Hs_sw' + str(i)] <= 0, 0, df['Hs_sw' + str(i)])
            df['Hs_sw' + str(i)] = np.where(df['Dn_sw' + str(i)].isna(), 0, df['Hs_sw' + str(i)])
            #df['Tp_sw' + str(i)] = np.where(df['Hs_sw' + str(i)] == 0, 0, df['Tp_sw' + str(i)])

            # this is the anti-jim line        
            #df['Dn_sw' + str(i)] = df['Dn_sw' + str(i)].apply(lambda x: theta if ((x>180)&(x<=theta)) else x )

        #create some blanked columns
        df['blank'] = ''
        for i in range(1, num_swells + 1):
            df['blank' + str(i)] = ''

        #create a list of columns to use
        columns = ['D','H','blank','Hs','n','x']
        for i in range(1,num_swells + 1):
            columns.append('blank{}'.format(i))
            columns.append('Hs_sw{}'.format(i))
            columns.append('Tp_sw{}'.format(i))
            columns.append('Dn_sw{}'.format(i))
        
        #sum of the squares rule over the hs columns
        hs_cols = [col for col in df.columns if 'Hs_sw' in col]
        df['Hs'] = df[hs_cols].apply(np.square,axis=1).sum(axis=1).apply(np.sqrt)
        #df['Hs'] = np.power(np.square(df['Hs_sw1']) + np.square(df['Hs_sw2']) + np.square(df['Hs_sw3']) + np.square(df['Hs_sw4']) + np.square(df['Hs_sw5']) + np.square(df['Hs_sw6']), 0.5)

        df = df[columns]

        df = df.round(2)
        df = df.replace({0:np.nan})
        df = df.fillna('')
        df = df.rename(columns={'D':'day','H':'hour'})
        df = df.drop(columns=['n','x'])

        return df    

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
            thresholds = self.get_thresholds()
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
		
    def printTable(self,df):
        '''
        Print out an nice looking html version of the table
        '''
        
        #get all we need
        theta1 = str(self.get_theta_1())
        theta2 = str(self.get_theta_2())
        #multiplier = self.get_multiplier()
        #attenuation = self.get_attenuation()
                
        styles = [ \
	        dict(selector='table', props=[('margin', '0px auto'), ('border','1px solid #000')]), \
	        dict(selector='tr:hover', props=[('background-color','lightgrey')]), \
	        dict(selector='th', props=[('font-size', '110%'),('text-align', 'center'),('border','1px solid #000')]), \
	        dict(selector='td', props=[('font-size', '100%'),('text-align', 'center')]), \
	        dict(selector='caption', props=[('font-size', '150%'),('font-weight', 'bold'),('caption-side', 'top')]), \
	        ]
		
        hsSubset = ['Hs','Hs_sw1','Hs_sw2','Hs_sw3','Hs_sw4','Hs_sw5','Hs_sw6']
        dnSubset = ['Dn_sw1','Dn_sw2','Dn_sw3','Dn_sw4','Dn_sw5','Dn_sw6']
        tpSubset = ['Tp_sw1','Tp_sw2','Tp_sw3','Tp_sw4','Tp_sw5','Tp_sw6']        
        groupSubset = ['blank','blank1','blank2','blank3','blank4','blank5','blank6']

        attributes = 'align = "center"'
        groupProperties = {'border-right':'1px solid #000','border-left':'1px solid #000'}
        caption = 'hs = cos((&#960 &#8260 180)&#8901(dir - {}))&#8901(hs)'.format(theta1 + ' or ' + theta2)
        
        # Attempt to convert columns intended for float formatting to numeric, handling errors
        for col in df.columns:
            if 'Tp' in col or 'Hs' in col or 'Dn' in col:  # Assuming these should be formatted as floats
                df[col] = pd.to_numeric(df[col], errors='coerce')# Convert to numeric, set errors to NaN
        df[dnSubset] = df[dnSubset].astype('Int64')  # Convert Dn columns to integers

        # Your existing formatting setup...
        tpFormatter = {col: "{:.2f}" for col in df.columns if 'Tp' in col}
        hsFormatter = {col: "{:.2f}" for col in df.columns if 'Hs' in col}
        dnFormatter = {col: "{:d}" for col in df.columns if 'Dn' in col and pd.api.types.is_numeric_dtype(df[col])}

        formatter = {**tpFormatter, **hsFormatter, **dnFormatter}
        
        styler = df.style
        styler = styler.applymap(self.highlightHsColor, subset=hsSubset)
        styler = styler.applymap(self.highlightDnColor, subset=dnSubset)
        styler = styler.apply(self.highlightTimeColor,axis=1)
        styler = styler.set_table_styles(styles)
        styler = styler.set_table_attributes(attributes)
        #styler = styler.set_caption(caption)
        styler = styler.set_properties(**groupProperties,subset=groupSubset)
        styler = styler.format(formatter, na_rep="")
        styler = styler.hide_index().render()

        print(styler)

    def save_to_file(self,df):
        '''
        Save the dataframe to a csv file for use as modified sigwave data in vulture
        '''
        
        df = df.copy()
        
        #get all we need
        siteName = self.get_siteName()    
        model = self.get_model()
        output_file = self.get_output_file()
        
        #work out what the first day and month are
        date_now = datetime.utcnow()
        year = date_now.year
        month = date_now.month
        day = date_now.day
        
        #clean up any wierd hours printed as '`0'
        df['hour'] = df['hour'].replace('`0','0',regex=True)
         
        #model start day and hour might be from previous day
        start_day = int(df.iloc[0]['day'])
        start_hour = int(df.iloc[0]['hour'])
        
        if start_day != day:
            yesterday = date_now - timedelta(days=1)
            month = yesterday.month
            year = yesterday.year
            day = yesterday.day
            
        #create a new date from day and hour from model run    
        start_date = datetime(year,month,day,start_hour)
        
        #if model is short then increment hourly else 3 hourly
        inc = 3
        if model == 'short':
            inc = 1
        
        #loop through each row and work out the datetime
        for i,row in df.iterrows():
            df.loc[i,'time_utc'] = start_date + timedelta(hours = i*inc)
            df.loc[i,'time'] = start_date + timedelta(hours = i*inc)
        
        #convert to local
        #df['time'] = df['time_utc'].dt.tz_localize('utc').dt.tz_convert('Australia/Perth')
        #df['time'] = df['time'].apply(lambda x: x.replace(tzinfo=None))
            
        #prepare and dump to csv
        df = df.rename(columns={'Hs':'total_ht'})
        df['field'] = 'total_ht'
        df['name'] = siteName
        
        #use a context manager to open the file correctly
        with open(output_file, "w") as reference:
            df[['name','time','field','total_ht']].to_csv(output_file,header=['name','time','field','value'])
        
        return df

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
    args = parse_arguments()
    
    # Then pass those arguments to your class initialization
    wave_table = WaveTable(
        siteName=args.siteName,
        tableName=args.tableName,
        theta_1=args.theta_1,
        theta_2=args.theta_2,
        multiplier=args.multiplier,
        attenuation=args.attenuation,
        model=args.model,
        thresholds=args.thresholds
    )

    df = wave_table.scrapeWaveTable()
    wave_table.save_to_file(df)
    
    #print(df.columns)
    #print(df[['day','hour','time']])

    wave_table.printTable(df)

if __name__ == '__main__':
    main() 
    
