import os
import shutil
import datetime

def rebuild_database():
    """
    Rebuilds the database with the current schema.
    This will rename the existing database file if it exists and create a new one.
    """
    # Default database path in user's documents folder
    documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
    app_folder = os.path.join(documents_path, 'FilamentTracker')
    db_path = os.path.join(app_folder, 'filament_tracker.db')
    
    # Check if database file exists
    if os.path.exists(db_path):
        # Create backup with timestamp
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = os.path.join(app_folder, f'filament_tracker_backup_{timestamp}.db')
        
        # Copy the database to backup
        shutil.copy2(db_path, backup_path)
        print(f"Created backup of existing database: {backup_path}")
        
        # Remove original database
        os.remove(db_path)
        print(f"Removed old database: {db_path}")
        
        print("The database will be rebuilt when you start the application.")
        print("Your existing data has been backed up, but will need to be re-entered in the new database.")
    else:
        print("No existing database found. A new one will be created when you start the application.")

if __name__ == "__main__":
    rebuild_database() 