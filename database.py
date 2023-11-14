from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.exc import IntegrityError

import os
import json

Base = declarative_base()

class Site(Base):
    __tablename__ = 'sites'
    site_id = Column(Integer, primary_key=True)
    site_name = Column(String, unique=True)  # Adding a unique constraint
    table = Column(String)  
    partitions = Column(Text)  # Storing partition data as a JSON string

    def get_partitions(self):
        """Return the partitions as a list of tuples."""
        return json.loads(self.partitions)

    def set_partitions(self, partition_list):
        """Set the partitions from a list of tuples."""
        self.partitions = json.dumps(partition_list)

    def __str__(self):
        """Return a simple string representation of the Site object."""
        return f"Site(id={self.site_id}, name='{self.site_name}', table='{self.table}')"

    def to_json(self):
        """Return a JSON-like string representation of the Site object."""
        return {
            "site_name": self.site_name,
            "table": self.table,
            "partitions": self.get_partitions()
        }

class WaveData(Base):
    __tablename__ = 'wave_data'
    data_id = Column(Integer, primary_key=True)
    run_time = Column(DateTime)
    formatted_table = Column(Text)
    site_id = Column(Integer, ForeignKey('sites.site_id'))

    # Relationship to the Site table
    site = relationship("Site", backref="wave_data")

    # Unique constraint on run_time and site_id
    __table_args__ = (UniqueConstraint('run_time', 'site_id', name='_run_time_site_id_uc'),)

    def __str__(self):
        """Return a simple string representation of the formatted_table."""
        return self.formatted_table

    def to_json(self):
        """Return a JSON-like string representation of the WaveData object."""
        wave_data_dict = {
            "data_id": self.data_id,
            "run_time": self.run_time.isoformat() if self.run_time else None,
            "formatted_table": self.formatted_table,
            "site_id": self.site_id
        }
        # Optionally include site details if needed
        if self.site:
            wave_data_dict["site_details"] = str(self.site)  # or self.site.to_json()

        return wave_data_dict

# Database setup
DATABASE_URL = "sqlite:///wave_data.db" 

engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)

def init_db():
    """Initialize the database, create tables."""
    Base.metadata.create_all(engine)

def get_session():
    """Get a new session."""
    return Session()
    
def site_runtime_exists(site_name, run_time):
    """return true if site and runtime is in the database"""
    session = get_session()
    try:
        site = session.query(Site).filter(site_name=site_name).first()
        wave_table = session.query(WaveData).filter(site_id=site.site_id, run_time=run_time).first()
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
        sites = session.query(Site).all()
        site_names = [site.site_name for site in sites] 

        return {"success": False, "message": "All sites returned", "data":site_names}
    except Exception as e:
        return {"success": False, "message": str(e)}
    
def add_site_to_db(site_name, location, partition_list):
    """Add a new site to the database."""
    session = get_session()
    try:
        new_site = Site(site_name=site_name, location=location)
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

def update_site_to_db( site_name, table, partition_list):
    """Update a site's details in the database."""
    session = get_session()
    try:
        site = session.query(Site).filter_by(site_name=site_name).first()
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

def get_site_partitions_from_db( site_name):
    """Retrieve the partitions for a given site."""
    session = get_session()
    try:
        site = session.query(Site).filter_by(site_name=site_name).first()
        if site:
            return {"success": True, "message": f"'{site_name} data found", "data": site.get_partitions()}
        else:
            return {"success": False, "message": f"Site with name '{site_name}' not found"}
    except Exception as e:
        # Log the exception as needed
        return {"success": False, "message": str(e)}
    finally:
        session.close()

def add_wavetable_to_db( site_name, run_time, table_output):
    """Add wave data to the database or return existing data if duplicate."""
    session = get_session()
    
    try:
        site = session.query(Site).filter_by(site_name=site_name).first()
        if not site:
            return {"success": False, "message": "Site not found", "data": None}

        # Check for existing wave data entry
        existing_wave_data = session.query(WaveData).filter_by(
            run_time=run_time, 
            site_id=site.site_id
        ).first()

        if existing_wave_data:
            return {"success": True, "message": "Duplicate wave data found", "data": existing_wave_data.formatted_table}

        # Add new wave data entry
        new_wave_table = WaveData(run_time=run_time, formatted_table=table_output, site_id=site.site_id)
        session.add(new_wave_table)
        session.commit()
        return {"success": True, "message": "Wave data added successfully", "data": new_wave_table.formatted_table}
    
    except Exception as e:
        session.rollback()
        # Log the exception as needed
        return {"success": False, "message": str(e), "data": None}
    finally:
        session.close()

def get_wavetable_from_db( site_name, run_time=None):
    """Return the wavetable data for a site at a given or most recent runtime."""
    session = get_session()
    try:
        site = session.query(Site).filter_by(site_name=site_name).first()
        if not site:
            return {"success": False, "message": "Site not found", "data": None}

        query = session.query(WaveData).filter_by(site_id=site.site_id)
        if run_time:
            query = query.filter_by(run_time=run_time)
        else:
            query = query.order_by(WaveData.run_time.desc())

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
        site = session.query(Site).filter_by(site_name=site_name).first()
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
