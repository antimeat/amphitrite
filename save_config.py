#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import sys
import datetime

if __name__ == "__main__":
    today = datetime.datetime.today()
    sites = sys.argv[1]
    comments = sys.argv[2]
    file_name = sys.argv[3]    
    
    file = open(file_name, 'w+')
    file.write("".join(comments))
    file.write("\n\n")
    file.write("".join(sites))
    file.close()
