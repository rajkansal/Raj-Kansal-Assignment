import os
import csv
import requests
from PIL import Image
from io import BytesIO
from celery import Celery
from database import SessionLocal
from models import ImageProcessingRequest
import uuid

celery = Celery("tasks", broker="redis://localhost:6379/0")

# Define local processed images directory
BASE_DIR = os.path.abspath(os.path.dirname(__file__))
PROCESSED_IMAGES_DIR = os.path.join(BASE_DIR, "processed_images")
# Ensure directory exists
if not os.path.exists(PROCESSED_IMAGES_DIR):
    os.makedirs(PROCESSED_IMAGES_DIR, exist_ok=True)

@celery.task
def process_images(request_id, webhook_url=None):
    db = SessionLocal()
    request_entries = db.query(ImageProcessingRequest).filter_by(request_id=request_id).all()

    if not request_entries:
        return "Invalid request ID"

    csv_data = [["S. No.", "Product Name", "Input Image Urls", "Output Image Paths"]]

    for index, request_entry in enumerate(request_entries, start=1):
        input_urls = request_entry.input_urls
        output_paths = []

        for url in input_urls:
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()  # Raise error for HTTP failures
                
                img = Image.open(BytesIO(response.content))

                output_filename = f"{uuid.uuid4()}.jpg"
                output_path = os.path.join(PROCESSED_IMAGES_DIR, output_filename)
                
                img.save(output_path, "WEBP", quality=50, optimize=True)
                output_paths.append(output_path)

            except Exception as e:
                print(f"Error processing image from {url}: {e}")
                continue  # Skip this image and move to the next one

        request_entry.output_urls = output_paths
        request_entry.status = "completed"

        csv_data.append([
            index, 
            request_entry.product_name, 
            "\n".join(input_urls), 
            "\n".join(output_paths)
        ])

    db.commit()
    db.close()

    # Save CSV inside processed_images folder
    csv_filename = os.path.join(PROCESSED_IMAGES_DIR, f"{request_id}_output.csv")
    with open(csv_filename, mode="w", newline="") as file:
        writer = csv.writer(file)
        writer.writerows(csv_data)
    
    # Call Webhook if available
    if webhook_url:
        payload = {
            "request_id": request_id,
            "status": "completed",
            "csv_file": csv_filename
        }
        try:
            requests.post(webhook_url, json=payload)
        except requests.exceptions.RequestException as e:
            print(f"Webhook call failed: {e}")


    return {
        "request_id": request_id,
        "status": "completed",
        "csv_file": csv_filename
    }
