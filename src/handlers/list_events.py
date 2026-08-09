from boto3.dynamodb.conditions import Key

from common.db import table
from common.responses import build_response


def _get_registration_count(event_id):
    """Counts registrations for one event via Query, not Scan -
    this is the payoff of the single-table PK/SK design from Step 2."""
    response = table.query(
        KeyConditionExpression=Key("PK").eq(f"EVENT#{event_id}") & Key("SK").begins_with("REG#"),
        Select="COUNT"
    )
    return response.get("Count", 0)


def _compute_status(registered, capacity):
    if registered >= capacity:
        return "Full"
    if registered >= capacity * 0.8:
        return "Limited"
    return "Available"


def lambda_handler(event, context):
    """
    GET /events
    Queries the GSI1 index for all items where GSI1PK = "EVENT",
    then enriches each with a live registration count and status.
    """
    response = table.query(
        IndexName="GSI1",
        KeyConditionExpression=Key("GSI1PK").eq("EVENT")
    )

    events = []
    for item in response.get("Items", []):
        registered = _get_registration_count(item["eventId"])
        events.append({
            "eventId": item["eventId"],
            "eventName": item["eventName"],
            "eventDate": item["eventDate"],
            "capacity": item["capacity"],
            "registered": registered,
            "status": _compute_status(registered, item["capacity"])
        })

    return build_response(200, {"events": events})
