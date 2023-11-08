#!/cws/anaconda/envs/mlenv/bin/python -W ignore
"""
Name:
    partitionSplitter.py

Classes:
    PartitionSplitter(origin,destination)

Functions:
    
"""
import os
os.environ[ 'NUMBA_CACHE_DIR' ] = '/tmp/'
#os.environ[ 'CONDA_DEFAULT_ENV' ] = 'mlenv'

# import swellSmusher
import partition
import pandas as pd
import sys
import argparse

class PartitionSplitter(object):   
    """Class of methods to breed a mongrel mix of wave spectra, transformations and Ofcast forecasts"""

    def __init__(self,site_name='Woodside - North Rankin 10 days',period_split=9):
        self.partition = partition.Partitions()
        self.table_name = self.get_table_name(site_name)
        self.period_split = period_split
        
    def get_table_name(self,siteName):
        """Get the table name related to the siteName
        Paramaters:
            siteName: ofcast site name
        Returns:
            the auswave table name related to the site
        """
        site_tables = {
            'BHP - Pyrenees': 'Pyranees',
            'Chevron - Gorgon': 'Gorgon',
            'Chevron - Jansz': 'Jansz',
            'Chevron - Wheatstone LNG Plant': 'WheatPlant',
            'Chevron - Wheatstone LNG Plant AFS': 'WheatPlant',
            'Chevron - Wheatstone Platform AFS': 'WheatPlat',
            'Chevron Barrow Island AFS': 'WRB-B',
            'Chevron Barrow Island AFS ML': 'WRB-B',
            'Citic Pacific - Cape Preston Area': 'Cape-Prest',
            'INPEX Ichthys 7 days':'Ichthys',
            'Jadestone Energy - Stag': 'Stag',
            'Jadestone Energy - Montara': 'Montara',
            'Santos - John Brookes 4 days': 'John-Brook',
            'Santos - Reindeer 4 days': 'Reindeer',
            'Santos - Van Gogh 4 days': 'Van-Gogh',
            'Santos - Varanus 4 days': 'Varanus',
            'Santos - Spartan-2 4 days': 'Spartan-2 ',
            'Santos - MS1Standby 4 days': 'MS-1_Stand',
            'Santos - Frigate-1 4 days': 'Frigate-1',
            'Vermilion - Wandoo': 'Wando',
            'Woodside - Balnaves 7 days': 'Balnaves',
            'Woodside - Mermaid Sound 7 days': 'Mermaid-Sn',
            'Woodside - Enfield and Vincent 10 days': 'Enfield',
            'Woodside - North Rankin 10 days': 'NorthRanki',
            'Woodside - Pluto 10 days': 'Pluto',
            'Woodside - Enfield and Vincent 7 days': 'Enfield',
            'Woodside - North Rankin 7 days': 'NorthRanki',
            'Woodside - Pluto 7 days': 'Pluto',
            'Woodside - Scarborough 7 days': 'Scarboroug',
            'WRB-A': 'WRB-A',
            'WRB-B': 'WRB-B',
            'CheJetty': 'CheJetty',
            'Mermaid-Sn': 'Mermaid-Sn',
            'Navaid9': 'Navaid9',
            'Noblige': 'Noblige',
            'Eagle-1': 'Eagle-1',
            'Mermaid-St': 'Mermaid-St',
            'Valaris': 'Valaris' 
        }
    
        return site_tables[siteName]
    
    def get_site_partitions(self,site,*parts):
        """Return the wave spectra partions from site
        Paramaters:
            site (str): Ofcast site name
            parts (list(tuples)): each tuple has the start and end of each partition range
        Returns:
            df (DataFrame): dataframe ready to merge with an Ofcast forecast
         """
        ws = self.partition.multi_parts(*parts)
        #print(self.partition.get_sites_list(ws))
        df = self.partition.get_site(ws,site)

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
    
    def merge_seas(self,ofcast_df,party_df ):
        """Merge seas from Ofcast with first swell partion from auswave partition (short period seas hoepfully!) 
        Paramaters:
            ofcast_df (DataFrame): Ofcast site name            
            party_df (DataFrame): partition dataframe            

        Returns:
            df (DataFrame): with merged seas and first swell partion from auswave partition
         """
    
        ofcast_df = ofcast_df[["seas_ht","seas_pd","seas_dirn"]].copy()
        merged = ofcast_df.merge(party_df,how="inner",left_index=True,right_index=True)
        
        return merged
    
    def smush_seas(self,df):
        """Smush the seas and by default the swell_1 partion from auswave partition (short period seas hoepfully!) 
        Paramaters:
            df (DataFrame): merged datafram from Ofcast seas and auswave swells
        Returns:
            df (DataFrame): with smushed seas and swells unchanged
         """
        df = df.copy()
        seas_df = self.smusher.calculate_simpleSwell(df,seas=True)
        
        return seas_df
    
    def format_swell(self,df):
        """Format the swell partitions by removing seas... by default the swell_1 partion from auswave partition (short period seas hoepfully!) 
        Paramaters:
            df (DataFrame): merged datafram from Ofcast seas and auswave swells
        Returns:
            df (DataFrame): with formated swell dataframe with seas removed
         """
        cols = [
            "seas_ht","seas_pd","seas_dirn",
            "swell_1_ht","swell_1_pd","swell_1_dirn",
            "total_ht","wnd_dir","wnd_spd","station_name","time_local"
        ]      
        
        swell_df = df.copy()
        swell_df.drop(cols,axis=1,inplace=True)
        
        #setup some initial stuff
        df = pd.DataFrame()
        swell_df = swell_df.copy()
        swell_df_index = swell_df.index
        
        #split out the period ranges to a mean value
        df = self.smusher.simplify_periods(swell_df,seas=False)
        
        #mask on the seas/swells
        #df = self.get_maskedSwells(df,ofcast_df,seas)
        
        #tidy up some directions
        df = self.smusher.tidyDirections(df)            
        
        #calculate the power for each masked swell traini
        df = self.smusher.derive_max_power(df)
        
        #tidy up the indexing and time formatting
        df['time_local'] = df.index
        #df = df.set_index('time_local').reindex(index=ofcast_df_index).reset_index()
        df['time_local'] = df['time_local'].dt.strftime('%Y-%m-%d %I %p')

        return df
    
    def merge_seas_swell(self,seas_df,swell_df):
        """Merge sweas and swell dataframes together and finalise for output
        Paramaters:
            seas_df (DataFrame): merged dataframe from Ofcast seas and auswave short period swells
            swell_df (DataFrame): formatted swell dataframe from auswave
        Returns:
            df (DataFrame): merged and formated dataframe ready for output
         """
        seas_df = seas_df.copy()
        swell_df = swell_df.copy()
        seas_df.drop("time_local",axis=1,inplace=True)
        swell_df.drop("time_local",axis=1,inplace=True)
        #print(seas_df)
        #print(swell_df)
        
        swell_seas_df = swell_df.merge(seas_df,how='inner',left_index=True,right_index=True,suffixes=('_swell','_seas'))
        #print(swell_seas_df.head())        
        swell_seas_df = self.smusher.finalFormatting(swell_seas_df)

        return swell_seas_df
            
    
if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    
    parser.add_argument("--site",dest="site_name",nargs="?", default="Woodside - Pluto 10 days",help="the forecast site name from Ofcast",required=False)
    parser.add_argument("--period",dest="period_split",nargs=1,default=9,type=int,help="seas/swell split",required=False)
    
    args = parser.parse_args()
    
    print(f"{args.site_name},{args.period_split}")
    
    parts = [(0.001,args.period_split),(args.period_split,40)]
        
    toolbox = PartitionSplitter(site_name=args.site_name,period_split=args.period_split)        
    print(toolbox.get_table_name(args.site_name))
    
    # ofcast_df = toolbox.get_ofcast_forecast(siteName)
    party_df = toolbox.get_site_partitions(toolbox.get_table_name(args.site_name),*parts)
    # merged = toolbox.merge_seas(ofcast_df,party_df)
    # seas = toolbox.smush_seas(merged)
    # swell = toolbox.format_swell(merged)
    # swell_seas = toolbox.merge_seas_swell(seas,swell)
    
    # # if version != 'debug':
    # #     swell_seas = toolbox.smusher.removeColumns(swell_seas)
    
    # swell_seas['time_local'] = swell_seas.index
    # swell_seas['time_local'] = swell_seas['time_local'].dt.strftime('%Y-%m-%d %I %p')

    # print(toolbox.smusher.outputToBoxes(swell_seas))
    # print(toolbox.smusher.apply_styles(df=swell_seas))    
    ws = toolbox.partition.single_part(*parts)
    #print(self.partition.get_sites_list(ws))
    df = toolbox.partition.get_site(ws,toolbox.get_table_name(args.site_name))

    print(party_df)
    print(df)