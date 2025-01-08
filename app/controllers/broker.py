from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from typing import List
from ..database import get_db
from ..services.broker_service import BrokerService
from ..schemas.broker_data import BrokerDataCreate, BrokerDataUpdate, BrokerDataResponse
from ..controllers.auth import get_current_user

router = APIRouter()

@router.get("/brokers/", response_model=List[BrokerDataResponse])
async def get_all_records(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return BrokerService.get_all_records(db)

@router.get("/brokers/{user}", response_model=BrokerDataResponse)
async def get_record(
    user: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    record = BrokerService.get_record_by_user(db, user)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.post("/brokers/", response_model=BrokerDataResponse)
async def create_record(
    data: BrokerDataCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return BrokerService.create_record(db, data)

@router.put("/brokers/{user}", response_model=BrokerDataResponse)
async def update_record(
    user: str,
    data: BrokerDataUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    record = BrokerService.update_record(db, user, data)
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
    return record

@router.delete("/brokers/{user}")
async def delete_record(
    user: str,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    success = BrokerService.delete_record(db, user)
    if not success:
        raise HTTPException(status_code=404, detail="Record not found")
    return {"message": "Record deleted successfully"}

@router.post("/brokers/upload-csv")
async def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    try:
        contents = await file.read()
        with open("temp_upload.csv", "wb") as f:
            f.write(contents)
        records = BrokerService.load_csv_to_db(db, "temp_upload.csv")
        return {"message": f"Successfully loaded {len(records)} records"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        import os
        if os.path.exists("temp_upload.csv"):
            os.remove("temp_upload.csv")

@router.get("/brokers/statistics/summary")
async def get_statistics(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    return BrokerService.get_broker_statistics(db)