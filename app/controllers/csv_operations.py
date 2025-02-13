# app/controllers/csv_operations.py
import pandas as pd
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from pydantic import BaseModel
from ..services.csv_manager import CSVManager
from ..database import get_db
from ..controllers.auth import get_current_user
from ..models.user import UserSession

router = APIRouter()
csv_manager = CSVManager()

@router.get("/csv")
async def read_csv(
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Get CSV data. Requires authentication.
    """
    return csv_manager.read().to_dict('records')

@router.post("/csv")
async def create_csv_entry(
    data: dict,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create new CSV entry. Requires authentication.
    """
    df = csv_manager.read()
    new_row = pd.DataFrame([data])
    df = pd.concat([df, new_row], ignore_index=True)
    
    csv_manager.write(df)
    return {"message": "Successfully wrote to CSV"}

@router.put("/csv/{row_id}")
async def update_csv_entry(
    row_id: int,
    data: dict,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update CSV entry. Requires authentication.
    """
    csv_manager.update_row(row_id, data)
    return {"message": f"Successfully updated row {row_id}"}

@router.delete("/csv/{row_id}")
async def delete_csv_entry(
    row_id: int,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Delete CSV entry. Requires authentication.
    """
    csv_manager.delete_row(row_id)
    return {"message": f"Successfully deleted row {row_id}"}

@router.get("/csv/backups")
async def list_backups(
    count: int = Query(5, description="Number of recent backups to retrieve"),
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Return a list of the most recent backup file names.
    """
    backups = csv_manager.get_previous_backups(count)
    return {"backups": backups}

class RestoreBackupRequest(BaseModel):
    backup_filename: str

@router.post("/csv/restore")
async def restore_csv_backup(
    request: RestoreBackupRequest,
    current_user: UserSession = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Restore the main CSV file using the specified backup.
    """
    print(request);
    csv_manager.restore_backup(request.backup_filename)
    return {"message": f"Successfully restored backup {request.backup_filename}"}
