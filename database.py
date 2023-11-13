from sqlalchemy import create_engine, Column, Integer, String, DateTime, ForeignKey, Text
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
    
    def get_partitions(self):
        """Return the partitions as a list of tuples."""
        return json.loads(self.partitions)

    def set_partitions(self, partition_list):
        """Set the partitions from a list of tuples."""
        self.partitions = json.dumps(partition_list)

class WaveData(Base):
    __tablename__ = 'wave_data'
    data_id = Column(Integer, primary_key=True)
    run_time = Column(DateTime)
    formatted_table = Column(Text)
    site_id = Column(Integer, ForeignKey('sites.site_id')) 

    # Relationship to the Site table
    site = relationship("Site", backref="wave_data")
    
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

def add_site(site_name, location, partitions):
    """Add a new site to the database."""
    session = get_session()
    try:
        new_site = Site(site_name=site_name, table=location)
        new_site.set_partitions(partitions)
        session.add(new_site)
        session.commit()
    except IntegrityError:
        print(f"A site with the name '{site_name}' already exists.")
        session.rollback()

def add_wave_data(run_time, location, formatted_table):
    """Add new wave data to the database."""
    session = get_session()
    site_id = get_site_id_by_location(location)

    if site_id is None:
        print(f"No site found for location: {location}")
        return  # or handle the error as needed

    new_wave_data = WaveData(run_time=run_time,site_id=site_id, formatted_table=formatted_table)
    session.add(new_wave_data)
    session.commit()

def get_site_id_by_location(location):
    """Retrieve site_id for a given location."""
    session = get_session()
    site = session.query(Site).filter_by(site_name=location).first()
    if site:
        return site.site_id
    else:
        return None

def get_wave_data_by_site(site_id):
    """Retrieve wave data for a specific site."""
    session = get_session()
    wave_data = session.query(WaveData).filter_by(site_id=site_id).all()
    for data in wave_data:
        print(f"Location: {data.site.location}, Run Time: {data.run_time}, Table: {data.formatted_table}")
    return wave_data
