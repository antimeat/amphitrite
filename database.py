"""
Name:
    database.py
Functions:
    single_part(*parts)
    multi_parts(*parts)
    mermaidSound()
"""
from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
import os
import json
from tabulate import tabulate
import pandas as pd
import argparse
import datetime

# Local imports
import models

# Database setup
DATABASE_URL = "sqlite:///wave_data.db" 
Base = declarative_base()

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database, create tables."""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new session."""
    return Session()

def add_site(site_name, location, partitions):
    """Add a new site to the database or update it if it already exists."""
    session = get_session()
    try:
        existing_site = session.query(models.Site).filter(models.Site.site_name == site_name).one_or_none()
        
        if existing_site:
            # Update existing site
            existing_site.table = location
            existing_site.set_partitions(partitions)
            print(f"Updated site: '{site_name}'")
        else:
            # Add new site
            new_site = models.Site(site_name=site_name, table=location)
            new_site.set_partitions(partitions)
            session.add(new_site)
            print(f"Added new site: '{site_name}'")
        
        session.commit()
    except Exception as e:
        print(f"Error processing site '{site_name}': {e}")
        session.rollback()
    
def site_runtime_exists(site_name, run_time):
    """return true if site and runtime is in the database"""
    session = get_session()
    try:
        site = session.query(models.Site).filter(models.Sites.site_name == site_name).first()
        wave_table = session.query(models.WaveData).filter(models.WaveData.site_id == site.site_id, models.WaveData.run_time == run_time).first()
        if wave_table:
            return {"success": True, "message": f"{site.site_name} and {run_time} already exist"}
        else:
            return {"success": False, "message": f"{site.site_name} and {run_time} dont exist"}
        
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_all_sites():
    """return all sites"""
    session = get_session()
    try:
        sites = session.query(models.Site).all()
        site_names = [site.site_name for site in sites]
        tables = [site.table for site in sites]
        partitions = [site.get_partitions() for site in sites]

        return {"success": False, "message": "All sites returned", "data":[site_names,tables,partitions]}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def get_all_wave_data():
    """return all wave data"""
    session = get_session()
    try:
        sites = session.query(models.Site).all()
        site_names = [site.site_name for site in sites]
        tables = [site.table for site in sites]
        partitions = [site.get_partitions() for site in sites]
        run_times = [session.query(models.WaveData.run_time).filter(models.WaveData.site_id == site.site_id).order_by(desc(models.WaveData.run_time)).first() for site in sites]
        # run_times = [rt.strftime("%Y/%m/%d %H") if rt is not None else None for rt in run_times]        
        return {"success": True, "message": "All wave data returned", "data":[site_names,tables,partitions,run_times]}
    except Exception as e:
        return {"success": False, "message": str(e)}

def add_site_to_db(site_name, location, partition_list):
    """Add a new site to the database."""
    session = get_session()
    try:
        new_site = models.Site(site_name=site_name, location=location)
        new_site.set_partitions(partition_list)
        session.add(new_site)
        session.commit()
        return {"success": True, "message": "Site added successfully"}
    except Exception as e:
        session.rollback()
        # Log the exception as needed
        return {"success": False, "message": str(e)}
    finally:
        session.close()

def update_site_to_db(site_name, table, partition_list):
    """Update a site's details in the database."""
    session = get_session()
    try:
        site = session.query(models.Site).filter_by(models.Site.site_name == site_name).first()
        if site:
            site.table = table
            site.set_partitions(partition_list)
            session.commit()
            return {"success": True, "message": "Site updated successfully"}
        else:
            return {"success": False, "message": "Site not found"}
    except Exception as e:
        session.rollback()
        # Log the exception as needed
        return {"success": False, "message": str(e)}
    finally:
        session.close()

def get_site_partitions_from_db(site_name):
    """Retrieve the partitions for a given site."""
    session = get_session()
    try:
        site = session.query(models.Site).filter_by(models.Site.site_name == site_name).first()
        if site:
            return {"success": True, "message": f"'{site_name} data found", "data": site.get_partitions()}
        else:
            return {"success": False, "message": f"Site with name '{site_name}' not found"}
    except Exception as e:
        # Log the exception as needed
        return {"success": False, "message": str(e)}
    finally:
        session.close()

def add_wavetable_to_db(site_name, run_time, table_output):
    """Add wave data to the database or return existing data if duplicate."""
    session = get_session()
    
    try:
        site = session.query(models.Site).filter_by(models.Site.site_name == site_name).first()
        if not site:
            return {"success": False, "message": "Site not found", "data": None}

        # Check for existing wave data entry
        existing_wave_data = session.query(models.WaveData).filter_by(
            models.WaveData.run_time == run_time, 
            models.WaveData.site_id == site.site_id
        ).first()

        if existing_wave_data:
            existing_wave_data.formatted_table = table_output
            session.commit()
            return {"success": True, "message": "Duplicate wave data found, site updated", "data": existing_wave_data.formatted_table}

        # Add new wave data entry
        new_wave_table = models.WaveData(run_time=run_time, formatted_table=table_output, site_id=site.site_id)
        session.add(new_wave_table)
        session.commit()
        return {"success": True, "message": "Wave data added successfully", "data": new_wave_table.formatted_table}
    
    except Exception as e:
        session.rollback()
        # Log the exception as needed
        return {"success": False, "message": str(e), "data": None}
    finally:
        session.close()

def get_wavetable_from_db(site_name, run_time=None):
    """Return the wavetable data for a site at a given or most recent runtime."""
    session = get_session()
    try:
        site = session.query(models.Site).filter_by(models.Site.site_name == site_name).first()
        #lets see if there is a table_name rather than a site_name that exists :-)
        if not site:
            site = session.query(models.Site).filter_by(models.Site.table == site_name).first()
            if not site:
                return {"success": False, "message": "Site/table not found", "data": None}                
            
        query = session.query(models.WaveData).filter_by(models.WaveData.site_id == site.site_id)
        if run_time:
            run_time_dt = datetime.datetime.strptime(run_time,"%Y%m%d%H")
            query = query.filter_by(models.WaveData.run_time == run_time_dt)
        else:
            query = query.order_by(models.WaveData.run_time.desc())

        wave_table = query.first()
        if wave_table:
            return {"success": True, "message": "Wave data retrieved successfully", "data": wave_table.formatted_table}
        else:
            return {"success": False, "message": "Wave data not found", "data": None}

    except Exception as e:
        session.rollback()
        # Log the exception as needed
        return {"success": False, "message": str(e)}
    finally:
        session.close()

def update_site_to_db( site_name, table, partition_list):
    """Update a site's details in the database."""
    session = get_session()
    try:
        site = session.query(models.Site).filter_by(models.Site.site_name == site_name).first()
        if site:
            site.table = table
            site.set_partitions(partition_list)
            session.commit()
            return site
        return None
    except Exception as e:
        # Handle or log the exception as needed
        session.rollback()
        raise e
    finally:
        session.close()

def delete_oldest_wave_data(max_size_gb=10):
    """Delete the oldest WaveData entries if the database exceeds a certain size."""
    db_size_gb = get_db_file_size()
    
    if db_size_gb <= max_size_gb:
        return {"success": True, "message": "Database size is within limits"}

    session = get_session()
    
    try:
        while get_db_file_size() > max_size_gb:
            oldest_data = session.query(models.WaveData).order_by(models.WaveData.run_time).first()
            if not oldest_data:
                break  # No more data to delete

            session.delete(oldest_data)
            session.commit()
        
        return {"success": True, "message": "Old entries deleted to reduce database size"}

    except Exception as e:
        session.rollback()
        return {"success": False, "message": str(e)}
    finally:
        session.close()

def get_db_file_size():
    """Get the size of the database file in gigabytes."""
    # Assumes SQLite; adjust for other DBs
    path = DATABASE_URL.split("///")[1]  
    return os.path.getsize(path) / (1024 ** 3)  # Convert bytes to GB

def get_all_run_times():
    """Return a list of all run_time values from the wave_data table."""
    session = get_session()
    try:
        # Query to get all run_time values from WaveData table
        run_times = session.query(models.WaveData.run_time).all()
        
        # Extract run_time values from the query result
        run_times_list = [run_time[0].strftime("%Y/%m/%d %H") for run_time in run_times]
        unique_run_times = set(run_times_list)

        return {"success": True, "message": "Run times retrieved successfully", "data": list(unique_run_times)}
    except Exception as e:
        return {"success": False, "message": str(e)}
    finally:
        session.close()

def console_output():
    """Format the state of the database for console output"""       
    #stie data from Sites
    site_data = get_all_sites()["data"]
    sites = site_data[0]
    tables = site_data[1]
    partitions = site_data[2]

    df_sites = pd.DataFrame({
        "sites": sites,
        "table": tables,
        "partitions": partitions
    })

    sites_table_output = tabulate(df_sites,headers="keys",tablefmt="psql", showindex=False)
    print(sites_table_output)

    #run_times from WaveData
    run_times = get_all_run_times()["data"]
    df_wave_data = pd.DataFrame({"run_times":run_times})
    run_time_table_output = tabulate(df_wave_data,headers="keys",tablefmt="psql", showindex=False)
    print(run_time_table_output)

def api_output():
    """Format the state of the database for api output"""       
    #stie data from Sites
    site_data = get_all_sites()["data"]
    sites = site_data[0]
    tables = site_data[1]
    partitions = site_data[2]
    
    df_sites = pd.DataFrame({
        "sites": sites,
        "table": tables,
        "partitions": partitions,
    })

    df_sites_sorted = df_sites.sort_values(by='sites')
    sites_table_output = tabulate(df_sites_sorted,headers="keys",tablefmt="html", showindex=False)
    
    run_times = get_all_run_times()["data"]
    df_wave_data = pd.DataFrame({"run_times":run_times})
    df_wave_data_sorted = df_wave_data.sort_values(by="run_times", ascending=False)

    run_time_table_output = tabulate(df_wave_data_sorted,headers="keys",tablefmt="html", showindex=False)
    
    return sites_table_output, run_time_table_output
    
def cleanup_old_run_times(days=10):
    """Delete WaveData records older than a specified number of days."""
    session = get_session()
    try:
        # Calculate the cutoff date
        cutoff_date = datetime.datetime.now() - datetime.timedelta(days=days)

        # Query and delete records older than the cutoff date
        old_records = session.query(models.WaveData).filter(models.WaveData.run_time < cutoff_date).all()
        for record in old_records:
            session.delete(record)

        session.commit()
        print(f"Deleted {len(old_records)} old records.")

    except Exception as e:
        session.rollback()
        print(f"Error during cleanup: {e}")

    finally:
        session.close()

if __name__ == "__main__":
    # Create the parser
    parser = argparse.ArgumentParser(description='Process some integers.')

    # Add arguments
    parser.add_argument('--api', action='store_true', help='Output for API')
    parser.add_argument('--console', action='store_true', help='Output for console')

    # Parse arguments
    args = parser.parse_args()

    if args.api:
        api_output()
    else:
        console_output()
    
    #tidy up the old records
    cleanup_old_run_times()