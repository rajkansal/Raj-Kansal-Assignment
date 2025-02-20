from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn

app = FastAPI()

# Define the expected payload structure
class WebhookPayload(BaseModel):
    request_id: str
    status: str
    csv_file: str

@app.post("/webhook")
async def receive_webhook(payload: WebhookPayload):
    print(f"Received Webhook Data: {payload}")
    return {"message": "Webhook received successfully"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
