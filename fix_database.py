"""
Script to update the database schema to add new columns for failed print tracking.
Uses a specific backup file automatically without user interaction.
"""
import os
import sqlite3
import shutil
from datetime import datetime

# Define paths
DOCUMENTS_PATH = os.path.join(os.path.expanduser('~'), 'Documents')
APP_FOLDER = os.path.join(DOCUMENTS_PATH, 'FilamentTracker')
SOURCE_DB_PATH = os.path.join(APP_FOLDER, 'filament_tracker_backup_20250317_141120.db')
CURRENT_DB_PATH = os.path.join(APP_FOLDER, 'filament_tracker.db')

def update_database_schema():
    """Update the database schema to add new columns for tracking failed prints."""
    print(f"Documents path: {DOCUMENTS_PATH}")
    print(f"App folder: {APP_FOLDER}")
    print(f"Source DB path: {SOURCE_DB_PATH}")
    print(f"Current DB path: {CURRENT_DB_PATH}")
    
    # Check if the app folder exists
    if not os.path.exists(APP_FOLDER):
        print(f"Error: App folder not found at {APP_FOLDER}")
        return False
    
    # Make sure the source file exists
    if not os.path.exists(SOURCE_DB_PATH):
        print(f"Error: Source database file not found at {SOURCE_DB_PATH}")
        
        # List all .db files in the folder to help identify the correct one
        print("Available database files:")
        for file in os.listdir(APP_FOLDER):
            if file.endswith('.db'):
                print(f"  - {file}")
        return False
    
    # Create another backup just to be safe
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_backup_path = os.path.join(APP_FOLDER, f'filament_tracker_pre_update_{timestamp}.db')
    
    conn = None
    try:
        # Make a safety backup
        print(f"Creating safety backup at: {safe_backup_path}")
        shutil.copy2(SOURCE_DB_PATH, safe_backup_path)
        print(f"Safety backup created successfully")
        
        # Connect to the database
        print("Connecting to database...")
        conn = sqlite3.connect(SOURCE_DB_PATH)
        cursor = conn.cursor()
        
        # Check if the print_jobs table exists
        print("Checking if print_jobs table exists...")
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='print_jobs'")
        if not cursor.fetchone():
            print("Error: print_jobs table not found in the database")
            conn.close()
            return False
        
        # Check if columns already exist (in case script is run multiple times)
        print("Checking existing columns...")
        cursor.execute("PRAGMA table_info(print_jobs)")
        columns = [column[1] for column in cursor.fetchall()]
        print(f"Existing columns in print_jobs table: {columns}")
        
        # Add the new columns if they don't exist
        if 'is_failed' not in columns:
            print("Adding 'is_failed' column to print_jobs table...")
            cursor.execute("ALTER TABLE print_jobs ADD COLUMN is_failed INTEGER DEFAULT 0")
            print("'is_failed' column added successfully")
        else:
            print("'is_failed' column already exists")
        
        if 'failure_percentage' not in columns:
            print("Adding 'failure_percentage' column to print_jobs table...")
            cursor.execute("ALTER TABLE print_jobs ADD COLUMN failure_percentage FLOAT DEFAULT NULL")
            print("'failure_percentage' column added successfully")
        else:
            print("'failure_percentage' column already exists")
        
        # Commit the changes
        print("Committing changes...")
        conn.commit()
        print("Changes committed successfully")
        
        # Close the connection
        conn.close()
        print("Database connection closed")
        
        # Copy the updated database to the current location
        print("Copying updated database to current location...")
        if os.path.exists(CURRENT_DB_PATH):
            os.remove(CURRENT_DB_PATH)
            print(f"Removed existing database: {CURRENT_DB_PATH}")
        
        shutil.copy2(SOURCE_DB_PATH, CURRENT_DB_PATH)
        print(f"Successfully updated database schema and restored to: {CURRENT_DB_PATH}")
        
        return True
    except Exception as e:
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        if conn:
            conn.close()
        return False

if __name__ == "__main__":
    print("Starting database schema update...")
    if update_database_schema():
        print("\nDatabase schema update completed successfully! You can now run the application.")
    else:
        print("\nDatabase schema update failed.") 