"""
Minimal script to add is_failed and failure_percentage columns to the print_jobs table.
"""
import os
import sqlite3

# Path to the current database
db_path = os.path.join(os.path.expanduser('~'), 'Documents', 'FilamentTracker', 'filament_tracker.db')

def add_columns():
    print(f"Using database at: {db_path}")
    
    # Check if database exists
    if not os.path.exists(db_path):
        print(f"Error: Database not found at {db_path}")
        return False
    
    try:
        # Connect to database
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Check if print_jobs table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='print_jobs'")
        if not cursor.fetchone():
            print("Error: print_jobs table not found")
            conn.close()
            return False
        
        print("Adding columns...")
        
        # Add is_failed column
        try:
            cursor.execute("ALTER TABLE print_jobs ADD COLUMN is_failed INTEGER DEFAULT 0")
            print("Added is_failed column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("is_failed column already exists")
            else:
                raise
        
        # Add failure_percentage column
        try:
            cursor.execute("ALTER TABLE print_jobs ADD COLUMN failure_percentage FLOAT DEFAULT NULL")
            print("Added failure_percentage column")
        except sqlite3.OperationalError as e:
            if "duplicate column name" in str(e):
                print("failure_percentage column already exists")
            else:
                raise
        
        # Commit changes and close
        conn.commit()
        conn.close()
        print("Database updated successfully")
        return True
    
    except Exception as e:
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    if add_columns():
        print("✅ Database columns added successfully. You can now run the application.")
    else:
        print("❌ Failed to add columns to database.") 