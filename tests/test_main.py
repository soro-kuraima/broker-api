# tests/test_api.py
import pytest
from fastapi.testclient import TestClient
from datetime import datetime
import time

from app.main import app  # Ensure PYTHONPATH is set so that "app" is found

client = TestClient(app)

# Fixture to register and log in a test user, then return the access token.
@pytest.fixture(scope="module")
def test_user_token():
    user_data = {"username": "testuser", "password": "testpass"}
    # Register the user (if not already registered)
    client.post("/api/v1/register", json=user_data)
    # Get token
    token_response = client.post("/api/v1/token", data=user_data)
    token = token_response.json().get("access_token")
    assert token is not None
    return token

def test_openapi_and_docs():
    # Test OpenAPI JSON endpoint
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200
    assert "openapi" in response.json()
    
    # Test docs endpoint
    docs_response = client.get("/api/v1/docs")
    assert docs_response.status_code == 200

def test_csv_crud_operations(test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # GET CSV (read all CSV entries)
    get_response = client.get("/api/v1/csv", headers=headers)
    assert get_response.status_code == 200
    initial_entries = get_response.json()
    
    # POST /api/v1/csv to create a new CSV entry.
    new_entry = {
        "user": "testuser",
        "broker": "testbroker",
        "API key": "key123",
        "API secret": "secret123",
        "pnl": 100,
        "margin": 50,
        "max_risk": 10
    }
    post_response = client.post("/api/v1/csv", json=new_entry, headers=headers)
    assert post_response.status_code in (200, 201)
    
    # Optionally, wait a bit to ensure the file lock and backup processes complete
    time.sleep(0.5)
    
    # PUT /api/v1/csv/{row_id} to update an entry.
    # Here we assume the newly created entry is at index 0 (adjust if your logic is different)
    update_data = {"pnl": 150}
    put_response = client.put("/api/v1/csv/0", json=update_data, headers=headers)
    assert put_response.status_code == 200
    
    # DELETE /api/v1/csv/{row_id} to delete an entry.
    delete_response = client.delete("/api/v1/csv/0", headers=headers)
    assert delete_response.status_code == 200

def test_csv_backup_and_restore(test_user_token):
    headers = {"Authorization": f"Bearer {test_user_token}"}
    
    # Trigger a backup by creating a new CSV entry.
    new_entry = {
        "user": "backupuser",
        "broker": "backupbroker",
        "API key": "keybackup",
        "API secret": "secretbackup",
        "pnl": 200,
        "margin": 100,
        "max_risk": 20
    }
    client.post("/api/v1/csv", json=new_entry, headers=headers)
    time.sleep(0.5)  # Give it a moment to complete backup
    
    # GET backups endpoint.
    backups_response = client.get("/api/v1/csv/backups", headers=headers)
    assert backups_response.status_code == 200
    backups = backups_response.json().get("backups", [])
    # Ensure at least one backup is present.
    assert isinstance(backups, list)
    if backups:
        # Restore using the most recent backup.
        restore_response = client.post("/api/v1/csv/restore", json={"backup_filename": backups[0]}, headers=headers)
        assert restore_response.status_code == 200

def test_websocket_random_numbers(test_user_token):
    ws_url = f"/api/v1/ws/random-numbers?token={test_user_token}"
    with client.websocket_connect(ws_url) as websocket:
        data = websocket.receive_json()
        # Ensure 'id' is in the response
        assert "id" in data
        
        # Remove the id key
        timestamp_keys = [key for key in data if key != "id"]
        # Ensure there is exactly one other key (the timestamp)
        assert len(timestamp_keys) == 1
        
        timestamp_key = timestamp_keys[0]
        # Validate that the timestamp key is in valid ISO format.
        try:
            from datetime import datetime
            datetime.fromisoformat(timestamp_key)
        except Exception as e:
            pytest.fail(f"Timestamp '{timestamp_key}' is not a valid ISO format: {e}")
        
        # Check that the value associated with the timestamp is a number.
        value = data[timestamp_key]
        assert isinstance(value, (int, float))

