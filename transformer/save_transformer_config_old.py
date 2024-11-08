#!/cws/anaconda/envs/mlenv/bin/python -W ignore

import sys

def save_config(sites,comments,file_name):
    """save and update the config file"""
    try:
        file = open(file_name, 'w+')
        file.write("".join(comments))
        file.write("\n\n")
        file.write("".join(sites))
        file.close()
        return "Config file updated successfully"
    except Exception as e:
        return "Error updating config file: {}".format(e)
def main():
    sites = sys.argv[1]
    comments = sys.argv[2]
    file_name = sys.argv[3]    
    
    result = save_config(sites,comments,file_name)
    print(result)
    
if __name__ == "__main__":
    main()    