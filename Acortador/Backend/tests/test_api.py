import uuid
from fastapi import status


def test_root_endpoint(client):
    """Test the root information endpoint."""
    response = client.get("/")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "online"
    assert "endpoints" in data


def test_health_check_endpoint(client):
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["status"] == "healthy"
    assert "connected" in data["dynamodb_status"]


def test_shorten_url_success(client, mock_table):
    """Test creating a shortened URL successfully."""
    original_url = "https://www.example.com/articulos/arquitectura-cloud"
    response = client.post("/shorten", json={"original_url": original_url})

    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert "short_code" in data
    assert data["original_url"] == original_url
    assert "short_url" in data

    # Verify UUID format
    short_code = data["short_code"]
    parsed_uuid = uuid.UUID(short_code)
    assert str(parsed_uuid) == short_code

    # Verify short_url contains the short_code
    assert short_code in data["short_url"]

    # Verify DynamoDB stored the item
    assert short_code in mock_table.items
    stored_item = mock_table.items[short_code]
    assert stored_item["original_url"] == original_url
    assert "created_at" in stored_item


def test_shorten_url_invalid(client):
    """Test validating malformed URLs."""
    # Not starting with http or https
    response = client.post("/shorten", json={"original_url": "ftp://example.com/file"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Plain text without protocol
    response = client.post("/shorten", json={"original_url": "not-a-valid-url"})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    # Missing field
    response = client.post("/shorten", json={})
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_redirect_to_original_url(client, mock_table):
    """Test HTTP 307 Temporary Redirect to original URL."""
    # Pre-populate table
    test_code = str(uuid.uuid4())
    target_url = "https://www.google.com/search?q=fastapi"
    mock_table.put_item({
        "short_code": test_code,
        "original_url": target_url,
        "created_at": "2026-10-29T20:00:00Z"
    })

    # Test client redirect with follow_redirects=False to assert 307
    response = client.get(f"/{test_code}", follow_redirects=False)
    assert response.status_code == status.HTTP_307_TEMPORARY_REDIRECT
    assert response.headers["location"] == target_url


def test_redirect_nonexistent_returns_404(client):
    """Test redirecting for non-existent code returns 404."""
    non_existent = str(uuid.uuid4())
    response = client.get(f"/{non_existent}", follow_redirects=False)
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "no existe" in response.json()["detail"].lower()


def test_get_url_info_success(client, mock_table):
    """Test retrieving URL metadata with GET /urls/{short_code}."""
    test_code = str(uuid.uuid4())
    target_url = "https://aws.amazon.com/dynamodb/"
    created_at = "2026-10-29T20:30:00Z"

    mock_table.put_item({
        "short_code": test_code,
        "original_url": target_url,
        "created_at": created_at
    })

    response = client.get(f"/urls/{test_code}")
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["short_code"] == test_code
    assert data["original_url"] == target_url
    assert data["created_at"] == created_at
    assert test_code in data["short_url"]


def test_get_url_info_not_found(client):
    """Test GET /urls/{short_code} with non-existent code returns 404."""
    non_existent = str(uuid.uuid4())
    response = client.get(f"/urls/{non_existent}")
    assert response.status_code == status.HTTP_404_NOT_FOUND
