import logging
from typing import Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from app.config import settings

logger = logging.getLogger(__name__)


def get_dynamodb_resource() -> Any:
    """
    Creates and returns a Boto3 DynamoDB resource.
    In AWS EC2 with an attached IAM Role, boto3 will automatically use
    the instance profile credentials without requiring hardcoded keys.
    """
    kwargs: dict[str, Any] = {
        "region_name": settings.aws_region
    }

    if settings.dynamodb_endpoint_url:
        kwargs["endpoint_url"] = settings.dynamodb_endpoint_url

    # Only include explicit credentials if configured (e.g. local dev / testing)
    if settings.aws_access_key_id and settings.aws_secret_access_key:
        kwargs["aws_access_key_id"] = settings.aws_access_key_id
        kwargs["aws_secret_access_key"] = settings.aws_secret_access_key
        if settings.aws_session_token:
            kwargs["aws_session_token"] = settings.aws_session_token

    return boto3.resource("dynamodb", **kwargs)


def get_url_table() -> Any:
    """Returns the DynamoDB Table instance configured for URLs."""
    dynamodb = get_dynamodb_resource()
    return dynamodb.Table(settings.dynamodb_table_name)


def check_dynamodb_connection() -> tuple[bool, str]:
    """
    Checks if the DynamoDB table is reachable and exists.
    Returns (True, "connected") or (False, error_message).
    """
    try:
        table = get_url_table()
        # load() refreshes table attributes from DynamoDB
        table.load()
        return True, f"connected (status: {table.table_status})"
    except ClientError as e:
        error_code = e.response.get("Error", {}).get("Code", "Unknown")
        error_msg = e.response.get("Error", {}).get("Message", str(e))
        logger.error("DynamoDB ClientError: %s - %s", error_code, error_msg)
        return False, f"ClientError ({error_code}): {error_msg}"
    except NoCredentialsError:
        logger.error("No AWS credentials or IAM role found.")
        return False, "NoCredentialsError: No AWS credentials or IAM role configured"
    except Exception as e:
        logger.error("Unexpected error connecting to DynamoDB: %s", str(e))
        return False, f"Error: {str(e)}"
