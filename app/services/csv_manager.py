# app/services/csv_manager.py
import pandas as pd
from pathlib import Path
from filelock import FileLock, Timeout
from datetime import datetime
import shutil
import logging
from fastapi import HTTPException
from ..config import get_settings
from contextlib import contextmanager

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

settings = get_settings()

class CSVManager:
    def __init__(self):
        self.file_path = Path(settings.CSV_FILE_PATH)
        self.backup_dir = Path(settings.BACKUP_DIR)
        self.lock_path = self.file_path.with_suffix('.lock')
        self.lock = FileLock(str(self.lock_path), timeout=10)  # 10 seconds timeout

        # Ensure directories exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Initialize CSV if it doesn't exist
        if not self.file_path.exists():
            self._create_empty_csv()

    def _create_empty_csv(self):
        """Create an empty CSV file with headers."""
        try:
            with self.lock:
                if not self.file_path.exists():
                    df = pd.DataFrame(columns=[
                        'user', 'broker', 'API key', 'API secret', 
                        'pnl', 'margin', 'max_risk'
                    ])
                    df.to_csv(self.file_path, index=False)
                    logger.info(f"Created new CSV file at {self.file_path}")
        except Exception as e:
            logger.error(f"Failed to create CSV file: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to initialize CSV file"
            )

    @contextmanager
    def atomic_write(self):
        """Context manager for atomic file operations with locking."""
        try:
            with self.lock:
                yield
        except Timeout:
            logger.error("Lock acquisition timed out")
            raise HTTPException(
                status_code=503,
                detail="Service temporarily unavailable. Please try again."
            )
        except Exception as e:
            logger.error(f"Error during atomic write operation: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Internal server error during file operation"
            )

    def backup(self):
        """Create a backup of the CSV file."""
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = self.backup_dir / f"backend_table_{timestamp}.csv"
            
            with self.lock:
                shutil.copy2(self.file_path, backup_path)
                logger.info(f"Created backup at {backup_path}")
                
                # Clean up old backups (keep last 5)
                self._cleanup_old_backups()
                
        except Exception as e:
            logger.error(f"Backup failed: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to create backup"
            )

    def _cleanup_old_backups(self, keep_last=5):
        """Clean up old backup files, keeping only the specified number."""
        try:
            backups = sorted(
                self.backup_dir.glob("backend_table_*.csv"),
                key=lambda x: x.stat().st_mtime
            )
            for backup in backups[:-keep_last]:
                backup.unlink()
                logger.info(f"Deleted old backup: {backup}")
        except Exception as e:
            logger.warning(f"Failed to cleanup old backups: {str(e)}")

    def get_previous_backups(self, count=3) -> list:
        """
        Return a list of the most recent backup file names.
        The list is sorted by modification time (most recent first).
        """
        try:
            backups = sorted(
                self.backup_dir.glob("backend_table_*.csv"),
                key=lambda x: x.stat().st_mtime,
                reverse=True
            )
            # Return the file names of the most recent `count` backups
            return [backup.name for backup in backups[:count]]
        except Exception as e:
            logger.error(f"Error retrieving backups: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to retrieve backups")

    def restore_backup(self, backup_filename: str):
        """
        Restore the main CSV file using the specified backup file.
        """
        backup_path = self.backup_dir / backup_filename
        if not backup_path.exists():
            logger.error(f"Backup file {backup_filename} not found")
            raise HTTPException(status_code=404, detail="Backup file not found")
        try:
            with self.atomic_write():
                shutil.copy2(backup_path, self.file_path)
            logger.info(f"Restored backup from {backup_filename}")
        except Exception as e:
            logger.error(f"Error restoring backup: {str(e)}")
            raise HTTPException(status_code=500, detail="Failed to restore backup")

    def read(self) -> pd.DataFrame:
        """Read the CSV file with proper locking."""
        try:
            with self.lock:
                if not self.file_path.exists():
                    raise FileNotFoundError("CSV file not found")
                return pd.read_csv(self.file_path)
        except FileNotFoundError:
            logger.error("CSV file not found")
            raise HTTPException(
                status_code=404,
                detail="CSV file not found"
            )
        except Exception as e:
            logger.error(f"Error reading CSV: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to read CSV file"
            )

    def write(self, df: pd.DataFrame):
        """Write to CSV file with proper locking and backup."""
        try:
            with self.atomic_write():
                self.backup()  # Create backup before writing
                df.to_csv(self.file_path, index=False)
                logger.info("Successfully wrote to CSV file")
        except Exception as e:
            logger.error(f"Error writing to CSV: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to write to CSV file"
            )

    def update_row(self, index: int, row_data: dict):
        """Update a specific row in the CSV file."""
        try:
            with self.atomic_write():
                df = pd.read_csv(self.file_path)
                if index >= len(df):
                    raise IndexError("Row index out of bounds")
                
                self.backup()  # Create backup before modifying
                for column, value in row_data.items():
                    df.loc[index, column] = value
                    
                df.to_csv(self.file_path, index=False)
                logger.info(f"Successfully updated row {index}")
        except IndexError:
            raise HTTPException(
                status_code=404,
                detail="Row not found"
            )
        except Exception as e:
            logger.error(f"Error updating row: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to update row"
            )

    def delete_row(self, index: int):
        """Delete a specific row from the CSV file."""
        try:
            with self.atomic_write():
                df = pd.read_csv(self.file_path)
                if index >= len(df):
                    raise IndexError("Row index out of bounds")
                
                self.backup()  # Create backup before deleting
                df = df.drop(index)
                df = df.reset_index(drop=True)
                df.to_csv(self.file_path, index=False)
                logger.info(f"Successfully deleted row {index}")
        except IndexError:
            raise HTTPException(
                status_code=404,
                detail="Row not found"
            )
        except Exception as e:
            logger.error(f"Error deleting row: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail="Failed to delete row"
            )

    def __del__(self):
        """Cleanup method to ensure lock file is removed."""
        try:
            if self.lock_path.exists():
                self.lock_path.unlink()
        except Exception as e:
            logger.warning(f"Failed to cleanup lock file: {str(e)}")
