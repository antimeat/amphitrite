import database as db
import os

DIR_PATH = "/cws/op/webapps/er_ml_projects/davink/amphitrite"
CONFIG_FILE = os.path.join(DIR_PATH,'site_config.txt')
        
def initialise_sites_from_config():
    """Read site configuration from a file and add sites to the database."""
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

def dump_sites_table():
    """Prints all records in the sites table."""
    session = db.get_session()
    sites = session.query(db.Site).all()

    for site in sites:
        print(f"Site ID: {site.site_id}, Name: {site.site_name}, Location: {site.table}, Partitions: {site.partitions}")

# setup and itialise the database
if __name__ == "__main__":
    db.init_db()
    initialise_sites_from_config()
    # print("Database initialized and sites populated.")

    dump_sites_table()
    