import json

import pytest
from fastapi.testclient import TestClient
from main import app
from models.rom import CheatCode, Rom
from models.user import User
from sqlalchemy.orm import Session

from backend.config.cheat_type_manager import cheat_type_manager

client = TestClient(app)


@pytest.fixture
def mock_rom(db_session: Session) -> Rom:
    """Create a mock ROM for testing"""
    rom = Rom(
        fs_name="mock_rom",
        fs_path="/mock/path",
        platform_id=1,
    )
    db_session.add(rom)
    db_session.commit()
    return rom


@pytest.fixture
def mock_user(db_session: Session) -> User:
    """Create a mock user for testing"""
    user = User(
        username="testuser",
        password="testpass",
        email="test@example.com",
    )
    db_session.add(user)
    db_session.commit()
    return user


def test_get_cheat_types(mock_user: User):
    """Test getting available cheat types"""
    # Login to get a valid token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Get cheat types
    response = client.get(
        "/cheat-types",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    cheat_types = response.json()

    # Verify expected types are present
    assert "raw" in [ct["name"] for ct in cheat_types], "Raw type should be available"
    assert "game_genie" in [
        ct["name"] for ct in cheat_types
    ], "Game Genie type should be available"
    assert "gameshark" in [
        ct["name"] for ct in cheat_types
    ], "GameShark type should be available"
    assert "codebreaker" in [
        ct["name"] for ct in cheat_types
    ], "CodeBreaker type should be available"
    assert "actionreplay" in [
        ct["name"] for ct in cheat_types
    ], "ActionReplay type should be available"


def test_add_cheat_code(mock_user: User, mock_rom: Rom):
    """Test adding a cheat code"""
    # Login to get a valid token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Add cheat code
    cheat_data = {
        "name": "Infinite Lives",
        "code": "ABCD-EFGH",
        "description": "Gives the player infinite lives",
        "type": "game_genie",
        "rom_id": mock_rom.id,
    }

    response = client.post(
        "/cheats",
        json=cheat_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 201
    cheat_code = response.json()

    # Verify cheat code was created correctly
    assert cheat_code["name"] == cheat_data["name"]
    assert cheat_code["code"] == cheat_data["code"]
    assert cheat_code["description"] == cheat_data["description"]
    assert cheat_code["type"] == cheat_data["type"]
    assert cheat_code["rom_id"] == cheat_data["rom_id"]


def test_add_cheat_code_invalid_type(mock_user: User, mock_rom: Rom):
    """Test adding a cheat code with an invalid type"""
    # Login to get a valid token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Add cheat code with invalid type
    cheat_data = {
        "name": "Infinite Lives",
        "code": "ABCD-EFGH",
        "description": "Gives the player infinite lives",
        "type": "invalid_type",
        "rom_id": mock_rom.id,
    }

    response = client.post(
        "/cheats",
        json=cheat_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 422  # Unprocessable Entity
    assert "type" in response.json()["detail"], "Should have error for invalid type"


def test_add_cheat_code_invalid_format(mock_user: User, mock_rom: Rom):
    """Test adding a cheat code with invalid format for the type"""
    # Login to get a valid token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Add cheat code with invalid format
    cheat_data = {
        "name": "Infinite Lives",
        "code": "ABCD",  # Too short for Game Genie
        "description": "Gives the player infinite lives",
        "type": "game_genie",
        "rom_id": mock_rom.id,
    }

    response = client.post(
        "/cheats",
        json=cheat_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 422  # Unprocessable Entity
    assert (
        "code" in response.json()["detail"]
    ), "Should have error for invalid code format"


def test_get_cheat_codes(mock_user: User, mock_rom: Rom):
    """Test getting cheat codes for a ROM"""
    # Login to get a valid token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Add a cheat code
    cheat_data = {
        "name": "Infinite Lives",
        "code": "ABCD-EFGH",
        "description": "Gives the player infinite lives",
        "type": "game_genie",
        "rom_id": mock_rom.id,
    }

    add_response = client.post(
        "/cheats",
        json=cheat_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert add_response.status_code == 201

    # Get cheat codes
    response = client.get(
        f"/cheats?rom_id={mock_rom.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    cheat_codes = response.json()

    # Verify cheat code was returned
    assert len(cheat_codes) == 1
    assert cheat_codes[0]["name"] == cheat_data["name"]
    assert cheat_codes[0]["code"] == cheat_data["code"]
    assert cheat_codes[0]["description"] == cheat_data["description"]
    assert cheat_codes[0]["type"] == cheat_data["type"]
    assert cheat_codes[0]["rom_id"] == cheat_data["rom_id"]


def test_update_cheat_code(mock_user: User, mock_rom: Rom):
    """Test updating a cheat code"""
    # Login to get a valid token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Add a cheat code
    cheat_data = {
        "name": "Infinite Lives",
        "code": "ABCD-EFGH",
        "description": "Gives the player infinite lives",
        "type": "game_genie",
        "rom_id": mock_rom.id,
    }

    add_response = client.post(
        "/cheats",
        json=cheat_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert add_response.status_code == 201
    cheat_code = add_response.json()

    # Update cheat code
    update_data = {
        "name": "Infinite Lives Updated",
        "code": "ABCD-EFGH",
        "description": "Gives the player infinite lives updated",
        "type": "game_genie",
    }

    response = client.put(
        f"/cheats/{cheat_code['id']}",
        json=update_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert response.status_code == 200
    updated_cheat = response.json()

    # Verify cheat code was updated correctly
    assert updated_cheat["name"] == update_data["name"]
    assert updated_cheat["description"] == update_data["description"]


def test_delete_cheat_code(mock_user: User, mock_rom: Rom):
    """Test deleting a cheat code"""
    # Login to get a valid token
    login_response = client.post(
        "/auth/login",
        json={"username": "testuser", "password": "testpass"},
    )
    assert login_response.status_code == 200
    token = login_response.json()["access_token"]

    # Add a cheat code
    cheat_data = {
        "name": "Infinite Lives",
        "code": "ABCD-EFGH",
        "description": "Gives the player infinite lives",
        "type": "game_genie",
        "rom_id": mock_rom.id,
    }

    add_response = client.post(
        "/cheats",
        json=cheat_data,
        headers={
            "Authorization": f"Bearer {token}",
        },
    )
    assert add_response.status_code == 201
    cheat_code = add_response.json()

    # Delete cheat code
    response = client.delete(
        f"/cheats/{cheat_code['id']}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 204  # No Content

    # Verify cheat code was deleted
    get_response = client.get(
        f"/cheats?rom_id={mock_rom.id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert get_response.status_code == 200
    cheat_codes = get_response.json()
    assert len(cheat_codes) == 0, "Cheat code should have been deleted"
