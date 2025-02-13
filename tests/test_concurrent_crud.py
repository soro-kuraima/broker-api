# tests/test_concurrent_crud.py
import pytest
from fastapi.testclient import TestClient
from concurrent.futures import ThreadPoolExecutor
import time

from app.main import app  # Ensure PYTHONPATH is set correctly

client = TestClient(app)


def register_and_get_token(user_data: dict) -> str:
    # Attempt to register (ignore error if already registered)
    client.post("/api/v1/register", json=user_data)
    # Log in to get a token
    token_resp = client.post("/api/v1/token", data=user_data)
    token = token_resp.json().get("access_token")
    assert token, f"Failed to get token for {user_data['username']}"
    return token


@pytest.fixture(scope="module")
def user_tokens():
    # Create tokens for two different users.
    user1 = {"username": "user1", "password": "pass1"}
    user2 = {"username": "user2", "password": "pass2"}
    token1 = register_and_get_token(user1)
    token2 = register_and_get_token(user2)
    return token1, token2


@pytest.fixture(scope="module")
def create_initial_entry(user_tokens):
    # Use one of the users to create an initial CSV entry.
    token1, _ = user_tokens
    headers = {"Authorization": f"Bearer {token1}"}
    new_entry = {
        "user": "user1",
        "broker": "broker1",
        "API key": "key1",
        "API secret": "secret1",
        "pnl": 100,
        "margin": 50,
        "max_risk": 10
    }
    resp = client.post("/api/v1/csv", json=new_entry, headers=headers)
    assert resp.status_code in (200, 201)
    # Give time for the backup mechanism if needed.
    time.sleep(0.5)
    # Return the index of the created row (assuming it's row 0)
    return 0


def update_entry(row_id: int, headers: dict, update_data: dict):
    return client.put(f"/api/v1/csv/{row_id}", json=update_data, headers=headers)


def test_simultaneous_updates_by_multiple_users(user_tokens, create_initial_entry):
    """
    Simulate two users concurrently updating the same CSV row.
    The file lock mechanism should ensure both updates eventually succeed,
    and the final CSV value should match one of the updates.
    """
    token1, token2 = user_tokens
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}
    row_id = create_initial_entry

    # Prepare different update payloads from each user.
    update_data1 = {"pnl": 1000}
    update_data2 = {"pnl": 2000}

    with ThreadPoolExecutor(max_workers=2) as executor:
        future1 = executor.submit(update_entry, row_id, headers1, update_data1)
        future2 = executor.submit(update_entry, row_id, headers2, update_data2)
        res1 = future1.result()
        res2 = future2.result()

    # Both operations should complete; if a lock timeout occurs,
    # the API should return an error (e.g., 503). Adjust assertions as needed.
    # For this example, we assume both eventually succeed.
    assert res1.status_code == 200, f"Update by user1 failed: {res1.text}"
    assert res2.status_code == 200, f"Update by user2 failed: {res2.text}"

    # Retrieve final CSV content and verify that the 'pnl' is one of the updated values.
    # We'll use one user's token to fetch the CSV data.
    get_resp = client.get("/api/v1/csv", headers=headers1)
    assert get_resp.status_code == 200
    csv_data = get_resp.json()

    # Assuming the updated entry is at row index 0.
    final_value = int(csv_data[row_id]["pnl"])
    assert final_value in (1000, 2000), f"Final pnl {final_value} not expected."


def test_simultaneous_creates_and_deletes(user_tokens):
    """
    Simulate multiple users concurrently creating and deleting entries.
    This tests concurrent POST and DELETE endpoints.
    """
    token1, token2 = user_tokens
    headers1 = {"Authorization": f"Bearer {token1}"}
    headers2 = {"Authorization": f"Bearer {token2}"}

    # Function to create a new CSV entry.
    def create_entry(user_label, pnl_value):
        new_entry = {
            "user": user_label,
            "broker": f"{user_label}_broker",
            "API key": f"{user_label}_key",
            "API secret": f"{user_label}_secret",
            "pnl": pnl_value,
            "margin": 50,
            "max_risk": 10
        }
        return client.post("/api/v1/csv", json=new_entry, headers=headers1)

    # Create several entries concurrently.
    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = [
            executor.submit(create_entry, "user1", 111),
            executor.submit(create_entry, "user2", 222),
            executor.submit(create_entry, "user3", 333),
        ]
        create_results = [f.result() for f in futures]
    for res in create_results:
        assert res.status_code in (200, 201), f"Creation failed: {res.text}"

    # Pause briefly to ensure file operations are complete.
    time.sleep(0.5)

    # Fetch the CSV to get the current entries.
    get_resp = client.get("/api/v1/csv", headers=headers1)
    csv_data = get_resp.json()
    num_entries = len(csv_data)
    assert num_entries >= 3, "Not enough entries created for delete test."

    # Concurrently attempt to delete the last three entries.
    def delete_entry(row_id):
        return client.delete(f"/api/v1/csv/{row_id}", headers=headers2)

    # Capture the indices to delete.
    indices_to_delete = list(range(num_entries - 3, num_entries))
    with ThreadPoolExecutor(max_workers=3) as executor:
        delete_futures = [executor.submit(delete_entry, rid) for rid in indices_to_delete]
        delete_results = [f.result() for f in delete_futures]

    # Since concurrent deletions may conflict (because row indices shift),
    # we expect that at least one deletion succeeds and at least one may fail.
    success_codes = [res.status_code for res in delete_results if res.status_code == 200]
    failure_codes = [res.status_code for res in delete_results if res.status_code != 200]

    assert success_codes, "At least one deletion should succeed."
    assert failure_codes, "At least one deletion should fail due to race conditions."

    # Final CSV fetch to check that the number of entries has decreased
    final_resp = client.get("/api/v1/csv", headers=headers1)
    final_data = final_resp.json()
    # Because of concurrent deletes, the expected number may vary.
    assert len(final_data) <= num_entries - 1, "The number of entries should have decreased."
