import os
import boto3

# TABLE_NAME is injected as a Lambda environment variable by the SAM template,
# so this code never hardcodes the table name and works the same in every stage (dev/prod).
TABLE_NAME = os.environ.get("TABLE_NAME", "EventRegistrationTable")

dynamodb = boto3.resource("dynamodb")
table = dynamodb.Table(TABLE_NAME)
