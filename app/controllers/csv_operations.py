# app/controllers/csv_operations.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
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
    df = df.append(data, ignore_index=True)
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