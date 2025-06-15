import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_get_cheat_types():
    """Test getting all cheat types"""
    response = client.get("/api/cheat_types")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0
    assert "raw" in [cheat_type.get("name").lower() for cheat_type in data]


def test_get_cheat_type():
    """Test getting a specific cheat type"""
    response = client.get("/api/cheat_types/raw")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Raw"
    assert "description" in data
    assert "pattern" in data
    assert "example" in data


def test_get_nonexistent_cheat_type():
    """Test getting a non-existent cheat type"""
    response = client.get("/api/cheat_types/nonexistent")
    assert response.status_code == 404
    data = response.json()
    assert data["detail"] == "Cheat type not found"


# These tests would require proper authentication
# and might need to be adjusted based on the actual implementation
# def test_create_cheat_type():
#     """Test creating a new cheat type"""
#     new_type = {
#         "name": "Test Type",
#         "description": "Test description",
#         "pattern": "^[A-Z0-9]{4}$",
#         "example": "ABCD"
#     }
#     response = client.post("/api/cheat_types/test_type", json=new_type)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Test Type"

# def test_update_cheat_type():
#     """Test updating an existing cheat type"""
#     updated_type = {
#         "name": "Updated Test Type",
#         "description": "Updated description",
#         "pattern": "^[A-Z0-9]{5}$",
#         "example": "ABCDE"
#     }
#     response = client.put("/api/cheat_types/test_type", json=updated_type)
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Updated Test Type"

# def test_delete_cheat_type():
#     """Test deleting a cheat type"""
#     response = client.delete("/api/cheat_types/test_type")
#     assert response.status_code == 200
#     data = response.json()
#     assert data["name"] == "Updated Test Type"
