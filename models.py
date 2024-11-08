"""
Name:
    models.py
Classes:
    Site()
    WaveData
"""
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, UniqueConstraint
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

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
