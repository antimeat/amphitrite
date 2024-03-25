import database as db
import models
import os
import argparse

DIR_PATH = "/cws/op/webapps/er_ml_projects/davink/amphitrite_dev/amphitrite"
CONFIG_FILE = os.path.join(DIR_PATH,'site_config.txt')
        
def initialise_sites_from_config():
    """Read site configuration from a file and add sites to the database."""
    try:
        with open(CONFIG_FILE, 'r') as file:
            for line in file:
                # Skip comments and empty lines
                if line.startswith('#') or not line.strip():
                    continue

                parts = line.strip().split(', ')
                if len(parts) < 3:
                    continue  # Skip malformed lines

                site_name = parts[0]
                location = parts[1]
                partition_ranges = [tuple(map(float, part.split('-'))) for part in parts[2:]]

                db.add_site(site_name, location, partition_ranges)
        return {"Config updated to database!"}
    
    except Exception as e:
        return {f"Failed to update database: {e}"}
        
def dump_sites_table():
    """Prints all records in the sites table."""
    session = db.get_session()
    sites = session.query(models.Site).all()

    for site in sites:
        print(f"Site ID: {site.site_id}, Name: {site.site_name}, Location: {site.table}, Partitions: {site.partitions}")

def main():
    """Parse either --init or --update"""
    parser = argparse.ArgumentParser(description="Initialise or update the database.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--init', action='store_true', help="Initialise the database.")
    group.add_argument('--update', action='store_true', help="Update the existing database.")

    args = parser.parse_args()

    if args.init:
        db.init_db()
        initialise_sites_from_config()
        print("Database initialized and sites populated.")
    elif args.update:
        initialise_sites_from_config()
        print("Database updated.")

    dump_sites_table()
    
if __name__ == "__main__":
    main()