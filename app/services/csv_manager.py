# app/services/csv_manager.py
import pandas as pd
from pathlib import Path
from filelock import FileLock
import shutil
from datetime import datetime
from ..config import get_settings

settings = get_settings()

class CSVManager:
    def __init__(self):
        self.file_path = Path(settings.CSV_FILE_PATH)
        self.backup_dir = Path(settings.BACKUP_DIR)
        self.lock = FileLock(str(self.file_path) + ".lock")

        # Ensure directories exist
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.backup_dir.mkdir(parents=True, exist_ok=True)

        # Create CSV if it doesn't exist
        if not self.file_path.exists():
            df = pd.DataFrame(columns=['user', 'broker', 'API key', 'API secret', 'pnl', 'margin', 'max_risk'])
            df.to_csv(self.file_path, index=False)

    def backup(self):
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = self.backup_dir / f"backend_table_{timestamp}.csv"
        shutil.copy2(self.file_path, backup_path)

    def read(self) -> pd.DataFrame:
        with self.lock:
            return pd.read_csv(self.file_path)

    def write(self, df: pd.DataFrame):
        with self.lock:
            self.backup()
            df.to_csv(self.file_path, index=False)