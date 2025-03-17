"""
Database handler module for managing database operations.
"""
import os
import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from models.schema import Base, Filament, Printer, PrinterComponent, PrintJob, FilamentIdealInventory, FilamentLinkGroup, FilamentLink, AppSettings

class DatabaseHandler:
    """Handler for database operations."""
    
    def __init__(self, db_path=None):
        """Initialize database handler."""
        if db_path is None:
            # Default database path in user's documents folder
            documents_path = os.path.join(os.path.expanduser('~'), 'Documents')
            app_folder = os.path.join(documents_path, 'FilamentTracker')
            
            # Create directory if it doesn't exist
            if not os.path.exists(app_folder):
                os.makedirs(app_folder)
                
            db_path = os.path.join(app_folder, 'filament_tracker.db')
            
        self.engine = create_engine(f'sqlite:///{db_path}')
        Base.metadata.create_all(self.engine)
        
        # Create a session factory
        self.session_factory = sessionmaker(bind=self.engine)
        self.Session = scoped_session(self.session_factory)
        
        # Initialize default settings if they don't exist
        self.initialize_default_settings()
    
    def initialize_default_settings(self):
        """Initialize default application settings if they don't exist."""
        session = self.Session()
        try:
            # Check if electricity cost setting exists, if not, create it
            electricity_cost = session.query(AppSettings).filter_by(setting_key='electricity_cost_per_kwh').first()
            if not electricity_cost:
                electricity_cost = AppSettings(setting_key='electricity_cost_per_kwh', setting_value='0.30')
                session.add(electricity_cost)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Error initializing default settings: {e}")
        finally:
            session.close()
    
    # Settings operations
    def get_setting(self, key, default=None):
        """Get a setting value by key."""
        session = self.Session()
        try:
            setting = session.query(AppSettings).filter_by(setting_key=key).first()
            if setting:
                return setting.setting_value
            return default
        except Exception as e:
            print(f"Error getting setting: {e}")
            return default
        finally:
            session.close()
    
    def set_setting(self, key, value):
        """Set a setting value by key."""
        session = self.Session()
        try:
            setting = session.query(AppSettings).filter_by(setting_key=key).first()
            if setting:
                setting.setting_value = str(value)
            else:
                setting = AppSettings(setting_key=key, setting_value=str(value))
                session.add(setting)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error setting value: {e}")
            return False
        finally:
            session.close()
    
    def get_electricity_cost(self):
        """Get the global electricity cost per kWh setting."""
        cost_str = self.get_setting('electricity_cost_per_kwh', '0.30')
        try:
            return float(cost_str)
        except (ValueError, TypeError):
            return 0.30  # Default value
    
    def set_electricity_cost(self, cost):
        """Set the global electricity cost per kWh setting."""
        return self.set_setting('electricity_cost_per_kwh', str(cost))
    
    # Filament operations
    def add_filament(self, filament_type, color, brand, spool_weight, quantity_remaining=None, price=None, purchase_date=None):
        """Add a new filament to the inventory."""
        session = self.Session()
        try:
            if quantity_remaining is None:
                quantity_remaining = spool_weight
                
            filament = Filament(
                type=filament_type,
                color=color,
                brand=brand,
                spool_weight=spool_weight,
                quantity_remaining=quantity_remaining,
                price=price,
                purchase_date=purchase_date if purchase_date else datetime.datetime.now()
            )
            session.add(filament)
            session.commit()
            return filament.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_filaments(self):
        """Get all filaments from the database."""
        session = self.Session()
        try:
            return session.query(Filament).all()
        finally:
            session.close()
    
    def get_filament_by_id(self, filament_id):
        """Get a single filament by its ID."""
        session = self.Session()
        try:
            return session.query(Filament).filter_by(id=filament_id).first()
        finally:
            session.close()
    
    def update_filament_quantity(self, filament_id, new_quantity):
        """Update the remaining quantity of a filament."""
        session = self.Session()
        try:
            filament = session.query(Filament).filter_by(id=filament_id).first()
            if not filament:
                raise ValueError(f"No filament found with ID {filament_id}")
            filament.quantity_remaining = new_quantity
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_filament(self, filament_id, filament_type, color, brand, spool_weight, quantity_remaining, price, purchase_date):
        """Update all properties of a filament."""
        session = self.Session()
        try:
            filament = session.query(Filament).filter_by(id=filament_id).first()
            if not filament:
                raise ValueError(f"No filament found with ID {filament_id}")
            
            filament.type = filament_type
            filament.color = color
            filament.brand = brand
            filament.spool_weight = spool_weight
            filament.quantity_remaining = quantity_remaining
            filament.price = price
            
            # Convert string date to datetime if needed
            if isinstance(purchase_date, str):
                import datetime
                purchase_date = datetime.datetime.strptime(purchase_date, "%Y-%m-%d").date()
            
            filament.purchase_date = purchase_date
            
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_filament(self, filament_id):
        """Delete a filament from the database."""
        session = self.Session()
        try:
            filament = session.query(Filament).filter_by(id=filament_id).first()
            if not filament:
                raise ValueError(f"No filament found with ID {filament_id}")
            
            # Check if filament is used in any print jobs
            print_jobs = session.query(PrintJob).filter_by(filament_id=filament_id).all()
            if print_jobs:
                raise ValueError("Cannot delete filament that is referenced by print jobs")
                
            session.delete(filament)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_filament_types(self):
        """Get a list of unique filament types in the inventory."""
        session = self.Session()
        try:
            return [type[0] for type in session.query(Filament.type).distinct().all()]
        finally:
            session.close()
    
    def get_filament_colors(self):
        """Get a list of unique filament colors in the inventory."""
        session = self.Session()
        try:
            return [color[0] for color in session.query(Filament.color).distinct().all()]
        finally:
            session.close()
    
    def get_filament_brands(self):
        """Get a list of unique filament brands in the inventory."""
        session = self.Session()
        try:
            return [brand[0] for brand in session.query(Filament.brand).distinct().all()]
        finally:
            session.close()
    
    def get_aggregated_filament_inventory(self):
        """Get filament inventory aggregated by type, color, and brand."""
        session = self.Session()
        try:
            # Group filaments by type, color, and brand and sum their quantities
            result = []
            
            # Get unique combinations of type, color, brand
            unique_filaments = session.query(
                Filament.type, 
                Filament.color, 
                Filament.brand
            ).distinct().all()
            
            for type_, color, brand in unique_filaments:
                # Get all filaments matching this combination
                matching_filaments = session.query(Filament).filter_by(
                    type=type_,
                    color=color,
                    brand=brand
                ).all()
                
                # Calculate total and remaining quantities
                total_quantity = sum(f.spool_weight for f in matching_filaments)
                quantity_remaining = sum(f.quantity_remaining for f in matching_filaments)
                
                # Calculate average price if available
                prices = [f.price for f in matching_filaments if f.price is not None]
                avg_price = sum(prices) / len(prices) if prices else None
                
                # Add to results
                result.append({
                    'type': type_,
                    'color': color,
                    'brand': brand,
                    'quantity_remaining': quantity_remaining,
                    'total_quantity': total_quantity,
                    'percentage_remaining': (quantity_remaining / total_quantity * 100) if total_quantity > 0 else 0,
                    'avg_price': avg_price,
                    'spool_count': len(matching_filaments),
                    'filament_ids': [f.id for f in matching_filaments]
                })
                
            return result
        finally:
            session.close()
    
    # Printer operations
    def add_printer(self, name, model=None, power_consumption=0.0, notes=None):
        """Add a new printer to the database."""
        session = self.Session()
        try:
            printer = Printer(
                name=name,
                model=model,
                purchase_date=datetime.datetime.now(),
                power_consumption=power_consumption,
                notes=notes
            )
            session.add(printer)
            session.commit()
            return printer.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_printers(self):
        """Get all printers from the database."""
        session = self.Session()
        try:
            return session.query(Printer).all()
        finally:
            session.close()
    
    def update_printer(self, printer_id, name=None, model=None, power_consumption=None, notes=None):
        """Update printer information."""
        session = self.Session()
        try:
            printer = session.query(Printer).filter_by(id=printer_id).first()
            if not printer:
                raise ValueError(f"No printer found with ID {printer_id}")
            
            if name:
                printer.name = name
            if model:
                printer.model = model
            if power_consumption is not None:
                printer.power_consumption = power_consumption
            if notes is not None:
                printer.notes = notes
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_printer(self, printer_id):
        """Delete a printer from the database."""
        session = self.Session()
        try:
            printer = session.query(Printer).filter_by(id=printer_id).first()
            if not printer:
                raise ValueError(f"No printer found with ID {printer_id}")
                
            # Check if printer is used in any print jobs
            print_jobs = session.query(PrintJob).filter_by(printer_id=printer_id).all()
            if print_jobs:
                raise ValueError("Cannot delete printer that is referenced by print jobs")
                
            # Delete related components
            components = session.query(PrinterComponent).filter_by(printer_id=printer_id).all()
            for component in components:
                session.delete(component)
                
            session.delete(printer)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Printer component operations
    def add_printer_component(self, printer_id, name, replacement_interval=None, notes=None):
        """Add a new component to a printer."""
        session = self.Session()
        try:
            printer = session.query(Printer).filter_by(id=printer_id).first()
            if not printer:
                raise ValueError(f"No printer found with ID {printer_id}")
                
            component = PrinterComponent(
                printer_id=printer_id,
                name=name,
                installation_date=datetime.datetime.now(),
                replacement_interval=replacement_interval,
                usage_hours=0.0,
                notes=notes
            )
            session.add(component)
            session.commit()
            return component.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_printer_components(self, printer_id=None):
        """Get components for a specific printer or all components."""
        session = self.Session()
        try:
            query = session.query(PrinterComponent).options(joinedload(PrinterComponent.printer))
            if printer_id:
                query = query.filter_by(printer_id=printer_id)
            return query.all()
        finally:
            session.close()
    
    def update_component_usage(self, component_id, additional_hours):
        """Update the usage hours of a printer component."""
        session = self.Session()
        try:
            component = session.query(PrinterComponent).filter_by(id=component_id).first()
            if not component:
                raise ValueError(f"No component found with ID {component_id}")
                
            component.usage_hours += additional_hours
            session.commit()
            return component.usage_hours
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_printer_component(self, component_id, name=None, replacement_interval=None, notes=None, 
                                installation_date=None, usage_hours=None):
        """Update a printer component's information."""
        session = self.Session()
        try:
            component = session.query(PrinterComponent).filter_by(id=component_id).first()
            if not component:
                raise ValueError(f"No component found with ID {component_id}")
            
            if name is not None:
                component.name = name
            if replacement_interval is not None:
                component.replacement_interval = replacement_interval
            if notes is not None:
                component.notes = notes
            if installation_date is not None:
                component.installation_date = installation_date
            if usage_hours is not None:
                component.usage_hours = usage_hours
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    # Print job operations
    def add_print_job(self, project_name, filament_id, printer_id, filament_used, duration, notes=None,
                      filament_id_2=None, filament_used_2=None,
                      filament_id_3=None, filament_used_3=None,
                      filament_id_4=None, filament_used_4=None):
        """Add a new print job to the database.
        
        Args:
            project_name: Name of the print project
            filament_id: Primary filament ID
            printer_id: Printer ID
            filament_used: Amount of primary filament used (in grams)
            duration: Print duration (in hours)
            notes: Optional notes
            filament_id_2: Secondary filament ID (optional)
            filament_used_2: Amount of secondary filament used (optional)
            filament_id_3: Tertiary filament ID (optional)
            filament_used_3: Amount of tertiary filament used (optional)
            filament_id_4: Quaternary filament ID (optional)
            filament_used_4: Amount of quaternary filament used (optional)
        """
        session = self.Session()
        try:
            # Check if primary filament exists
            filament = session.query(Filament).filter_by(id=filament_id).first()
            if not filament:
                raise ValueError(f"No filament found with ID {filament_id}")
            
            # Check if printer exists
            printer = session.query(Printer).filter_by(id=printer_id).first()
            if not printer:
                raise ValueError(f"No printer found with ID {printer_id}")
            
            # Check if enough primary filament is available
            if filament.quantity_remaining < filament_used:
                raise ValueError(f"Not enough filament available. Only {filament.quantity_remaining}g remaining.")
            
            # Check secondary filaments if provided
            filament_2 = None
            if filament_id_2 and filament_used_2:
                filament_2 = session.query(Filament).filter_by(id=filament_id_2).first()
                if not filament_2:
                    raise ValueError(f"No filament found with ID {filament_id_2}")
                if filament_2.quantity_remaining < filament_used_2:
                    raise ValueError(f"Not enough secondary filament available. Only {filament_2.quantity_remaining}g remaining.")
            
            filament_3 = None
            if filament_id_3 and filament_used_3:
                filament_3 = session.query(Filament).filter_by(id=filament_id_3).first()
                if not filament_3:
                    raise ValueError(f"No filament found with ID {filament_id_3}")
                if filament_3.quantity_remaining < filament_used_3:
                    raise ValueError(f"Not enough tertiary filament available. Only {filament_3.quantity_remaining}g remaining.")
            
            filament_4 = None
            if filament_id_4 and filament_used_4:
                filament_4 = session.query(Filament).filter_by(id=filament_id_4).first()
                if not filament_4:
                    raise ValueError(f"No filament found with ID {filament_id_4}")
                if filament_4.quantity_remaining < filament_used_4:
                    raise ValueError(f"Not enough quaternary filament available. Only {filament_4.quantity_remaining}g remaining.")
            
            # Create print job
            print_job = PrintJob(
                date=datetime.datetime.now(),
                project_name=project_name,
                filament_id=filament_id,
                printer_id=printer_id,
                filament_used=filament_used,
                duration=duration,
                notes=notes,
                filament_id_2=filament_id_2,
                filament_used_2=filament_used_2,
                filament_id_3=filament_id_3,
                filament_used_3=filament_used_3,
                filament_id_4=filament_id_4,
                filament_used_4=filament_used_4
            )
            
            # Update primary filament quantity
            filament.quantity_remaining -= filament_used
            
            # Update secondary filament quantities if provided
            if filament_2 and filament_used_2:
                filament_2.quantity_remaining -= filament_used_2
                
            if filament_3 and filament_used_3:
                filament_3.quantity_remaining -= filament_used_3
                
            if filament_4 and filament_used_4:
                filament_4.quantity_remaining -= filament_used_4
            
            # Update component usage for all components of this printer
            components = session.query(PrinterComponent).filter_by(printer_id=printer_id).all()
            for component in components:
                component.usage_hours += duration
            
            session.add(print_job)
            session.commit()
            return print_job.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_print_jobs(self, project_name=None, filament_id=None, printer_id=None, start_date=None, end_date=None):
        """Get print jobs with optional filtering."""
        session = self.Session()
        try:
            # Use joinedload to eagerly load the relationships to prevent lazy loading errors
            query = session.query(PrintJob).options(
                joinedload(PrintJob.filament),
                joinedload(PrintJob.printer),
                joinedload(PrintJob.filament_2),
                joinedload(PrintJob.filament_3),
                joinedload(PrintJob.filament_4)
            )
            
            if project_name:
                query = query.filter(PrintJob.project_name.like(f"%{project_name}%"))
                
            if filament_id:
                # Filter for any of the filament columns containing this filament
                query = query.filter(
                    (PrintJob.filament_id == filament_id) |
                    (PrintJob.filament_id_2 == filament_id) |
                    (PrintJob.filament_id_3 == filament_id) |
                    (PrintJob.filament_id_4 == filament_id)
                )
                
            if printer_id:
                query = query.filter_by(printer_id=printer_id)
                
            if start_date:
                query = query.filter(PrintJob.date >= start_date)
                
            if end_date:
                query = query.filter(PrintJob.date <= end_date)
            
            # Order by date, newest first
            query = query.order_by(PrintJob.date.desc())
            
            # Execute the query and return all results
            return query.all()
        finally:
            session.close()
    
    def get_failed_print_jobs(self, printer_id=None, filament_id=None, start_date=None, end_date=None):
        """Get all failed print jobs with optional filtering."""
        session = self.Session()
        try:
            # Use joinedload to eagerly load the relationships to prevent lazy loading errors
            query = session.query(PrintJob).options(
                joinedload(PrintJob.filament),
                joinedload(PrintJob.printer),
                joinedload(PrintJob.filament_2),
                joinedload(PrintJob.filament_3),
                joinedload(PrintJob.filament_4)
            ).filter(PrintJob.is_failed == 1)  # Filter for failed prints
            
            # Apply additional filters if provided
            if printer_id:
                query = query.filter_by(printer_id=printer_id)
                
            if filament_id:
                # Filter for any of the filament columns containing this filament
                query = query.filter(
                    (PrintJob.filament_id == filament_id) |
                    (PrintJob.filament_id_2 == filament_id) |
                    (PrintJob.filament_id_3 == filament_id) |
                    (PrintJob.filament_id_4 == filament_id)
                )
                
            if start_date:
                query = query.filter(PrintJob.date >= start_date)
                
            if end_date:
                query = query.filter(PrintJob.date <= end_date)
            
            # Order by date, newest first
            query = query.order_by(PrintJob.date.desc())
            
            # Execute the query and return all results
            return query.all()
        finally:
            session.close()
    
    def get_print_job_by_id(self, job_id):
        """Get a single print job by its ID."""
        session = self.Session()
        try:
            # Use joinedload to eagerly load the relationships to prevent lazy loading errors
            return session.query(PrintJob).options(
                joinedload(PrintJob.filament),
                joinedload(PrintJob.printer),
                joinedload(PrintJob.filament_2),
                joinedload(PrintJob.filament_3),
                joinedload(PrintJob.filament_4)
            ).filter_by(id=job_id).first()
        finally:
            session.close()
    
    def update_print_job(self, job_id, project_name=None, printer_id=None, notes=None, 
                        is_failed=None, failure_percentage=None):
        """Update an existing print job.
        
        If a print is marked as failed, this will also restore the unused portion of filament back to inventory
        and adjust the print duration based on the failure percentage.
        
        Args:
            job_id: ID of the print job to update
            project_name: New project name (optional)
            printer_id: New printer ID (optional)
            notes: New notes (optional)
            is_failed: Whether the print failed (0 = success, 1 = failed)
            failure_percentage: Percentage of completion when the print failed (0-100)
        
        Returns:
            Dictionary with information about the updated job and restored filaments if applicable
        """
        session = self.Session()
        try:
            job = session.query(PrintJob).filter_by(id=job_id).first()
            if not job:
                raise ValueError(f"No print job found with ID {job_id}")
            
            # Track changes for return value
            update_info = {'id': job_id, 'project_name': job.project_name}
            restored_filaments = []
            
            # Update basic fields if provided
            if project_name is not None:
                job.project_name = project_name
                update_info['project_name'] = project_name
                
            if printer_id is not None:
                job.printer_id = printer_id
                
            if notes is not None:
                job.notes = notes
            
            # Handle failed print status
            # Check if we're marking a previously successful print as failed
            if is_failed == 1 and job.is_failed == 0 and failure_percentage is not None:
                # This is a newly failed print - need to restore filament and adjust duration
                job.is_failed = 1
                job.failure_percentage = failure_percentage
                
                # Calculate how much filament to restore for each used filament
                # If we failed at X%, then we restore (100-X)% of the filament
                restore_factor = (100 - failure_percentage) / 100.0
                
                # Store original duration for reporting
                original_duration = job.duration
                
                # Adjust duration based on failure percentage
                # If failed at X%, then actual duration is X% of original
                adjusted_duration = job.duration * (failure_percentage / 100.0)
                job.duration = adjusted_duration
                
                # Track time adjustment for reporting
                update_info['original_duration'] = original_duration
                update_info['adjusted_duration'] = adjusted_duration
                update_info['time_saved'] = original_duration - adjusted_duration
                
                # Restore primary filament
                if job.filament_id and job.filament_used:
                    amount_to_restore = job.filament_used * restore_factor
                    filament = session.query(Filament).filter_by(id=job.filament_id).first()
                    if filament:
                        filament.quantity_remaining += amount_to_restore
                        restored_filaments.append({
                            'filament_id': job.filament_id,
                            'brand': filament.brand,
                            'color': filament.color,
                            'type': filament.type,
                            'restored': amount_to_restore
                        })
                
                # Restore secondary filaments if they exist
                if job.filament_id_2 and job.filament_used_2:
                    amount_to_restore = job.filament_used_2 * restore_factor
                    filament2 = session.query(Filament).filter_by(id=job.filament_id_2).first()
                    if filament2:
                        filament2.quantity_remaining += amount_to_restore
                        restored_filaments.append({
                            'filament_id': job.filament_id_2,
                            'brand': filament2.brand,
                            'color': filament2.color,
                            'type': filament2.type,
                            'restored': amount_to_restore
                        })
                
                if job.filament_id_3 and job.filament_used_3:
                    amount_to_restore = job.filament_used_3 * restore_factor
                    filament3 = session.query(Filament).filter_by(id=job.filament_id_3).first()
                    if filament3:
                        filament3.quantity_remaining += amount_to_restore
                        restored_filaments.append({
                            'filament_id': job.filament_id_3,
                            'brand': filament3.brand,
                            'color': filament3.color,
                            'type': filament3.type,
                            'restored': amount_to_restore
                        })
                
                if job.filament_id_4 and job.filament_used_4:
                    amount_to_restore = job.filament_used_4 * restore_factor
                    filament4 = session.query(Filament).filter_by(id=job.filament_id_4).first()
                    if filament4:
                        filament4.quantity_remaining += amount_to_restore
                        restored_filaments.append({
                            'filament_id': job.filament_id_4,
                            'brand': filament4.brand,
                            'color': filament4.color,
                            'type': filament4.type,
                            'restored': amount_to_restore
                        })
                
                update_info['restored_filaments'] = restored_filaments
                update_info['total_restored'] = sum(item['restored'] for item in restored_filaments)
                update_info['is_failed'] = True
                update_info['failure_percentage'] = failure_percentage
            
            # If marking a failed print as successful, don't do anything with the filament
            # as that would be too complex to track (the filament has already been adjusted)
            elif is_failed == 0 and job.is_failed == 1:
                job.is_failed = 0
                job.failure_percentage = None
                update_info['is_failed'] = False
                
            # Just updating the failure percentage without changing the failed status
            elif is_failed == 1 and job.is_failed == 1 and failure_percentage is not None:
                # Already a failed print, just update the percentage
                job.failure_percentage = failure_percentage
                update_info['is_failed'] = True
                update_info['failure_percentage'] = failure_percentage
            
            session.commit()
            return update_info
            
        except Exception as e:
            session.rollback()
            print(f"Error in update_print_job: {str(e)}")
            raise e
        finally:
            session.close()
    
    def get_filament_usage_by_type(self):
        """Get filament usage statistics by type."""
        session = self.Session()
        try:
            # This is a simplified version - in a real app you might want to use SQLAlchemy's 
            # group_by and func features for more complex queries
            filaments = session.query(Filament).all()
            result = {}
            
            for filament in filaments:
                filament_type = filament.type
                if filament_type not in result:
                    result[filament_type] = 0
                    
                # Sum up usage from print jobs
                for job in filament.print_jobs:
                    result[filament_type] += job.filament_used
                    
            return result
        finally:
            session.close()
    
    def get_filament_usage_by_color(self):
        """Get filament usage statistics by color."""
        session = self.Session()
        try:
            filaments = session.query(Filament).all()
            result = {}
            
            for filament in filaments:
                color = filament.color
                if color not in result:
                    result[color] = 0
                    
                # Sum up usage from print jobs
                for job in filament.print_jobs:
                    result[color] += job.filament_used
                    
            return result
        finally:
            session.close()
    
    def get_printer_usage_stats(self):
        """Get printer usage statistics."""
        session = self.Session()
        try:
            printers = session.query(Printer).all()
            result = {}
            
            for printer in printers:
                # Calculate total hours and jobs
                total_hours = sum(job.duration for job in printer.print_jobs)
                total_jobs = len(printer.print_jobs)
                total_filament = sum(job.filament_used for job in printer.print_jobs)
                
                result[printer.name] = {
                    'total_hours': total_hours,
                    'total_jobs': total_jobs,
                    'total_filament_used': total_filament
                }
                
            return result
        finally:
            session.close()
    
    def delete_print_job(self, job_id):
        """Delete a print job and restore the filament used back to inventory."""
        session = self.Session()
        try:
            job = session.query(PrintJob).filter_by(id=job_id).first()
            if not job:
                raise ValueError(f"No print job found with ID {job_id}")
            
            # Track restored filaments for reporting
            restored_filaments = []
            
            # Restore primary filament
            if job.filament_id and job.filament_used:
                filament = session.query(Filament).filter_by(id=job.filament_id).first()
                if filament:
                    filament.quantity_remaining += job.filament_used
                    restored_filaments.append((job.filament_id, job.filament_used))
                    print(f"Restored {job.filament_used}g to filament ID {job.filament_id}")
            
            # Restore secondary filaments if they exist
            if job.filament_id_2 and job.filament_used_2:
                filament2 = session.query(Filament).filter_by(id=job.filament_id_2).first()
                if filament2:
                    filament2.quantity_remaining += job.filament_used_2
                    restored_filaments.append((job.filament_id_2, job.filament_used_2))
                    print(f"Restored {job.filament_used_2}g to filament ID {job.filament_id_2}")
            
            if job.filament_id_3 and job.filament_used_3:
                filament3 = session.query(Filament).filter_by(id=job.filament_id_3).first()
                if filament3:
                    filament3.quantity_remaining += job.filament_used_3
                    restored_filaments.append((job.filament_id_3, job.filament_used_3))
                    print(f"Restored {job.filament_used_3}g to filament ID {job.filament_id_3}")
            
            if job.filament_id_4 and job.filament_used_4:
                filament4 = session.query(Filament).filter_by(id=job.filament_id_4).first()
                if filament4:
                    filament4.quantity_remaining += job.filament_used_4
                    restored_filaments.append((job.filament_id_4, job.filament_used_4))
                    print(f"Restored {job.filament_used_4}g to filament ID {job.filament_id_4}")
            
            # Store job information for reporting
            job_info = {
                'id': job.id,
                'project_name': job.project_name,
                'restored_filaments': restored_filaments,
                'total_restored': sum(amount for _, amount in restored_filaments)
            }
                
            # Delete the print job
            session.delete(job)
            session.commit()
            
            # Return information about the deleted job and restored filaments
            return job_info
            
        except Exception as e:
            session.rollback()
            print(f"Error in delete_print_job: {str(e)}")
            raise e
        finally:
            session.close()
            
    # Ideal Inventory operations
    def set_ideal_filament_quantity(self, filament_type, color, brand, ideal_quantity):
        """Set the ideal quantity for a specific filament type/color/brand."""
        session = self.Session()
        try:
            # Check if record already exists
            existing = session.query(FilamentIdealInventory).filter_by(
                type=filament_type,
                color=color,
                brand=brand
            ).first()
            
            if existing:
                # Update existing record
                existing.ideal_quantity = ideal_quantity
                print(f"Updated ideal quantity for {filament_type} {color} {brand}: {ideal_quantity}g")
            else:
                # Create new record
                new_ideal = FilamentIdealInventory(
                    type=filament_type,
                    color=color,
                    brand=brand,
                    ideal_quantity=ideal_quantity
                )
                session.add(new_ideal)
                print(f"Created new ideal quantity for {filament_type} {color} {brand}: {ideal_quantity}g")
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            print(f"Error setting ideal quantity: {str(e)}")
            raise e
        finally:
            session.close()
            
    def get_ideal_filament_quantities(self):
        """Get all ideal filament quantities."""
        session = self.Session()
        try:
            return session.query(FilamentIdealInventory).all()
        finally:
            session.close()
            
    def get_ideal_filament_quantity(self, filament_type, color, brand):
        """Get the ideal quantity for a specific filament."""
        session = self.Session()
        try:
            ideal = session.query(FilamentIdealInventory).filter_by(
                type=filament_type,
                color=color,
                brand=brand
            ).first()
            return ideal.ideal_quantity if ideal else 0
        finally:
            session.close()
            
    def get_inventory_status(self):
        """Get the comparison between current and ideal inventory levels."""
        session = self.Session()
        try:
            # Get the current aggregated inventory
            current_inventory = self.get_aggregated_filament_inventory()
            
            # Get the ideal inventory quantities from the database
            ideal_inventory = session.query(FilamentIdealInventory).all()
            
            # Convert ideal inventory to a dictionary for easier lookup
            ideal_dict = {
                (item.type, item.color, item.brand): item.ideal_quantity 
                for item in ideal_inventory
            }
            
            # Get filament link groups for combined view
            link_groups = self.get_filament_link_groups()
            
            # Process link groups first
            inventory_status = []
            processed_filaments = set()  # To track which filaments have been processed in groups
            
            # Process linked filament groups
            for group in link_groups:
                if not group.filament_links:
                    continue  # Skip empty groups
                    
                # Get all filaments in this group
                group_filaments = []
                total_current_quantity = 0
                
                for link in group.filament_links:
                    key = (link.type, link.color, link.brand)
                    processed_filaments.add(key)  # Mark as processed
                    
                    # Find this filament in current inventory
                    for item in current_inventory:
                        if item['type'] == link.type and item['color'] == link.color and item['brand'] == link.brand:
                            group_filaments.append(item)
                            total_current_quantity += item['quantity_remaining']
                            break
                
                # Calculate combined stats
                if group_filaments:
                    # Use the group's ideal quantity
                    ideal_qty = group.ideal_quantity
                    
                    # Calculate difference and percentage
                    diff = total_current_quantity - ideal_qty
                    
                    # Calculate percentage only if ideal_qty is not zero
                    if ideal_qty > 0:
                        percentage = (total_current_quantity / ideal_qty * 100)
                    else:
                        percentage = None
                    
                    # Create group status entry
                    group_status = {
                        'is_group': True,
                        'group_id': group.id,
                        'group_name': group.name or "Unknown Group",  # Use group name or default if None
                        'name': group.name or "Unknown Group",  # For backward compatibility
                        'type': group.name or "Unknown Group",  # Use group name for type instead of concatenating all filament types
                        'color': '',    # Empty for groups
                        'brand': '',    # Empty for groups
                        'current_quantity': total_current_quantity,
                        'ideal_quantity': ideal_qty,
                        'difference': diff,
                        'percentage': percentage,
                        'spool_count': sum(item.get('spool_count', 0) for item in group_filaments),
                        'filaments': group_filaments
                    }
                    
                    inventory_status.append(group_status)
            
            # Process individual filaments (not in any group)
            for item in current_inventory:
                filament_key = (item['type'], item['color'], item['brand'])
                
                # Skip if this filament was already processed in a group
                if filament_key in processed_filaments:
                    continue
                    
                # Use the individually set ideal quantity for this filament
                ideal_qty = ideal_dict.get(filament_key, 0)
                
                # Calculate difference and percentage
                diff = item['quantity_remaining'] - ideal_qty
                
                # Calculate percentage only if ideal_qty is not zero
                if ideal_qty > 0:
                    percentage = (item['quantity_remaining'] / ideal_qty * 100)
                else:
                    # If ideal_qty is 0, set percentage to None to indicate it's not applicable
                    percentage = None
                
                status = {
                    'is_group': False,
                    'type': item['type'],
                    'color': item['color'],
                    'brand': item['brand'],
                    'current_quantity': item['quantity_remaining'],
                    'ideal_quantity': ideal_qty,
                    'difference': diff,
                    'percentage': percentage,
                    'spool_count': item['spool_count']
                }
                
                inventory_status.append(status)
                
            # Add any ideal inventory items that aren't in current inventory (completely out of stock)
            for key, ideal_qty in ideal_dict.items():
                if not any(item['type'] == key[0] and item['color'] == key[1] and item['brand'] == key[2] 
                          for item in current_inventory) and key not in processed_filaments:
                    inventory_status.append({
                        'is_group': False,
                        'type': key[0],
                        'color': key[1],
                        'brand': key[2],
                        'current_quantity': 0,
                        'ideal_quantity': ideal_qty,
                        'difference': -ideal_qty,
                        'percentage': None,
                        'spool_count': 0
                    })
            
            return inventory_status
        finally:
            session.close()
            
    # Filament Link Group operations
    def create_filament_link_group(self, name, description=None, ideal_quantity=0):
        """Create a new filament link group."""
        session = self.Session()
        try:
            group = FilamentLinkGroup(
                name=name,
                description=description,
                ideal_quantity=ideal_quantity
            )
            session.add(group)
            session.commit()
            return group.id
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def update_filament_link_group(self, group_id, name=None, description=None, ideal_quantity=None):
        """Update a filament link group."""
        session = self.Session()
        try:
            group = session.query(FilamentLinkGroup).filter_by(id=group_id).first()
            if not group:
                raise ValueError(f"No filament link group found with ID {group_id}")
            
            if name is not None:
                group.name = name
            if description is not None:
                group.description = description
            if ideal_quantity is not None:
                group.ideal_quantity = ideal_quantity
                
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def delete_filament_link_group(self, group_id):
        """Delete a filament link group."""
        session = self.Session()
        try:
            group = session.query(FilamentLinkGroup).filter_by(id=group_id).first()
            if not group:
                raise ValueError(f"No filament link group found with ID {group_id}")
                
            session.delete(group)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def add_filament_to_link_group(self, group_id, filament_type, color, brand):
        """Add a filament to a link group."""
        session = self.Session()
        try:
            # Check if group exists
            group = session.query(FilamentLinkGroup).filter_by(id=group_id).first()
            if not group:
                raise ValueError(f"No filament link group found with ID {group_id}")
            
            # Check if this filament is already in another group
            existing_link = session.query(FilamentLink).filter_by(
                type=filament_type, color=color, brand=brand
            ).first()
            
            if existing_link:
                if existing_link.group_id != group_id:
                    raise ValueError(f"Filament {filament_type} {color} {brand} is already in another group")
                return True  # Already in this group
            
            # Add the filament to the group
            link = FilamentLink(
                group_id=group_id,
                type=filament_type,
                color=color,
                brand=brand
            )
            session.add(link)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def remove_filament_from_link_group(self, group_id, filament_type, color, brand):
        """Remove a filament from a link group."""
        session = self.Session()
        try:
            link = session.query(FilamentLink).filter_by(
                group_id=group_id,
                type=filament_type,
                color=color,
                brand=brand
            ).first()
            
            if not link:
                raise ValueError(f"Filament {filament_type} {color} {brand} not found in group {group_id}")
                
            session.delete(link)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()
    
    def get_filament_link_groups(self):
        """Get all filament link groups with their linked filaments."""
        session = self.Session()
        try:
            return session.query(FilamentLinkGroup).options(
                joinedload(FilamentLinkGroup.filament_links)
            ).all()
        finally:
            session.close()
    
    def get_filament_link_group(self, group_id):
        """Get a specific filament link group with its linked filaments."""
        session = self.Session()
        try:
            return session.query(FilamentLinkGroup).options(
                joinedload(FilamentLinkGroup.filament_links)
            ).filter_by(id=group_id).first()
        finally:
            session.close()

    def update_full_print_job(self, job_id, date=None, duration=None, 
                       filament_id=None, filament_used=None,
                       filament_id_2=None, filament_used_2=None,
                       filament_id_3=None, filament_used_3=None,
                       filament_id_4=None, filament_used_4=None):
        """Update all fields of an existing print job except for failure status.
        
        This method updates detailed information about a print job but does not handle
        the filament restoration logic for failed prints, which is handled separately
        by the update_print_job method.
        
        Args:
            job_id: ID of the print job to update
            date: New date/time for the print job
            duration: New duration in hours
            filament_id: Primary filament ID
            filament_used: Amount of primary filament used
            filament_id_2: Secondary filament 1 ID
            filament_used_2: Amount of secondary filament 1 used
            filament_id_3: Secondary filament 2 ID
            filament_used_3: Amount of secondary filament 2 used
            filament_id_4: Secondary filament 3 ID
            filament_used_4: Amount of secondary filament 3 used
            
        Returns:
            Dictionary with information about the updated job
        """
        session = self.Session()
        try:
            job = session.query(PrintJob).filter_by(id=job_id).first()
            if not job:
                raise ValueError(f"No print job found with ID {job_id}")
            
            # Update job fields if provided
            if date is not None:
                job.date = date
                
            if duration is not None:
                job.duration = duration
            
            # Update filament fields if provided
            if filament_id is not None:
                job.filament_id = filament_id
                
            if filament_used is not None:
                job.filament_used = filament_used
            
            # Update secondary filament fields if provided
            if filament_id_2 is not None:
                job.filament_id_2 = filament_id_2
                
            if filament_used_2 is not None:
                job.filament_used_2 = filament_used_2
                
            if filament_id_3 is not None:
                job.filament_id_3 = filament_id_3
                
            if filament_used_3 is not None:
                job.filament_used_3 = filament_used_3
                
            if filament_id_4 is not None:
                job.filament_id_4 = filament_id_4
                
            if filament_used_4 is not None:
                job.filament_used_4 = filament_used_4
            
            session.commit()
            return {'id': job_id, 'updated': True}
            
        except Exception as e:
            session.rollback()
            print(f"Error in update_full_print_job: {str(e)}")
            raise e
        finally:
            session.close()