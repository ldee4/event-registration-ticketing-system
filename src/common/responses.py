import json
from decimal import Decimal


class DecimalEncoder(json.JSONEncoder):
    """DynamoDB returns numeric attributes as Decimal, which json.dumps
    can't serialize by default. This converts them to int/float on the way out."""
    def default(self, obj):
        if isinstance(obj, Decimal):
            return int(obj) if obj % 1 == 0 else float(obj)
        return super().default(obj)


def build_response(status_code, body):
    """Every Lambda returns through this so API Gateway proxy integration
    gets a consistently-shaped response, with CORS enabled for the frontend."""
    return {
        "statusCode": status_code,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type",
            "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
        },
        "body": json.dumps(body, cls=DecimalEncoder)
    }
