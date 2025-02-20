# Image Processing System - Low-Level Design (LLD)

## 1. System Overview
The system processes image data asynchronously from a CSV file. The key functionalities include:

- Uploading a CSV containing product names and image URLs.
- Validating and parsing the CSV file.
- Asynchronously compressing images by 50%.
- Storing the processed images and tracking request status.
- Providing APIs for file upload, status check, and webhook integration.
- Generating an output CSV with original and processed image URLs.

## 2. System Architecture Diagram
![alt text](<Architecture Diagram.png>)

## 3. System Components
### 3.1 API Gateway (FastAPI)
- Handles incoming HTTP requests.
- Exposes endpoints for file upload, status check.
- Sends tasks to Celery workers.

### 3.2 Database (PostgreSQL)
- Stores product names, input image URLs, and processed image URLs.
- Tracks the status of each image processing request.

### 3.3 Celery Workers (Asynchronous Processing)
- Fetches image URLs from the database.
- Downloads and compresses images asynchronously.
- Saves processed images and updates the database.
- Notifies webhook after processing completion.

### 3.4 Webhook Service
- Receives status updates when image processing is completed.
- Logs or further processes the webhook notification.

## 4. Database Schema
### `image_requests` Table

| Column        | Type         | Description                               |
|--------------|-------------|-------------------------------------------|
| id           | INT (PK)     | Unique ID for each request                |
| request_id   | VARCHAR      | Unique ID for each request                |
| status       | VARCHAR      | Current status (`pending`, `processing`, `completed`, `failed`) |
| product_name | TEXT         | Name of the product                       |
| input_urls   | JSON         | List of original image URLs               |
| output_urls  | JSON         | List of compressed image URLs             |
| webhook_url  | TEXT (Optional) | URL to send webhook notifications      |

## 5. API Endpoints
### 5.1 Upload CSV
- **Endpoint:** `POST /upload`
- **Request:** Accepts a CSV file containing product names and image URLs.
- **Validation:**
  - File must be `.csv` format.
  - CSV must not be empty.
  - Must contain required columns: `S. No.`, `Product Name`, `Input Image Urls`.
  - Each row must have valid data (non-empty product name & image URLs).
- **Response:** Returns a unique `request_id`.

### 5.2 Check Status
- **Endpoint:** `GET /status/{request_id}`
- **Functionality:** Checks processing status of the request.
- **Response:**
  ```json
  {
    "request_id": "36977978-8e24-4730-8761-1ca2ce4602bc",
    "status": "completed"
  }
  ```

### 5.3 Webhook Notification
- **Endpoint:** `POST /webhook`
- **Functionality:** Sends notification when image processing is completed.

## 6. Asynchronous Workers Functionality
**Celery Worker Function: `process_images(request_id, webhook_url)`**

#### Functionality:
- Downloads and compresses images.
- Saves processed images.
- Updates request status.
- Calls webhook if available.

## 7. Project Repository Structure
```
project_root/
│── app.py                # FastAPI application
│── tasks.py              # Celery worker tasks
│── models.py             # Database models
│── database.py           # DB connection setup
│── utils.py              # Utility functions (CSV parsing, etc.)
│── webhook_server.py     # Webhook listener
│── requirements.txt      # Dependencies
│── processed_images/     # Compressed images storage
│── .env                  # Environment variables
```

## 8. Postman Collection
### Upload CSV API
- **Endpoint:** `http://127.0.0.1:8000/upload`
- **Request:**
  - Send a CSV file (`image.csv`) via form-data in a `POST` request.
  - Include a webhook URL (`http://localhost:9000/webhook`).
- **Response:** Returns a request ID for tracking.

### Check Status API
- **Endpoint:** `http://127.0.0.1:8000/status/<request_id>`
- **Request:** `GET` request to check the status of an image processing request.
- **Response:**
  ```json
  {
    "request_id": "36977978-8e24-4730-8761-1ca2ce4602bc",
    "status": "completed"
  }
  ```

## 9. Important Commands & Descriptions
### 9.1 Connect to PostgreSQL Database
```bash
psql -U postgres
\c image_db
SELECT * FROM image_requests WHERE request_id='<request_id>';
```

### 9.2 Run Webhook Server
```bash
python3 webhook_server.py
```

### 9.3 Start Celery Worker
```bash
celery -A worker worker --loglevel=info
```

### 9.4 Run FastAPI Application
```bash
uvicorn main:app --reload
```

## 10. Conclusion
This document provides a complete low-level design (LLD) for the image processing system, including its architecture, API documentation, asynchronous worker details, database schema, and project structure. Following these steps ensures smooth deployment and execution of the system.

