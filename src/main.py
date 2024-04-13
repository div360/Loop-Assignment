from fastapi import FastAPI, BackgroundTasks
from fastapi.responses import JSONResponse, FileResponse
from typing import Dict, Tuple
from sqlalchemy.orm import Session
from src.service import calculate_uptime_downtime, formatted_results
from src.database import get_store_ids
from src.models import StoreActivity, StoreReport
from src.database import SessionLocal
from HTTPException import HTTPException
import uuid
from datetime import datetime
import pytz
from fastapi import Response
import csv
from io import StringIO

app = FastAPI()

db = SessionLocal()
@app.post("/trigger_report")
async def trigger_report(background_tasks: BackgroundTasks):
    store_ids = get_store_ids(db)
    reports_ids = []
    for store_id in store_ids:
        report_id = str(uuid.uuid4())
        reports_ids.append(report_id)
        if not db.query(StoreActivity).filter(StoreActivity.store_id == store_id).first():
            continue
        time_string = "2023-01-25 18:13:22.47922"

        current_time = datetime.strptime(time_string, "%Y-%m-%d %H:%M:%S.%f")

        background_tasks.add_task(formatted_results(store_id, report_id, current_time, db), store_id, report_id)
    return {"report_ids": reports_ids}

@app.get("/get_report")
async def get_report(report_id: str):
    
    report_data = db.query(StoreReport).filter(StoreReport.report_id == report_id).first()
    if not report_data:
        return {"status": "Running"}
        
    csv_output = StringIO() 
    csv_writer = csv.writer(csv_output)

    csv_writer.writerow(report_data.keys())
    csv_writer.writerow(report_data.values())

    response = Response(content=csv_output.getvalue(), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=report_{report_id}.csv"
    return response
