import json
import uuid
from datetime import datetime, timezone

from common.db import table
from common.responses import build_response


def lambda_handler(event, context):
    """
    POST /events
    Body: { "eventName": str, "eventDate": "YYYY-MM-DD", "capacity": int }
    Creates the event's metadata item: PK=EVENT#<id>, SK=METADATA
    """
    try:
        body = json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return build_response(400, {"error": "Request body must be valid JSON"})

    event_name = body.get("eventName")
    event_date = body.get("eventDate")
    capacity = body.get("capacity")

    # Fail fast on missing/invalid input before touching DynamoDB
    if not event_name or not event_date or capacity is None:
        return build_response(400, {
            "error": "eventName, eventDate, and capacity are required"
        })

    if not isinstance(capacity, int) or capacity <= 0:
        return build_response(400, {"error": "capacity must be a positive integer"})

    event_id = str(uuid.uuid4())

    item = {
        "PK": f"EVENT#{event_id}",
        "SK": "METADATA",
        "GSI1PK": "EVENT",
        "GSI1SK": event_date,
        "eventId": event_id,
        "eventName": event_name,
        "eventDate": event_date,
        "capacity": capacity,
        "createdAt": datetime.now(timezone.utc).isoformat()
    }

    table.put_item(Item=item)

    return build_response(201, {
        "message": "Event created",
        "eventId": event_id
    })
