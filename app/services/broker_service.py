from sqlalchemy.orm import Session
from ..models.broker_data import BrokerData
from ..schemas.broker_data import BrokerDataCreate, BrokerDataUpdate
from fastapi import HTTPException
import pandas as pd
from typing import List, Optional

class BrokerService:
    @staticmethod
    def get_all_records(db: Session) -> List[BrokerData]:
        return db.query(BrokerData).all()

    @staticmethod
    def get_record_by_user(db: Session, user: str) -> Optional[BrokerData]:
        return db.query(BrokerData).filter(BrokerData.user == user).first()

    @staticmethod
    def create_record(db: Session, data: BrokerDataCreate) -> BrokerData:
        db_record = BrokerData(**data.dict())
        db.add(db_record)
        try:
            db.commit()
            db.refresh(db_record)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return db_record

    @staticmethod
    def update_record(
        db: Session, 
        user: str, 
        data: BrokerDataUpdate
    ) -> Optional[BrokerData]:
        db_record = BrokerService.get_record_by_user(db, user)
        if not db_record:
            return None

        for key, value in data.dict(exclude_unset=True).items():
            setattr(db_record, key, value)

        try:
            db.commit()
            db.refresh(db_record)
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return db_record

    @staticmethod
    def delete_record(db: Session, user: str) -> bool:
        db_record = BrokerService.get_record_by_user(db, user)
        if not db_record:
            return False

        db.delete(db_record)
        try:
            db.commit()
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))
        return True

    @staticmethod
    def load_csv_to_db(db: Session, csv_path: str) -> List[BrokerData]:
        try:
            df = pd.read_csv(csv_path)
            records = []
            for _, row in df.iterrows():
                data = BrokerDataCreate(**row.to_dict())
                record = BrokerService.create_record(db, data)
                records.append(record)
            return records
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Failed to load CSV: {str(e)}")

    @staticmethod
    def get_broker_statistics(db: Session):
        records = BrokerService.get_all_records(db)
        df = pd.DataFrame([{
            'broker': r.broker,
            'pnl': r.pnl,
            'margin': r.margin,
            'max_risk': r.max_risk
        } for r in records])
        
        return {
            'broker_summary': df.groupby('broker').agg({
                'pnl': ['mean', 'sum'],
                'margin': ['mean', 'sum'],
                'max_risk': ['mean', 'max']
            }).to_dict(),
            'total_pnl': df['pnl'].sum(),
            'total_margin': df['margin'].sum(),
            'avg_max_risk': df['max_risk'].mean()
        }