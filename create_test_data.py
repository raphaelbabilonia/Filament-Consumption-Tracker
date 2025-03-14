#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Create test data for manual testing of the Filament Consumption Tracker.
This script will populate the database with a variety of filaments, printers,
and print jobs for testing purposes.
"""

import os
import sys
import random
import datetime
from pathlib import Path

# Add parent directory to path to be able to import modules
sys.path.insert(0, str(Path(__file__).parent))

from database.db_handler import DatabaseHandler

def create_test_data(db_handler, clear_existing=False):
    """
    Create test data in the database.
    
    Args:
        db_handler: DatabaseHandler instance
        clear_existing: If True, clear existing data before adding test data
    """
    if clear_existing:
        print("Clearing existing data...")
        # Clear existing data in reverse order of dependencies
        db_handler.clear_print_jobs()
        db_handler.clear_printers()
        db_handler.clear_filaments()
        db_handler.clear_filament_link_groups()
        db_handler.clear_ideal_quantities()
    
    # Create filament types
    filament_types = ["PLA", "PETG", "ABS", "TPU", "Nylon", "HIPS", "PVA", "ASA"]
    
    # Create colors
    colors = [
        "Red", "Blue", "Green", "Yellow", "Orange", "Purple", "Pink", 
        "Black", "White", "Gray", "Brown", "Cyan", "Magenta", "Transparent",
        "Silver", "Gold", "Bronze", "Copper", "Glow in the Dark", "Wood"
    ]
    
    # Create brands
    brands = [
        "Prusament", "Hatchbox", "eSUN", "Overture", "Polymaker", "Sunlu", 
        "MatterHackers", "Colorfabb", "Proto-Pasta", "Fillamentum", 
        "Atomic Filament", "3D Solutech", "Eryone"
    ]
    
    # Add filaments
    print("Adding filaments...")
    filament_ids = []
    
    # Create a variety of filaments with different types, colors, and brands
    for i in range(50):
        filament_type = random.choice(filament_types)
        color = random.choice(colors)
        brand = random.choice(brands)
        spool_weight = random.choice([200.0, 250.0, 500.0, 750.0, 1000.0])
        qty_remaining = round(random.uniform(0, spool_weight), 1)
        price = round(random.uniform(15.0, 45.0), 2)
        
        # Create purchase date between 1-365 days ago
        days_ago = random.randint(1, 365)
        purchase_date = datetime.date.today() - datetime.timedelta(days=days_ago)
        
        try:
            filament_id = db_handler.add_filament(
                filament_type=filament_type,
                color=color,
                brand=brand,
                spool_weight=spool_weight,
                quantity_remaining=qty_remaining,
                price=price,
                purchase_date=purchase_date
            )
            filament_ids.append(filament_id)
            print(f"Added {filament_type} {color} by {brand}")
        except Exception as e:
            print(f"Error adding filament: {e}")
    
    # Set ideal quantities for some filament combinations
    print("\nSetting ideal quantities...")
    
    # Get unique type/color combinations
    filaments = db_handler.get_filaments()
    type_color_combos = set()
    
    for filament in filaments:
        type_color_combos.add((filament.type, filament.color, filament.brand))
    
    # Set ideal quantities for half of the combinations
    for combo in list(type_color_combos)[:len(type_color_combos)//2]:
        filament_type, color, brand = combo
        ideal_qty = round(random.uniform(500.0, 3000.0), 1)
        try:
            db_handler.set_ideal_filament_quantity(filament_type, color, brand, ideal_qty)
            print(f"Set ideal quantity of {ideal_qty}g for {filament_type} {color} ({brand})")
        except Exception as e:
            print(f"Error setting ideal quantity: {e}")
    
    # Create filament link groups
    print("\nCreating filament link groups...")
    group_ids = []
    
    # Create 5 groups
    for i in range(5):
        group_name = f"Group {i+1}: {random.choice(filament_types)}"
        description = f"Test group for {group_name}"
        ideal_qty = round(random.uniform(1000.0, 5000.0), 1)
        
        try:
            group_id = db_handler.create_filament_link_group(
                name=group_name,
                description=description,
                ideal_quantity=ideal_qty
            )
            group_ids.append(group_id)
            print(f"Created group '{group_name}'")
        except Exception as e:
            print(f"Error creating group: {e}")
    
    # Add filaments to groups
    for group_id in group_ids:
        # Add 3-6 filaments to each group
        num_filaments = random.randint(3, 6)
        added_filaments = set()
        
        for _ in range(num_filaments):
            # Get a random filament
            while True:
                filament = random.choice(filaments)
                key = (filament.type, filament.color, filament.brand)
                
                # Don't add the same filament twice
                if key not in added_filaments:
                    added_filaments.add(key)
                    break
            
            try:
                db_handler.add_filament_to_link_group(
                    group_id, filament.type, filament.color, filament.brand
                )
                print(f"Added {filament.type} {filament.color} to group {group_id}")
            except Exception as e:
                print(f"Error adding filament to group: {e}")
    
    # Add printers
    print("\nAdding printers...")
    printer_ids = []
    
    printer_models = [
        "Prusa i3 MK3S+", "Ender 3 Pro", "Ender 3 V2", "Voron 2.4",
        "Voron Trident", "Bambu Lab X1", "Creality CR-10", "Prusa Mini+",
        "Ultimaker S3", "Elegoo Mars 2 Pro", "AnyCubic Photon Mono",
        "Flashforge Adventurer 3", "Anycubic Kobra Max"
    ]
    
    for i in range(5):
        name = f"Printer {i+1}"
        model = random.choice(printer_models)
        purchase_date = datetime.date.today() - datetime.timedelta(days=random.randint(1, 730))
        price = round(random.uniform(200.0, 2000.0), 2)
        power_consumption = round(random.uniform(100.0, 400.0), 1)
        
        try:
            printer_id = db_handler.add_printer(
                name=name,
                model=model,
                purchase_date=purchase_date,
                price=price,
                power_consumption=power_consumption
            )
            printer_ids.append(printer_id)
            print(f"Added printer '{name}' ({model})")
        except Exception as e:
            print(f"Error adding printer: {e}")
    
    # Add print jobs
    print("\nAdding print jobs...")
    
    job_names = [
        "XYZ Calibration Cube", "Benchy", "Phone Stand", "Vase", "Drawer Organizer",
        "Cable Clip", "Headphone Stand", "Miniature Figure", "Keychain", "Tool Holder",
        "Arduino Case", "Raspberry Pi Case", "Wall Mount", "Desk Organizer", "Plant Pot",
        "Christmas Ornament", "Halloween Decoration", "Fidget Toy", "Mask Holder",
        "Door Stop", "Pen Holder", "SD Card Holder", "Remote Control Holder"
    ]
    
    for i in range(30):
        name = random.choice(job_names)
        printer_id = random.choice(printer_ids)
        filament_id = random.choice(filament_ids)
        
        # Create date between 1-180 days ago
        days_ago = random.randint(1, 180)
        date = datetime.date.today() - datetime.timedelta(days=days_ago)
        
        # Random print job details
        weight = round(random.uniform(5.0, 200.0), 1)
        duration_hours = round(random.uniform(0.5, 10.0), 1)
        
        try:
            job_id = db_handler.add_print_job(
                name=name,
                printer_id=printer_id,
                filament_id=filament_id,
                date=date,
                weight=weight,
                duration_hours=duration_hours
            )
            print(f"Added print job '{name}' ({weight}g)")
        except Exception as e:
            print(f"Error adding print job: {e}")
    
    print("\nTest data creation complete!")

def main():
    """Main function to create test data."""
    # Ask user if they want to clear existing data
    clear_existing = input("Clear existing data before adding test data? (y/n): ").lower() == 'y'
    
    db_handler = DatabaseHandler()
    create_test_data(db_handler, clear_existing)

if __name__ == "__main__":
    main() 