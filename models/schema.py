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
    
    # Relationship with print jobs
    print_jobs = relationship("PrintJob", back_populates="filament")
    
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
        return f"<PrinterComponent(name='{self.name}', printer='{self.printer.name}')>"


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
    
    # Relationships
    filament = relationship("Filament", back_populates="print_jobs")
    printer = relationship("Printer", back_populates="print_jobs")
    
    def __repr__(self):
        return f"<PrintJob(project_name='{self.project_name}', date='{self.date}')>"


def init_db(db_path):
    """Initialize the database and create tables if they don't exist."""
    engine = create_engine(f'sqlite:///{db_path}')
    Base.metadata.create_all(engine)
    return engine