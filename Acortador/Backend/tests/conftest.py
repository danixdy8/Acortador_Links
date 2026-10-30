import pytest
from unittest.mock import MagicMock, patch
from fastapi.testclient import TestClient

from app.main import app


class InMemoryDynamoDBTable:
    """Simulates DynamoDB Table in-memory for testing."""

    def __init__(self):
        self.items = {}
        self.table_status = "ACTIVE"

    def load(self):
        return True

    def put_item(self, Item):
        short_code = Item["short_code"]
        self.items[short_code] = dict(Item)
        return {"ResponseMetadata": {"HTTPStatusCode": 200}}

    def get_item(self, Key):
        short_code = Key.get("short_code")
        if short_code in self.items:
            return {"Item": dict(self.items[short_code])}
        return {}


@pytest.fixture
def mock_table():
    """Provides a fresh in-memory table fixture."""
    return InMemoryDynamoDBTable()


@pytest.fixture
def client(mock_table):
    """FastAPI TestClient with DynamoDB table mocked in-memory."""
    with patch("app.services.get_url_table", return_value=mock_table), \
         patch("app.database.get_url_table", return_value=mock_table):
        with TestClient(app) as test_client:
            yield test_client
