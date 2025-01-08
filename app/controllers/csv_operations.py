from fastapi import APIRouter, Depends, HTTPException
from ..services.csv_manager import CSVManager
from ..controllers.auth import get_current_user
from typing import List, Dict, Any

router = APIRouter()
csv_manager = CSVManager()

@router.get("/csv")
async def get_csv(current_user = Depends(get_current_user)) -> List[Dict[str, Any]]:
    df = csv_manager.read()
    return df.to_dict('records')

@router.post("/csv")
async def create_row(
    row: Dict[str, Any],
    current_user = Depends(get_current_user)
):
    df = csv_manager.read()
    if row['id'] in df['id'].values:
        raise HTTPException(status_code=400, detail="ID already exists")
    
    df = df.append(row, ignore_index=True)
    csv_manager.write(df)
    return {"message": "Row created successfully"}
