#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import sys
import datetime
import update_sites_db as update

def save_config(sites,comments,file_name):
    """save and update the config file"""
    file = open(file_name, 'w+')
    file.write("".join(comments))
    file.write("\n\n")
    file.write("".join(sites))
    file.close()

def update_database():
    """update the database using the current config file""" 
    result = update.initialise_sites_from_config()
    return result
    
def main():
    today = datetime.datetime.today()
    sites = sys.argv[1]
    comments = sys.argv[2]
    file_name = sys.argv[3]    
    
    save_config(sites,comments,file_name)
    result = update_database()    
    
if __name__ == "__main__":
    main()    