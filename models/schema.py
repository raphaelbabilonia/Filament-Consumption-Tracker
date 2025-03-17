"""
Database schema for the Filament Consumption Tracker.
"""
from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import datetime
import os

Base = declarative_base()

class Filament(Base):
    """Table for storing filament inventory information."""
    __tablename__ = 'filaments'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False)  # PLA, ABS, etc.
    color = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)
    quantity_remaining = Column(Float, nullable=False)  # in grams
    spool_weight = Column(Float, nullable=False)  # total spool weight in grams
    price = Column(Float)  # price per spool
    purchase_date = Column(DateTime, default=datetime.datetime.now)
    
    # Relationship with print jobs - specify which foreign key to use
    print_jobs = relationship("PrintJob", 
                              foreign_keys="PrintJob.filament_id", 
                              back_populates="filament")
    
    # Relationships for secondary filaments (print jobs where this filament is used as secondary)
    secondary_print_jobs_2 = relationship("PrintJob", 
                                         foreign_keys="PrintJob.filament_id_2",
                                         overlaps="print_jobs",
                                         back_populates="filament_2")
    
    secondary_print_jobs_3 = relationship("PrintJob", 
                                         foreign_keys="PrintJob.filament_id_3",
                                         overlaps="print_jobs",
                                         back_populates="filament_3")
    
    secondary_print_jobs_4 = relationship("PrintJob", 
                                         foreign_keys="PrintJob.filament_id_4",
                                         overlaps="print_jobs",
                                         back_populates="filament_4")
    
    def __repr__(self):
        return f"<Filament(type='{self.type}', color='{self.color}', brand='{self.brand}')>"


class Printer(Base):
    """Table for storing printer information."""
    __tablename__ = 'printers'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    model = Column(String(50))
    purchase_date = Column(DateTime, default=datetime.datetime.now)
    notes = Column(Text)
    power_consumption = Column(Float, default=0.0)  # Average power consumption in kWh
    
    # Relationship with print jobs
    print_jobs = relationship("PrintJob", back_populates="printer")
    
    # Relationship with printer components
    components = relationship("PrinterComponent", back_populates="printer")
    
    def __repr__(self):
        return f"<Printer(name='{self.name}', model='{self.model}')>"


class PrinterComponent(Base):
    """Table for storing printer component information."""
    __tablename__ = 'printer_components'
    
    id = Column(Integer, primary_key=True)
    printer_id = Column(Integer, ForeignKey('printers.id'))
    name = Column(String(50), nullable=False)  # e.g., "Nozzle", "Extruder"
    installation_date = Column(DateTime, default=datetime.datetime.now)
    replacement_interval = Column(Integer)  # recommended replacement interval in hours
    usage_hours = Column(Float, default=0.0)  # accumulated usage hours
    notes = Column(Text)
    
    # Relationship with printer
    printer = relationship("Printer", back_populates="components")
    
    def __repr__(self):
        return f"<PrinterComponent(name='{self.name}', printer_id={self.printer_id})>"


class PrintJob(Base):
    """Table for storing print job information."""
    __tablename__ = 'print_jobs'
    
    id = Column(Integer, primary_key=True)
    date = Column(DateTime, default=datetime.datetime.now)
    project_name = Column(String(100), nullable=False)
    filament_id = Column(Integer, ForeignKey('filaments.id'))
    printer_id = Column(Integer, ForeignKey('printers.id'))
    filament_used = Column(Float, nullable=False)  # in grams
    duration = Column(Float, nullable=False)  # in hours
    notes = Column(Text)
    
    # For tracking failed prints
    is_failed = Column(Integer, default=0)  # Using Integer instead of Boolean for SQLite compatibility
    failure_percentage = Column(Float, nullable=True)  # At what percentage the print failed
    
    # For multicolor prints (secondary filaments)
    filament_id_2 = Column(Integer, ForeignKey('filaments.id'), nullable=True)
    filament_used_2 = Column(Float, nullable=True)  # in grams
    
    filament_id_3 = Column(Integer, ForeignKey('filaments.id'), nullable=True)
    filament_used_3 = Column(Float, nullable=True)  # in grams
    
    filament_id_4 = Column(Integer, ForeignKey('filaments.id'), nullable=True)
    filament_used_4 = Column(Float, nullable=True)  # in grams
    
    # Relationships
    filament = relationship("Filament", foreign_keys=[filament_id], back_populates="print_jobs")
    printer = relationship("Printer", back_populates="print_jobs")
    
    # Relationships for secondary filaments
    filament_2 = relationship("Filament", 
                             foreign_keys=[filament_id_2],
                             overlaps="secondary_print_jobs_2",
                             back_populates="secondary_print_jobs_2")
    
    filament_3 = relationship("Filament", 
                             foreign_keys=[filament_id_3],
                             overlaps="secondary_print_jobs_3",
                             back_populates="secondary_print_jobs_3")
    
    filament_4 = relationship("Filament", 
                             foreign_keys=[filament_id_4],
                             overlaps="secondary_print_jobs_4",
                             back_populates="secondary_print_jobs_4")
    
    def __repr__(self):
        return f"<PrintJob(project_name='{self.project_name}', date='{self.date}')>"


class FilamentIdealInventory(Base):
    """Table for storing ideal inventory quantities for filament types."""
    __tablename__ = 'filament_ideal_inventory'
    
    id = Column(Integer, primary_key=True)
    type = Column(String(20), nullable=False)  # PLA, ABS, etc.
    color = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)
    ideal_quantity = Column(Float, nullable=False)  # in grams
    
    def __repr__(self):
        return f"<FilamentIdealInventory(type='{self.type}', color='{self.color}', brand='{self.brand}', ideal_quantity={self.ideal_quantity})>"


class FilamentLinkGroup(Base):
    """Table for storing filament link groups."""
    __tablename__ = 'filament_link_groups'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(100), nullable=False)  # Name for the group, e.g., "White PLA variants"
    description = Column(Text)  # Optional description
    ideal_quantity = Column(Float, default=0)  # Ideal quantity for the entire group
    
    # Relationship with filament links
    filament_links = relationship("FilamentLink", back_populates="group", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<FilamentLinkGroup(name='{self.name}', ideal_quantity={self.ideal_quantity})>"


class FilamentLink(Base):
    """Table for storing linked filaments within a group."""
    __tablename__ = 'filament_links'
    
    id = Column(Integer, primary_key=True)
    group_id = Column(Integer, ForeignKey('filament_link_groups.id'), nullable=False)
    type = Column(String(20), nullable=False)  # PLA, ABS, etc.
    color = Column(String(50), nullable=False)
    brand = Column(String(50), nullable=False)
    
    # Relationship with group
    group = relationship("FilamentLinkGroup", back_populates="filament_links")
    
    def __repr__(self):
        return f"<FilamentLink(group_id={self.group_id}, type='{self.type}', color='{self.color}', brand='{self.brand}')>"


class AppSettings(Base):
    """Table for storing application settings."""
    __tablename__ = 'app_settings'
    
    id = Column(Integer, primary_key=True)
    setting_key = Column(String(50), nullable=False, unique=True)
    setting_value = Column(String(255), nullable=False)
    
    def __repr__(self):
        return f"<AppSettings(key='{self.setting_key}', value='{self.setting_value}')>"


def init_db(db_path):
    """Initialize the database and create tables if they don't exist."""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine