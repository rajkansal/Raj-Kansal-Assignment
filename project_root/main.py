from fastapi import FastAPI, UploadFile, File, Depends, HTTPException, Form
from sqlalchemy.orm import Session
from database import get_db, init_db
from models import ImageProcessingRequest
from tasks import process_images
from utils import parse_csv
import os

app = FastAPI()

# Run database initialization on startup
@app.on_event("startup")
def startup_event():
    init_db()  # This will create tables if they don't exist

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), webhook_url: str = Form(None), db: Session = Depends(get_db)):
    # Ensure the uploaded file is a CSV
    if not file.filename.endswith(".csv"):
        raise HTTPException(status_code=400, detail="Only CSV files are allowed.")
    request_id, data = parse_csv(file)

    for entry in data:
        db_entry = ImageProcessingRequest(
            request_id=request_id,
            product_name=entry["product_name"],
            input_urls=entry["input_urls"],
            status="pending",
            webhook_url=webhook_url
        )
        db.add(db_entry)
    
    db.commit()

    # Trigger asynchronous image processing
    process_images.delay(request_id, webhook_url)

    return {"request_id": request_id, "message": "File uploaded successfully"}

@app.get("/status/{request_id}")
async def check_status(request_id: str, db: Session = Depends(get_db)):
    request_entry = db.query(ImageProcessingRequest).filter_by(request_id=request_id).first()
    if not request_entry:
        return {"error": "Request ID not found"}
    return {
        "request_id": request_entry.request_id,
        "status": request_entry.status
    }
