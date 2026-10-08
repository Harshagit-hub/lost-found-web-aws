
import json
import boto3
import base64
import uuid
from datetime import datetime

s3 = boto3.client("s3")
dynamodb = boto3.resource("dynamodb")

bucket_name = "lost-found-project"
table = dynamodb.Table("LostFoundItems")


def lambda_handler(event, context):

    # GET request → show website
    if event.get("httpMethod") == "GET":

        with open("index.html", "r", encoding="utf-8") as file:
            html = file.read()

        return {
            "statusCode": 200,
            "headers": {
                "Content-Type": "text/html"
            },
            "body": html
        }


    # POST request → upload report
    try:

        # Get data from API Gateway
        body = json.loads(event["body"])

        item_name = body["itemName"]
        item_type = body["type"]
        category = body["category"]
        description = body["description"]
        location = body["location"]
        date = body["date"]
        contact = body["contact"]

        image_data = body["image"]
        image_name = body["imageName"]


        # Check file type
        allowed_extensions = [".jpg", ".jpeg", ".png"]

        if not any(
            image_name.lower().endswith(ext)
            for ext in allowed_extensions
        ):

            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps(
                    "Only JPG, JPEG and PNG files are allowed"
                )
            }


        # Convert Base64 image to bytes
        image_bytes = base64.b64decode(image_data)


        # Check file size
        file_size = len(image_bytes)

        min_size = 10 * 1024
        max_size = 2 * 1024 * 1024


        if file_size < min_size:

            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps(
                    "File is too small. Minimum size is 10 KB."
                )
            }


        if file_size > max_size:

            return {
                "statusCode": 400,
                "headers": {
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Allow-Headers": "Content-Type",
                    "Access-Control-Allow-Methods": "POST,OPTIONS"
                },
                "body": json.dumps(
                    "File is too large. Maximum size is 2 MB."
                )
            }


        # Create unique image name
        file_name = str(uuid.uuid4()) + "-" + image_name


        # Upload image to S3
        s3.put_object(
            Bucket=bucket_name,
            Key="uploads/" + file_name,
            Body=image_bytes
        )
# Generate unique item ID
        item_id = str(uuid.uuid4())


        # Store details in DynamoDB
        table.put_item(
            Item={
                "itemId": item_id,
                "itemName": item_name,
                "type": item_type,
                "category": category,
                "description": description,
                "location": location,
                "date": date,
                "contact": contact,
                "imageKey": "uploads/" + file_name,
                "createdAt": datetime.utcnow().isoformat()
            }
        )
       # Success response
        return {
            "statusCode": 200,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({
                "message": "Report submitted successfully",
                "itemId": item_id
            })
        }
    except Exception as e:

        # Error response
        return {
            "statusCode": 500,
            "headers": {
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "POST,OPTIONS"
            },
            "body": json.dumps({
                "error": str(e)
            })
        }




        



 
