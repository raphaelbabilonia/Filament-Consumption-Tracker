"""
Database handler module for managing database operations.
"""
import os
import datetime
from sqlalchemy import create_engine, func
from sqlalchemy.orm import sessionmaker, scoped_session, joinedload
from models.schema import Base, Filament, Printer, PrinterComponent, PrintJob

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
    
    # Filament operations
    def add_filament(self, filament_type, color, brand, spool_weight, quantity_remaining=None, price=None):
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
                purchase_date=datetime.datetime.now()
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
    def add_printer(self, name, model=None, notes=None):
        """Add a new printer to the database."""
        session = self.Session()
        try:
            printer = Printer(
                name=name,
                model=model,
                purchase_date=datetime.datetime.now(),
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
    
    def update_printer(self, printer_id, name=None, model=None, notes=None):
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
            query = session.query(PrinterComponent)
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
    
    # Print job operations
    def add_print_job(self, project_name, filament_id, printer_id, filament_used, duration, notes=None):
        """Add a new print job to the database."""
        session = self.Session()
        try:
            # Check if filament exists
            filament = session.query(Filament).filter_by(id=filament_id).first()
            if not filament:
                raise ValueError(f"No filament found with ID {filament_id}")
            
            # Check if printer exists
            printer = session.query(Printer).filter_by(id=printer_id).first()
            if not printer:
                raise ValueError(f"No printer found with ID {printer_id}")
            
            # Check if enough filament is available
            if filament.quantity_remaining < filament_used:
                raise ValueError(f"Not enough filament available. Only {filament.quantity_remaining}g remaining.")
            
            # Create print job
            print_job = PrintJob(
                date=datetime.datetime.now(),
                project_name=project_name,
                filament_id=filament_id,
                printer_id=printer_id,
                filament_used=filament_used,
                duration=duration,
                notes=notes
            )
            
            # Update filament quantity
            filament.quantity_remaining -= filament_used
            
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
                joinedload(PrintJob.printer)
            )
            
            if project_name:
                query = query.filter(PrintJob.project_name.like(f"%{project_name}%"))
            if filament_id:
                query = query.filter_by(filament_id=filament_id)
            if printer_id:
                query = query.filter_by(printer_id=printer_id)
            if start_date:
                query = query.filter(PrintJob.date >= start_date)
            if end_date:
                query = query.filter(PrintJob.date <= end_date)
            
            # Execute the query and return all results    
            return query.order_by(PrintJob.date.desc()).all()
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
        """Delete a print job and restore the filament quantity."""
        session = self.Session()
        try:
            # Find the print job
            print_job = session.query(PrintJob).filter_by(id=job_id).first()
            if not print_job:
                raise ValueError(f"No print job found with ID {job_id}")
            
            # Get the filament and printer to restore/update data
            filament = print_job.filament
            printer = print_job.printer
            
            # Restore filament quantity
            filament.quantity_remaining += print_job.filament_used
            
            # Reverse the component usage for all components of this printer
            components = session.query(PrinterComponent).filter_by(printer_id=printer.id).all()
            for component in components:
                component.usage_hours -= print_job.duration
                # Ensure usage hours don't go below zero
                if component.usage_hours < 0:
                    component.usage_hours = 0
            
            # Delete the print job
            session.delete(print_job)
            session.commit()
            return True
        except Exception as e:
            session.rollback()
            raise e
        finally:
            session.close()