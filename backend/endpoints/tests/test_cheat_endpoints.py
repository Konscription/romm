from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from main import app
from models.rom import CheatCodeType, Rom


@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client


@pytest.fixture
def mock_db_rom_handler():
    """Mock the database ROM handler."""
    with patch("endpoints.rom.db_rom_handler") as mock:
        # Create a mock object instead of a real Rom instance
        class MockRom:
            def __init__(self):
                self.id = 1
                self.name = "Test ROM"
                self.fs_name = "test_rom.rom"
                self.platform_id = 1
                self.fs_path = "test/path"
                self.fs_resources_path = "test/resources/path"

        # Use the mock object instead of a real Rom
        mock.get_rom.return_value = MockRom()

        # Setup cheat code methods
        mock.add_cheat_code.return_value = {
            "id": 1,
            "name": "Infinite Lives",
            "code": "ABCD-1234",
            "description": "Gives the player infinite lives",
            "type": CheatCodeType.GAME_GENIE,
        }

        mock.update_cheat_code.return_value = {
            "id": 1,
            "name": "Updated Cheat",
            "code": "EFGH-5678",
            "description": "Updated description",
            "type": CheatCodeType.GAMESHARK,
        }

        mock.get_cheat_codes.return_value = [
            {
                "id": 1,
                "name": "Infinite Lives",
                "code": "ABCD-1234",
                "description": "Gives the player infinite lives",
                "type": CheatCodeType.GAME_GENIE,
            }
        ]

        # Setup cheat file methods
        mock.upload_cheat_file = AsyncMock(
            return_value={
                "id": 1,
                "rom_id": 1,
                "file_name": "test_cheats.cht",
                "file_size": 1024,
                "uploaded_at": "2025-06-11T12:00:00",
            }
        )

        mock.get_cheat_files.return_value = [
            {
                "id": 1,
                "rom_id": 1,
                "file_name": "test_cheats.cht",
                "file_size": 1024,
                "uploaded_at": "2025-06-11T12:00:00",
            }
        ]

        yield mock


# Test cases for POST /roms/{id}/cheats
def test_add_cheat_code_success(client, access_token, mock_db_rom_handler):
    """Test adding a cheat code successfully."""
    cheat_data = {
        "name": "Infinite Lives",
        "code": "ABCD-1234",
        "description": "Gives the player infinite lives",
        "type": CheatCodeType.GAME_GENIE,
    }

    response = client.post(
        "/api/roms/1/cheats",
        headers={"Authorization": f"Bearer {access_token}"},
        json=cheat_data,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Infinite Lives",
        "code": "ABCD-1234",
        "description": "Gives the player infinite lives",
        "type": CheatCodeType.GAME_GENIE,
    }
    mock_db_rom_handler.add_cheat_code.assert_called_once_with(1, cheat_data)


def test_add_cheat_code_rom_not_found(client, access_token, mock_db_rom_handler):
    """Test adding a cheat code when the ROM is not found."""
    mock_db_rom_handler.get_rom.return_value = None

    cheat_data = {
        "name": "Infinite Lives",
        "code": "ABCD-1234",
        "description": "Gives the player infinite lives",
        "type": CheatCodeType.GAME_GENIE,
    }

    response = client.post(
        "/api/roms/1/cheats",
        headers={"Authorization": f"Bearer {access_token}"},
        json=cheat_data,
    )

    assert response.status_code == 404
    assert "Rom with id" in response.json()["detail"]
    mock_db_rom_handler.add_cheat_code.assert_not_called()


# Test cases for PUT /roms/{id}/cheats/{cheat_id}
def test_update_cheat_code_success(client, access_token, mock_db_rom_handler):
    """Test updating a cheat code successfully."""
    cheat_data = {
        "name": "Updated Cheat",
        "code": "EFGH-5678",
        "description": "Updated description",
        "type": CheatCodeType.GAMESHARK,
    }

    response = client.put(
        "/api/roms/1/cheats/1",
        headers={"Authorization": f"Bearer {access_token}"},
        json=cheat_data,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "name": "Updated Cheat",
        "code": "EFGH-5678",
        "description": "Updated description",
        "type": CheatCodeType.GAMESHARK,
    }
    mock_db_rom_handler.update_cheat_code.assert_called_once_with(1, cheat_data)


def test_update_cheat_code_rom_not_found(client, access_token, mock_db_rom_handler):
    """Test updating a cheat code when the ROM is not found."""
    mock_db_rom_handler.get_rom.return_value = None

    cheat_data = {
        "name": "Updated Cheat",
        "code": "EFGH-5678",
        "description": "Updated description",
        "type": CheatCodeType.GAMESHARK,
    }

    response = client.put(
        "/api/roms/1/cheats/1",
        headers={"Authorization": f"Bearer {access_token}"},
        json=cheat_data,
    )

    assert response.status_code == 404
    assert "Rom with id" in response.json()["detail"]
    mock_db_rom_handler.update_cheat_code.assert_not_called()


# Test cases for DELETE /roms/{id}/cheats/{cheat_id}
def test_delete_cheat_code_success(client, access_token, mock_db_rom_handler):
    """Test deleting a cheat code successfully."""
    response = client.delete(
        "/api/roms/1/cheats/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"msg": "Cheat code deleted successfully"}
    mock_db_rom_handler.delete_cheat_code.assert_called_once_with(1)


def test_delete_cheat_code_rom_not_found(client, access_token, mock_db_rom_handler):
    """Test deleting a cheat code when the ROM is not found."""
    mock_db_rom_handler.get_rom.return_value = None

    response = client.delete(
        "/api/roms/1/cheats/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert "Rom with id" in response.json()["detail"]
    mock_db_rom_handler.delete_cheat_code.assert_not_called()


# Test cases for GET /roms/{id}/cheats
def test_get_cheat_codes_success(client, access_token, mock_db_rom_handler):
    """Test getting all cheat codes for a ROM successfully."""
    response = client.get(
        "/api/roms/1/cheats",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "name": "Infinite Lives",
            "code": "ABCD-1234",
            "description": "Gives the player infinite lives",
            "type": CheatCodeType.GAME_GENIE,
        }
    ]
    mock_db_rom_handler.get_cheat_codes.assert_called_once_with(1)


def test_get_cheat_codes_rom_not_found(client, access_token, mock_db_rom_handler):
    """Test getting all cheat codes when the ROM is not found."""
    mock_db_rom_handler.get_rom.return_value = None

    response = client.get(
        "/api/roms/1/cheats",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert "Rom with id" in response.json()["detail"]
    mock_db_rom_handler.get_cheat_codes.assert_not_called()


# Test cases for POST /roms/{id}/cheats/files
def test_upload_cheat_file_success(client, access_token, mock_db_rom_handler):
    """Test uploading a cheat file successfully."""
    # Create form data
    form_data = {
        "file_name": "test_cheats.cht",
        "file_size": "1024",
        "file_content": "Test cheat file content",
    }

    # Mock the upload_cheat_file method to handle the form data
    mock_db_rom_handler.upload_cheat_file.return_value = {
        "id": 1,
        "rom_id": 1,
        "file_name": "test_cheats.cht",
        "file_size": 1024,
        "uploaded_at": "2025-06-11T12:00:00",
    }

    # Use the client to post the form data
    response = client.post(
        "/api/roms/1/cheats/files",
        headers={"Authorization": f"Bearer {access_token}"},
        data=form_data,
    )

    assert response.status_code == 200
    assert response.json() == {
        "id": 1,
        "rom_id": 1,
        "file_name": "test_cheats.cht",
        "file_size": 1024,
        "uploaded_at": "2025-06-11T12:00:00",
    }


def test_upload_cheat_file_rom_not_found(client, access_token, mock_db_rom_handler):
    """Test uploading a cheat file when the ROM is not found."""
    mock_db_rom_handler.get_rom.return_value = None

    # Create form data
    form_data = {
        "file_name": "test_cheats.cht",
        "file_size": "1024",
        "file_content": "Test cheat file content",
    }

    response = client.post(
        "/api/roms/1/cheats/files",
        headers={"Authorization": f"Bearer {access_token}"},
        data=form_data,
    )

    assert response.status_code == 404
    assert "Rom with id" in response.json()["detail"]
    mock_db_rom_handler.upload_cheat_file.assert_not_called()


# Test cases for GET /roms/{id}/cheats/files
def test_get_cheat_files_success(client, access_token, mock_db_rom_handler):
    """Test getting all cheat files for a ROM successfully."""
    response = client.get(
        "/api/roms/1/cheats/files",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == [
        {
            "id": 1,
            "rom_id": 1,
            "file_name": "test_cheats.cht",
            "file_size": 1024,
            "uploaded_at": "2025-06-11T12:00:00",
        }
    ]
    mock_db_rom_handler.get_cheat_files.assert_called_once_with(1)


def test_get_cheat_files_rom_not_found(client, access_token, mock_db_rom_handler):
    """Test getting all cheat files when the ROM is not found."""
    mock_db_rom_handler.get_rom.return_value = None

    response = client.get(
        "/api/roms/1/cheats/files",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert "Rom with id" in response.json()["detail"]
    mock_db_rom_handler.get_cheat_files.assert_not_called()


# Test cases for DELETE /roms/{id}/cheats/files/{file_id}
def test_delete_cheat_file_success(client, access_token, mock_db_rom_handler):
    """Test deleting a cheat file successfully."""
    response = client.delete(
        "/api/roms/1/cheats/files/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 200
    assert response.json() == {"msg": "Cheat file deleted successfully"}
    mock_db_rom_handler.delete_cheat_file.assert_called_once_with(1)


def test_delete_cheat_file_rom_not_found(client, access_token, mock_db_rom_handler):
    """Test deleting a cheat file when the ROM is not found."""
    mock_db_rom_handler.get_rom.return_value = None

    response = client.delete(
        "/api/roms/1/cheats/files/1",
        headers={"Authorization": f"Bearer {access_token}"},
    )

    assert response.status_code == 404
    assert "Rom with id" in response.json()["detail"]
    mock_db_rom_handler.delete_cheat_file.assert_not_called()
