from boto3.dynamodb.conditions import Key

from common.db import table
from common.responses import build_response


def lambda_handler(event, context):
    """
    GET /events/{eventId}/registrations
    Returns every participant registered for the given event.
    """
    event_id = event.get("pathParameters", {}).get("eventId")
    if not event_id:
        return build_response(400, {"error": "eventId is required in the path"})

    # Confirm the event exists so callers get a clean 404 instead of an empty list
    event_item = table.get_item(Key={"PK": f"EVENT#{event_id}", "SK": "METADATA"}).get("Item")
    if not event_item:
        return build_response(404, {"error": "Event not found"})

    response = table.query(
        KeyConditionExpression=Key("PK").eq(f"EVENT#{event_id}") & Key("SK").begins_with("REG#")
    )

    registrations = [
        {
            "email": item["email"],
            "participantName": item["participantName"],
            "registeredAt": item["registeredAt"]
        }
        for item in response.get("Items", [])
    ]

    return build_response(200, {
        "eventId": event_id,
        "eventName": event_item["eventName"],
        "registrations": registrations
    })
