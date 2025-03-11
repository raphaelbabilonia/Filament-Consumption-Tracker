import os
import shutil
import datetime
import sqlite3
from PyQt5.QtWidgets import QApplication, QMessageBox
from sqlalchemy import create_engine, Column, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

from database.db_handler import DatabaseHandler
from models.schema import Base, Printer

def update_database_schema():
    """
    Creates a backup of the existing database and then alters 
    the schema to add columns needed for multicolor printing.
    """
    # Default database path in user's documents folder
    documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    app_folder = os.path.join(documents_path, 'FilamentTracker')
    db_path = os.path.join(app_folder, 'filament_tracker.db')
    
    # Check if database file exists
    if os.path.exists(db_path):
        print(f"Found database at: {db_path}")
        
        # Create backup with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(app_folder, f'filament_tracker_backup_{timestamp}.db')
        
        # Copy the database to backup
        shutil.copy2(db_path, backup_path)
        print(f"Created backup of existing database at: {backup_path}")
        
        # Connect to the database
        try:
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            
            # Check if the new columns already exist
            cursor.execute("PRAGMA table_info(print_jobs)")
            columns = [row[1] for row in cursor.fetchall()]
            
            # Add new columns if they don't exist
            if 'filament_id_2' not in columns:
                print("Adding new columns for multicolor printing...")
                
                # Add columns for multicolor printing
                cursor.execute("ALTER TABLE print_jobs ADD COLUMN filament_id_2 INTEGER REFERENCES filaments(id)")
                cursor.execute("ALTER TABLE print_jobs ADD COLUMN filament_used_2 FLOAT")
                cursor.execute("ALTER TABLE print_jobs ADD COLUMN filament_id_3 INTEGER REFERENCES filaments(id)")
                cursor.execute("ALTER TABLE print_jobs ADD COLUMN filament_used_3 FLOAT")
                cursor.execute("ALTER TABLE print_jobs ADD COLUMN filament_id_4 INTEGER REFERENCES filaments(id)")
                cursor.execute("ALTER TABLE print_jobs ADD COLUMN filament_used_4 FLOAT")
                
                conn.commit()
                print("Database schema updated successfully!")
                return True, backup_path
            else:
                print("Database schema is already up to date.")
                return True, "No update needed"
            
            conn.close()
            
        except Exception as e:
            print(f"Error updating database schema: {str(e)}")
            return False, str(e)
    else:
        print("Database file not found. Please run the application first to create the database.")
        return False, "Database not found"

def update_database():
    """Update the database schema to add power consumption field."""
    try:
        # Get database path
        documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
        app_folder = os.path.join(documents_path, 'FilamentTracker')
        db_path = os.path.join(app_folder, 'filament_tracker.db')
        
        if not os.path.exists(db_path):
            print(f"Database not found at {db_path}")
            return False, "Database not found"
        
        print(f"Found database at: {db_path}")
        
        # Connect to the database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if power_consumption column exists in printers table
        cursor.execute("PRAGMA table_info(printers)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Add power_consumption column if it doesn't exist
        if "power_consumption" not in columns:
            print("Adding power_consumption column to printers table...")
            cursor.execute("ALTER TABLE printers ADD COLUMN power_consumption FLOAT DEFAULT 0.0")
            conn.commit()
            print("Power consumption field added successfully!")
            return True, "Power consumption field added successfully"
        else:
            print("Power consumption field already exists. No update needed.")
            return True, "No update needed"
    except Exception as e:
        print(f"Error updating database: {str(e)}")
        return False, str(e)
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    print("=== Database Update for Filament Consumption Tracker ===")
    
    # Run the multicolor printing update
    print("\n=== Update for Multicolor Printing Support ===")
    success, message = update_database_schema()
    if success:
        print(f"SUCCESS: {message}")
    else:
        print(f"ERROR: Failed to update database: {message}")
    
    # Run the power consumption update
    print("\n=== Update for Power Consumption Tracking ===")
    success, message = update_database()
    if success:
        print(f"SUCCESS: {message}")
    else:
        print(f"ERROR: Failed to update database: {message}")
    
    input("\nPress Enter to exit...") 