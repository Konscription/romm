import pytest
from models.rom import CheatCode, CheatCodeType, Rom
from sqlalchemy import select


@pytest.fixture
def cheat_code(rom: Rom):
    """Create a test cheat code for a ROM."""
    # Use uppercase for the enum value to match what's in the database
    cheat_code = CheatCode(
        rom_id=rom.id,
        name="Infinite Lives",
        code="ABCD-1234",
        description="Gives the player infinite lives",
        type=CheatCodeType.GAME_GENIE,
    )
    return cheat_code


def test_cheat_code_creation(cheat_code: CheatCode):
    """Test that a CheatCode can be created with all required fields."""
    assert cheat_code.name == "Infinite Lives"
    assert cheat_code.code == "ABCD-1234"
    assert cheat_code.description == "Gives the player infinite lives"
    assert cheat_code.type == CheatCodeType.GAME_GENIE


def test_cheat_code_rom_relationship(
    rom: Rom, cheat_code: CheatCode, setup_database, clear_database
):
    """Test the relationship between CheatCode and Rom."""
    from config.config_manager import ConfigManager
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    # Create a session
    engine = create_engine(ConfigManager.get_db_engine(), pool_pre_ping=True)
    session = Session(engine)

    try:
        # Add the rom and cheat code to the database
        session.add(rom)
        session.add(cheat_code)
        session.commit()

        # Query the rom and cheat code from the database to get fresh instances
        db_rom = session.execute(select(Rom).filter_by(id=rom.id)).scalar_one()
        db_cheat_code = session.execute(
            select(CheatCode).filter_by(id=cheat_code.id)
        ).scalar_one()

        # Verify the cheat code is associated with the rom
        assert len(db_rom.cheat_codes) == 1
        assert db_rom.cheat_codes[0].id == db_cheat_code.id
        assert db_rom.cheat_codes[0].name == "Infinite Lives"

        # Verify the rom is associated with the cheat code
        assert db_cheat_code.rom.id == db_rom.id
        assert db_cheat_code.rom.name == "test_rom"
    finally:
        session.close()


def test_multiple_cheat_codes_for_rom(rom: Rom, setup_database, clear_database):
    """Test that a Rom can have multiple CheatCodes."""
    from config.config_manager import ConfigManager
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    # Create a session
    engine = create_engine(ConfigManager.get_db_engine(), pool_pre_ping=True)
    session = Session(engine)

    try:
        # Add the rom to the database first
        session.add(rom)
        session.commit()

        # Create multiple cheat codes for the same rom
        cheat_code1 = CheatCode(
            rom_id=rom.id,
            name="Infinite Lives",
            code="ABCD-1234",
            description="Gives the player infinite lives",
            type=CheatCodeType.GAME_GENIE,
        )

        cheat_code2 = CheatCode(
            rom_id=rom.id,
            name="Infinite Energy",
            code="EFGH-5678",
            description="Gives the player infinite energy",
            type=CheatCodeType.GAMESHARK,
        )

        # Add the cheat codes to the database
        session.add(cheat_code1)
        session.add(cheat_code2)
        session.commit()

        # Query the rom from the database to get a fresh instance
        db_rom = session.execute(select(Rom).filter_by(id=rom.id)).scalar_one()

        # Verify the rom has multiple cheat codes
        assert len(db_rom.cheat_codes) == 2

        # Verify the cheat codes are correctly associated with the rom
        cheat_codes = sorted(db_rom.cheat_codes, key=lambda x: x.name)
        assert cheat_codes[0].name == "Infinite Energy"
        assert cheat_codes[1].name == "Infinite Lives"
    finally:
        session.close()


def test_cascade_delete(setup_database, clear_database):
    """Test that when a Rom is deleted, its associated CheatCodes are also deleted."""
    from config.config_manager import ConfigManager
    from models.platform import Platform
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    # Create a session
    engine = create_engine(ConfigManager.get_db_engine(), pool_pre_ping=True)
    session = Session(engine)

    try:
        # Create a new platform and rom specifically for this test
        platform = Platform(
            name="test_platform_cascade",
            slug="test_platform_cascade_slug",
            fs_slug="test_platform_cascade_slug",
        )
        session.add(platform)
        session.flush()

        # Create a new rom
        test_rom = Rom(
            platform_id=platform.id,
            name="test_rom_cascade",
            slug="test_rom_cascade_slug",
            fs_name="test_rom_cascade.zip",
            fs_name_no_tags="test_rom_cascade",
            fs_name_no_ext="test_rom_cascade",
            fs_extension="zip",
            fs_path=f"{platform.slug}/roms",
        )
        session.add(test_rom)
        session.flush()

        # Create a cheat code for the rom
        cheat_code = CheatCode(
            rom_id=test_rom.id,
            name="Infinite Lives",
            code="ABCD-1234",
            description="Gives the player infinite lives",
            type=CheatCodeType.GAME_GENIE,
        )

        # Add the cheat code to the database
        session.add(cheat_code)
        session.commit()

        # Get the cheat code ID for later verification
        cheat_code_id = cheat_code.id

        # Delete the rom directly from the database using SQLAlchemy text
        from sqlalchemy import text

        session.execute(text(f"DELETE FROM roms WHERE id = {test_rom.id}"))
        session.commit()

        # Verify the cheat code was also deleted (cascade delete)
        remaining_cheat_code = session.execute(
            select(CheatCode).filter_by(id=cheat_code_id)
        ).scalar_one_or_none()
        assert remaining_cheat_code is None
    finally:
        session.close()


def test_cheat_code_types(rom: Rom, setup_database, clear_database):
    """Test that all CheatCodeType enum values can be used."""
    from config.config_manager import ConfigManager
    from sqlalchemy import create_engine, select
    from sqlalchemy.orm import Session

    # Create a session
    engine = create_engine(ConfigManager.get_db_engine(), pool_pre_ping=True)
    session = Session(engine)

    try:
        # Add the rom to the database first
        session.add(rom)
        session.commit()

        # Create a cheat code for each type
        for cheat_type in CheatCodeType:
            cheat_code = CheatCode(
                rom_id=rom.id,
                name=f"{cheat_type.name} Cheat",
                code=f"CODE-{cheat_type.name}",
                description=f"Test cheat of type {cheat_type.name}",
                type=cheat_type,
            )
            session.add(cheat_code)

        session.commit()

        # Query all cheat codes from the database
        db_cheat_codes = (
            session.execute(select(CheatCode).filter_by(rom_id=rom.id)).scalars().all()
        )

        # Verify all cheat codes were created
        assert len(db_cheat_codes) == len(list(CheatCodeType))

        # Verify each type is represented
        cheat_types = {cheat_code.type for cheat_code in db_cheat_codes}
        assert len(cheat_types) == len(list(CheatCodeType))

        # Verify each enum value is in the set of types
        for cheat_type in CheatCodeType:
            assert cheat_type in cheat_types
    finally:
        session.close()
