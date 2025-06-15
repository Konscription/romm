import pytest
from validators.cheat_code import CheatCodeValidator

from backend.config.cheat_type_manager import cheat_type_manager


def test_validate_cheat_code_valid_data():
    """Test validation with valid data"""
    data = {
        "name": "Infinite Lives",
        "code": "ABCD-1234",
        "description": "Gives the player infinite lives",
        "type": "game_genie",
    }
    errors = CheatCodeValidator.validate_cheat_code(data)
    assert not errors, f"Expected no errors but got: {errors}"


def test_validate_cheat_code_missing_required_fields():
    """Test validation with missing required fields"""
    data = {"description": "Gives the player infinite lives"}
    errors = CheatCodeValidator.validate_cheat_code(data)
    assert "name" in errors, "Should have error for missing name"
    assert "code" in errors, "Should have error for missing code"
    assert "type" in errors, "Should have error for missing type"


def test_validate_cheat_code_invalid_type():
    """Test validation with invalid cheat type"""
    data = {
        "name": "Infinite Lives",
        "code": "ABCD-1234",
        "description": "Gives the player infinite lives",
        "type": "invalid_type",
    }
    errors = CheatCodeValidator.validate_cheat_code(data)
    assert "type" in errors, "Should have error for invalid type"


def test_validate_cheat_code_invalid_format():
    """Test validation with invalid code format"""
    data = {
        "name": "Infinite Lives",
        "code": "ABCD123",  # Invalid Game Genie format
        "description": "Gives the player infinite lives",
        "type": "game_genie",
    }
    errors = CheatCodeValidator.validate_cheat_code(data)
    assert "code" in errors, "Should have error for invalid code format"


def test_validate_code_format_raw():
    """Test validation of raw code format"""
    assert CheatCodeValidator.validate_code_format("any code", "raw") is None
    assert (
        CheatCodeValidator.validate_code_format("", "raw") == "Raw code cannot be empty"
    )


def test_validate_code_format_game_genie():
    """Test validation of Game Genie code format"""
    assert CheatCodeValidator.validate_code_format("ABCD-EFGH", "game_genie") is None
    assert CheatCodeValidator.validate_code_format("ABCDEF", "game_genie") is None
    assert (
        CheatCodeValidator.validate_code_format("ABCDE", "game_genie")
        == "Game Genie codes must be 6-8 alphanumeric characters (A-Z, 0-9)"
    )
    assert CheatCodeValidator.validate_code_format("ABCDEFGH", "game_genie") is None
    assert (
        CheatCodeValidator.validate_code_format("ABCDEFGHI", "game_genie")
        == "Game Genie codes must be 6-8 alphanumeric characters (A-Z, 0-9)"
    )


def test_validate_code_format_gameshark():
    """Test validation of GameShark code format"""
    assert CheatCodeValidator.validate_code_format("12345678", "gameshark") is None
    assert (
        CheatCodeValidator.validate_code_format("12345678 9ABCDEF0", "gameshark")
        is None
    )
    assert (
        CheatCodeValidator.validate_code_format("1234567", "gameshark")
        == "GameShark codes must be in format: XXXXXXXX or XXXXXXXX YYYYYYYY (hex digits)"
    )
    assert (
        CheatCodeValidator.validate_code_format("123456789ABCDEF01", "gameshark")
        == "GameShark codes must be in format: XXXXXXXX or XXXXXXXX YYYYYYYY (hex digits)"
    )


def test_validate_code_format_codebreaker():
    """Test validation of CodeBreaker code format"""
    assert CheatCodeValidator.validate_code_format("12345678", "codebreaker") is None
    assert (
        CheatCodeValidator.validate_code_format("123456789ABC", "codebreaker") is None
    )
    assert (
        CheatCodeValidator.validate_code_format("1234567", "codebreaker")
        == "CodeBreaker codes must be 8-12 hex digits"
    )
    assert (
        CheatCodeValidator.validate_code_format("123456789ABCDEF", "codebreaker")
        is None
    )


def test_validate_code_format_actionreplay():
    """Test validation of Action Replay code format"""
    assert CheatCodeValidator.validate_code_format("12345678", "actionreplay") is None
    assert (
        CheatCodeValidator.validate_code_format("123456789ABCDEF0", "actionreplay")
        is None
    )
    assert (
        CheatCodeValidator.validate_code_format("1234567", "actionreplay")
        == "Action Replay codes must be 8-16 hex digits"
    )
    assert (
        CheatCodeValidator.validate_code_format("123456789ABCDEF012345", "actionreplay")
        == "Action Replay codes must be 8-16 hex digits"
    )


def test_sanitize_cheat_code():
    """Test sanitization of cheat code data"""
    data = {
        "name": "  Infinite Lives  ",
        "code": "  ABCD-1234  ",
        "description": "  Gives the player infinite lives  ",
        "type": "  game_genie  ",
    }
    sanitized = CheatCodeValidator.sanitize_cheat_code(data)
    assert sanitized["name"] == "Infinite Lives"
    assert sanitized["code"] == "ABCD-1234"
    assert sanitized["description"] == "Gives the player infinite lives"
    assert sanitized["type"] == "game_genie"


def test_sanitize_cheat_code_missing_type():
    """Test sanitization with missing type field"""
    data = {
        "name": "Infinite Lives",
        "code": "ABCD-1234",
        "description": "Gives the player infinite lives",
    }
    sanitized = CheatCodeValidator.sanitize_cheat_code(data)
    assert "type" in sanitized, "Missing type should be added"
    assert sanitized["type"] == "raw", "Missing type should default to 'raw'"
