#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import pandas as pd
import numpy as np

class SwellSmusher():
    '''
    Class for simplifying swells
    '''
    
    def __init__(self,siteName='Woodside_-_North_Rankin_10_days',periodSplit=9):
        self.siteName = siteName
        self.periodSplit = periodSplit        
        self.num_swells = None
                
    def get_num_swells(self):
        return self.num_swells 
    
    def get_periodSplit(self):
        return self.periodSplit 
    
    def get_siteName(self):
        return self.siteName 
    
    def set_num_swells(self,num_swells):
        self.num_swells = num_swells        
    
    def get_issue_time(self):
        #return self.issue_time.strftime('%Y/%m/%d %H:%M')
        return self.issue_time
        
    def simplify_periods(self,df):
        '''
        return a dataframe with period ranges simplified into a mean value of pd_val
        '''
        df = df.copy()
        pd_cols = []
        
        try:
            # get all the period columns and set the number of swells
            pd_cols = [col for col in df.columns if '_pd' in col]
            self.set_num_swells(len(pd_cols))
               
            # calculate the mean period for period ranges
            for i,col in enumerate(pd_cols):
                df[col] = df[col].astype(str)
                df[col] = df[col].apply(lambda x: "{}/{}".format(x,x) if ("/" not in x) else x)
                
                df[['{}_0'.format(col),'{}_1'.format(col)]] = df[col].str.split('/',n=2,expand=True)
                
                df['{}_0'.format(col)] = df['{}_0'.format(col)].fillna(df['{}'.format(col)])
                df['{}_1'.format(col)] = df['{}_1'.format(col)].fillna(df['{}'.format(col)])
                
                #df['{}_1'.format(col)] = df[col].apply(lambda x: x.split('/')[1] if not x.split('/') else x.split('/')[0])
                #df['{}_0'.format(col)] = df[col].apply(lambda x: x.split('/')[0])
                df['{}_0'.format(col)] = pd.to_numeric(df['{}_0'.format(col)],errors='coerce')
                df['{}_1'.format(col)] = pd.to_numeric(df['{}_1'.format(col)],errors='coerce')
                df['{}_val'.format(col)] = (df['{}_0'.format(col)] + df['{}_1'.format(col)]) / 2.0
                
            # get rid of useless columns
            df = df.drop(df.filter(regex='pd_0').columns, axis=1)
            df = df.drop(df.filter(regex='pd_1').columns, axis=1)
            
        except Exception as e:
            print('''<html>
                        <body> 
                            Cannot get a full set of data with dir and period. Error: {}\n
                            {}
                        </body>
                     </html>'''.format(e)) #,df.to_html()))
            exit(1)
        
        #print('\n'.join(df.columns))
        #print(df.head(50))
        #exit()
        return df    
    
    def get_maskedSwells(self,df,ofcast_df,seas):
        '''
        get a masked dataframe that is split on the seas/swell split
        '''
        df = df.copy()
        original_df = ofcast_df.copy()
        
        #original_df = self.get_archived_forecast()[0]
        
        # get all the period columns and set the number of swells
        pd_val_cols = [col for col in df.columns if '_pd_val' in col]
        
        #rename seas to swell_n+1 where n is the last swell 
        if seas:
            last_swell_num = int(pd_val_cols[0].split('_')[1]) + 1
            
            df.rename(columns = {
                'seas_pd_val':'swell_{}_pd_val'.format(last_swell_num),
                'seas_dir':'swell_{}_dir'.format(last_swell_num),
                'seas_pd':'swell_{}_pd'.format(last_swell_num),
                'seas_ht':'swell_{}_ht'.format(last_swell_num)
            },inplace=True)
            
            original_df.rename(columns = {
                'seas_pd_val':'swell_{}_pd_val'.format(last_swell_num),
                'seas_dir':'swell_{}_dir'.format(last_swell_num),
                'seas_pd':'swell_{}_pd'.format(last_swell_num),
                'seas_ht':'swell_{}_ht'.format(last_swell_num)
            },inplace=True)        
        
            #re-evaluate the columns
            pd_val_cols = [col for col in df.columns if '_pd_val' in col]
            
        # split above or blelow seas/swell period
        if seas:
            df = df[df[pd_val_cols] <= self.get_periodSplit()]            
        else: 
            df = df[df[pd_val_cols] > self.get_periodSplit()]
        
        #get rid of swells with all NaN
        df.dropna(axis=1,how='all',inplace=True)    
        
        #work out which swells we have/need
        pd_val_cols = [col for col in df.columns if '_pd_val' in col]
        df_swell_nums = ['{}_{}'.format(n.split('_')[0],n.split('_')[1]) for n in df.columns if n.split('_')[1] in n]
        orig_cols = [col for col in original_df.columns]
        df_swell_cols = [col for col in orig_cols if any(n for n in df_swell_nums if n in col)] 
        
        #reorder the cols: god what a mess! there must be a better way!!!
        dir_swell_cols = df_swell_cols[0::3]
        ht_swell_cols = df_swell_cols[1::3]
        pd_swell_cols = df_swell_cols[2::3]
        
        df_swell_cols = []
        for i in range(0,len(dir_swell_cols)):
            df_swell_cols.append(dir_swell_cols[i])
            df_swell_cols.append(pd_swell_cols[i])
            df_swell_cols.append(ht_swell_cols[i])
        
        #merge the pd_val columns back into the dataframe
        df = original_df[df_swell_cols].merge(df[pd_val_cols],how='inner',left_index=True,right_index=True)
        
        #if pd_val == nan then we want that filtered out
        for n in df_swell_nums:
            df['{}_dir'.format(n)] = df['{}_dir'.format(n)].mask(df['{}_pd_val'.format(n)].isnull(),np.nan)
            df['{}_pd'.format(n)] = df['{}_pd_val'.format(n)].mask(df['{}_pd_val'.format(n)].isnull(),np.nan)
            df['{}_ht'.format(n)] = df['{}_ht'.format(n)].mask(df['{}_pd_val'.format(n)].isnull(),np.nan)
            
        #print(df_swell_cols)
        #print(df.head(20))    
        #print(df.tail(10))    
        
        return df
        
    def derive_max_power(self,df):
        '''
        calculate the power and derive the maximums
        '''
        df = df.copy()
        
        pd_val_cols = [col for col in df.columns if '_pd_val' in col]
        df_swell_nums = ['{}_{}'.format(n.split('_')[0],n.split('_')[1]) for n in pd_val_cols]
        
        # generate some power
        for n in df_swell_nums:
            df['{}_power'.format(n)] = df['{}_ht'.format(n)].fillna(0).pow(2) * (df['{}_pd_val'.format(n)]).round(3)
        
        #setup some initial values
        df['peak_dir'] = np.nan
        df['peak_pd'] = np.nan
        df['peak_ht'] = np.nan
        
        #calculate the new peak power across each swell 
        df['peak_power'] = df[['{}_power'.format(n) for n in df_swell_nums]].max(axis=1)    
            
        # calculate power and peak power/dir/periods
        for n in df_swell_nums:
            
            #work out the peak period,dir and power if we have more than 1 swell train
            df['peak_ht'] = df['peak_ht'].mask(df['{}_power'.format(n)] >= df['peak_power'],df['{}_ht'.format(n)])
            df['peak_pd'] = df['peak_pd'].mask(df['{}_power'.format(n)] >= df['peak_power'],df['{}_pd_val'.format(n)]).apply(np.round).astype("Int64")
            df['peak_dir'] = df['peak_dir'].mask(df['{}_power'.format(n)] >= df['peak_power'],df['{}_dir'.format(n)])
            
        
        #tidy up unwanted columns and missing data    
        #df.fillna('',inplace=True)
        #df.replace(0,'',inplace=True)
        
        return df    
        
    def tidyDirections(self,df):
        '''
        fix some other ungly things here too
        '''
        
        df = df.copy()
        df_swell_nums = ['{}_{}'.format(n.split('_')[0],n.split('_')[1]) for n in df.columns if n.split('_')[1] in n]
        
        #set 0 to 360
        for n in np.unique(df_swell_nums):
            df['{}_dir'.format(n)] = df['{}_dir'.format(n)].replace(0,360)
            
        return df    
    
    def calculate_simpleSwell(self,ofcast_df,seas):
        '''
        test stub for new function to do main work
        '''
        
        #setup some initial stuff
        df = pd.DataFrame()
        ofcast_df = ofcast_df.copy()
        ofcast_df_index = ofcast_df.index
        
        #ofcast_df = pd.DataFrame()
        #ofcast_df_index = pd.DataFrame()
        
        #get the ofcast forecast    
        #ofcast_df = self.get_archived_forecast()[0]
        #ofcast_df_index = self.get_archived_forecast()[1]
                
        #split out the period ranges to a mean value
        df = self.simplify_periods(ofcast_df)
        
        #mask on the seas/swells
        df = self.get_maskedSwells(df,ofcast_df,seas)
        
        #tidy up some directions
        df = self.tidyDirections(df)            
        
        #calculate the power for each masked swell traini
        df = self.derive_max_power(df)
        
        #tidy up the indexing and time formatting
        df['time_local'] = df.index
        #df = df.set_index('time_local').reindex(index=ofcast_df_index).reset_index()
        df['time_local'] = df['time_local'].dt.strftime('%Y-%m-%d %I %p')

        return df
        
    def removeColumns(self,df):
        '''
        Return a dataframe with useless columns removed
        '''
        df = df.copy()
        
        #drop power cols
        df = df.drop(df.filter(regex='power').columns, axis=1)
        
        #format the cols for display in the dataframe
        cols = []
        df_swell_nums = ['{}_{}'.format(n.split('_')[0],n.split('_')[1]) for n in df.columns if (("swell" in n) and ("peak" not in n))]
        for n in list(dict.fromkeys(df_swell_nums)):
            cols.append('{}_ht'.format(n))
            cols.append('{}_pd'.format(n))
            cols.append('{}_dir'.format(n))
        
        cols.append('peak_ht_seas')
        cols.append('peak_pd_seas')
        cols.append('peak_dir_seas')
        cols.append('peak_ht_swell')
        cols.append('peak_pd_swell')
        cols.append('peak_dir_swell')
        cols.append('total_hs')        
        
        return df[cols]
        
    def finalFormatting(self,df):
        '''
        through in an extra column with all the energy combined
        '''
        df = df.copy()
        df.rename(columns={"peak_ht":"seas_ht[m]","peak_dir":"seas_dir[degrees]","peak_pd":"seas_pd[s]"},inplace=True)
        df = df[["seas_ht[m]","seas_pd[s]","seas_dir[degrees]"]]
        
        return df
                        
if __name__ == '__main__':
    
    simplified = SwellSmusher()