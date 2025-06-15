import pytest
from models.rom import CheatCode

from backend.config.cheat_type_manager import cheat_type_manager


def test_cheat_code_model():
    """Test the CheatCode model"""
    cheat = CheatCode(
        id=1,
        rom_id=1,
        name="Infinite Lives",
        code="ABCD-1234",
        description="Gives the player infinite lives",
        type="game_genie",
    )

    assert cheat.id == 1
    assert cheat.rom_id == 1
    assert cheat.name == "Infinite Lives"
    assert cheat.code == "ABCD-1234"
    assert cheat.description == "Gives the player infinite lives"
    assert cheat.type == "game_genie"


def test_cheat_code_type_validation():
    """Test validation of cheat code types"""
    valid_types = cheat_type_manager.get_all_type_ids()
    assert "raw" in valid_types
    assert "game_genie" in valid_types
    assert "gameshark" in valid_types
    assert "codebreaker" in valid_types
    assert "actionreplay" in valid_types

    # Test getting cheat type info
    raw_info = cheat_type_manager.get_cheat_type("raw")
    assert raw_info is not None
    if raw_info:
        assert raw_info.get("name") == "Raw"
        assert raw_info.get("description") == "Raw cheat code with no specific format"
        assert raw_info.get("pattern") == "^.+$"
        assert raw_info.get("example") == "ABCDEF"
