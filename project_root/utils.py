import csv
import uuid
from fastapi import HTTPException

def parse_csv(file):
    try:
        # Read file and split lines
        decoded_content = file.file.read().decode("utf-8").splitlines()
        reader = csv.reader(decoded_content)

        # Validate header row
        expected_header = ["S. No.", "Product Name", "Input Image Urls"]
        header = next(reader, None)  # Read the first line as the header

        if header is None or header != expected_header:
            raise HTTPException(status_code=400, detail="Invalid CSV header. Expected: 'S. No.', 'Product Name', 'Input Image Urls'")

        request_id = str(uuid.uuid4())
        data = []

        # Process each row
        for row in reader:
            if len(row) != 3:
                raise HTTPException(status_code=400, detail=f"Invalid row format: {row}. Expected 3 columns.")

            s_no, product_name, input_urls = row  # Unpack values

            # Ensure S. No. is a number
            if not s_no.isdigit():
                raise HTTPException(status_code=400, detail=f"Invalid S. No. value: {s_no}. It must be a number.")

            # Ensure input_urls are not empty
            input_urls_list = [url.strip() for url in input_urls.split(",") if url.strip()]
            if not input_urls_list:
                raise HTTPException(status_code=400, detail=f"Invalid Input Image Urls for {product_name}. At least one URL is required.")

            data.append({
                "request_id": request_id,
                "product_name": product_name.strip(),
                "input_urls": input_urls_list
            })

        return request_id, data

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"CSV Parsing Error: {str(e)}")
