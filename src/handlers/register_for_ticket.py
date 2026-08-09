import json
import os
from datetime import datetime, timezone

import boto3
from botocore.exceptions import ClientError
from boto3.dynamodb.conditions import Key

from common.db import table
from common.responses import build_response

# TOPIC_ARN is only set once SNS is wired up in a later step.
# Its absence should never break registration - confirmation email is a nice-to-have, not core logic.
TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN")
sns = boto3.client("sns") if TOPIC_ARN else None


def lambda_handler(event, context):
    """
    POST /events/{eventId}/register
    Body: { "email": str, "participantName": str }
    """
    event_id = event.get("pathParameters", {}).get("eventId")
    if not event_id:
        return build_response(400, {"error": "eventId is required in the path"})

    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return build_response(400, {"error": "Request body must be valid JSON"})

    email = body.get("email")
    participant_name = body.get("participantName")

    if not email or not participant_name:
        return build_response(400, {"error": "email and participantName are required"})

    # 1. Confirm the event exists before allowing a registration against it
    event_item = table.get_item(Key={"PK": f"EVENT#{event_id}", "SK": "METADATA"}).get("Item")
    if not event_item:
        return build_response(404, {"error": "Event not found"})

    # 2. Enforce capacity - count current registrations first
    count_response = table.query(
        KeyConditionExpression=Key("PK").eq(f"EVENT#{event_id}") & Key("SK").begins_with("REG#"),
        Select="COUNT"
    )
    if count_response.get("Count", 0) >= event_item["capacity"]:
        return build_response(409, {"error": "Event is at full capacity"})

    # 3. Write the registration, using a condition expression so a duplicate
    #    email can never overwrite an existing registration (race-safe, unlike a plain check-then-write)
    try:
        table.put_item(
            Item={
                "PK": f"EVENT#{event_id}",
                "SK": f"REG#{email}",
                "eventId": event_id,
                "email": email,
                "participantName": participant_name,
                "registeredAt": datetime.now(timezone.utc).isoformat()
            },
            ConditionExpression="attribute_not_exists(SK)"
        )
    except ClientError as e:
        if e.response["Error"]["Code"] == "ConditionalCheckFailedException":
            return build_response(409, {"error": "This email is already registered for this event"})
        raise

    # 4. Best-effort confirmation notification - failure here shouldn't fail the registration itself
    if sns:
        try:
            sns.publish(
                TopicArn=TOPIC_ARN,
                Subject=f"Registration confirmed: {event_item['eventName']}",
                Message=(
                    f"Hi {participant_name},\n\n"
                    f"You're registered for {event_item['eventName']} on {event_item['eventDate']}.\n"
                )
            )
        except ClientError:
            pass  # logged automatically via CloudWatch; doesn't block the API response

    return build_response(201, {"message": "Registration successful", "eventId": event_id, "email": email})
