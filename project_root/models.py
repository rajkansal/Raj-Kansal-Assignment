from sqlalchemy import Column, Integer, String, JSON
from database import Base

class ImageProcessingRequest(Base):
    __tablename__ = "image_requests"

    id = Column(Integer, primary_key=True, autoincrement=True)  # SERIAL in SQL
    request_id = Column(String, nullable=False, index=True)  # Not unique!
    status = Column(String(20), nullable=False, default="pending")  # VARCHAR(20)
    product_name = Column(String(255), nullable=False)  # VARCHAR(255)
    input_urls = Column(JSON, nullable=False)  # JSON field
    output_urls = Column(JSON, nullable=False, default="[]")  # JSON field, default to empty array
    webhook_url = Column(String, nullable=True)  # Optional webhook URL
