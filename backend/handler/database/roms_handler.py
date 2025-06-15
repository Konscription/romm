import functools
from collections.abc import Iterable
from datetime import datetime
from typing import List, Sequence, Tuple

from config import ROMM_DB_DRIVER
from decorators.database import begin_session
from models.collection import Collection, VirtualCollection
from models.platform import Platform
from models.rom import CheatCode, CheatFile, Rom, RomFile, RomMetadata, RomUser
from sqlalchemy import (
    Integer,
    Row,
    String,
    Text,
    and_,
    case,
    cast,
    delete,
    func,
    literal,
    or_,
    select,
    text,
    update,
)
from sqlalchemy.orm import InstrumentedAttribute, Query, Session, selectinload

from .base_handler import DBBaseHandler

EJS_SUPPORTED_PLATFORMS = [
    "3do",
    "amiga",
    "amiga-cd32",
    "arcade",
    "neogeoaes",
    "neogeomvs",
    "atari2600",
    "atari-2600-plus",
    "atari5200",
    "atari7800",
    "c-plus-4",
    "c64",
    "cpet",
    "commodore-64c",
    "c128",
    "commmodore-128",
    "colecovision",
    "jaguar",
    "lynx",
    "atari-lynx-mkii",
    "neo-geo-pocket",
    "neo-geo-pocket-color",
    "nes",
    "famicom",
    "fds",
    "game-televisison",
    "new-style-nes",
    "n64",
    "ique-player",
    "nds",
    "nintendo-ds-lite",
    "nintendo-dsi",
    "nintendo-dsi-xl",
    "gb",
    "game-boy-pocket",
    "game-boy-light",
    "gba",
    "game-boy-adavance-sp",
    "game-boy-micro",
    "gbc",
    "pc-fx",
    "ps",
    "psp",
    "segacd",
    "sega32",
    "gamegear",
    "sms",
    "sega-mark-iii",
    "sega-game-box-9",
    "sega-master-system-ii",
    "master-system-super-compact",
    "master-system-girl",
    "genesis-slash-megadrive",
    "sega-mega-drive-2-slash-genesis",
    "sega-mega-jet",
    "mega-pc",
    "tera-drive",
    "sega-nomad",
    "saturn",
    "snes",
    "sfam",
    "super-nintendo-original-european-version",
    "super-famicom-shvc-001",
    "super-famicom-jr-model-shvc-101",
    "new-style-super-nes-model-sns-101",
    "turbografx16--1",
    "vic-20",
    "virtualboy",
    "wonderswan",
    "swancrystal",
    "wonderswan-color",
]


def with_details(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        kwargs["query"] = select(Rom).options(
            selectinload(Rom.saves),
            selectinload(Rom.states),
            selectinload(Rom.screenshots),
            selectinload(Rom.rom_users),
            selectinload(Rom.sibling_roms),
            selectinload(Rom.metadatum),
            selectinload(Rom.files),
            selectinload(Rom.collections),
        )
        return func(*args, **kwargs)

    return wrapper


def with_simple(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        kwargs["query"] = select(Rom).options(
            selectinload(Rom.rom_users),
            selectinload(Rom.metadatum),
            selectinload(Rom.files),
        )
        return func(*args, **kwargs)

    return wrapper


class DBRomsHandler(DBBaseHandler):
    @begin_session
    @with_details
    def add_rom(self, rom: Rom, query: Query = None, session: Session = None) -> Rom:
        rom = session.merge(rom)
        session.flush()

        return session.scalar(query.filter_by(id=rom.id).limit(1))

    @begin_session
    @with_details
    def get_rom(
        self, id: int, *, query: Query = None, session: Session = None
    ) -> Rom | None:
        return session.scalar(query.filter_by(id=id).limit(1))

    def filter_by_platform_id(self, query: Query, platform_id: int):
        return query.filter(Rom.platform_id == platform_id)

    def filter_by_collection_id(
        self, query: Query, session: Session, collection_id: int
    ):
        collection = (
            session.query(Collection)
            .filter(Collection.id == collection_id)
            .one_or_none()
        )
        if collection:
            return query.filter(Rom.id.in_(collection.rom_ids))
        return query

    def filter_by_virtual_collection_id(
        self, query: Query, session: Session, virtual_collection_id: str
    ):
        name, type = VirtualCollection.from_id(virtual_collection_id)
        v_collection = (
            session.query(VirtualCollection)
            .filter(VirtualCollection.name == name, VirtualCollection.type == type)
            .one_or_none()
        )
        if v_collection:
            return query.filter(Rom.id.in_(v_collection.rom_ids))
        return query

    def filter_by_search_term(self, query: Query, search_term: str):
        return query.filter(
            or_(
                Rom.fs_name.ilike(f"%{search_term}%"),
                Rom.name.ilike(f"%{search_term}%"),
            )
        )

    def filter_by_unmatched_only(self, query: Query):
        return query.filter(
            and_(
                Rom.igdb_id.is_(None),
                Rom.moby_id.is_(None),
                Rom.ss_id.is_(None),
            )
        )

    def filter_by_matched_only(self, query: Query):
        return query.filter(
            or_(
                Rom.igdb_id.isnot(None),
                Rom.moby_id.isnot(None),
                Rom.ss_id.isnot(None),
            )
        )

    def filter_by_favourites_only(self, query: Query, session: Session, user_id: int):
        favourites_collection = (
            session.query(Collection)
            .filter(Collection.name.ilike("favourites"))
            .filter(Collection.user_id == user_id)
            .one_or_none()
        )

        if favourites_collection:
            return query.filter(Rom.id.in_(favourites_collection.rom_ids))

        return query

    def filter_by_duplicates_only(self, query: Query):
        return query.filter(Rom.sibling_roms.any())

    def filter_by_playables_only(self, query: Query):
        return query.join(Rom.platform).filter(
            Platform.slug.in_(EJS_SUPPORTED_PLATFORMS)
        )

    def filter_by_ra_only(self, query: Query):
        return query.filter(Rom.ra_id.isnot(None))

    def filter_by_genre(self, query: Query, selected_genre: str):
        if ROMM_DB_DRIVER == "postgresql":
            return query.filter(
                text("genres @> (:genre)::jsonb").bindparams(
                    genre=f'["{selected_genre}"]'
                )
            )
        else:
            return query.filter(
                text("JSON_OVERLAPS(genres, JSON_ARRAY(:genre))").bindparams(
                    genre=selected_genre
                )
            )

    def filter_by_franchise(self, query: Query, selected_franchise: str):
        if ROMM_DB_DRIVER == "postgresql":
            return query.filter(
                text("franchises @> (:franchise)::jsonb").bindparams(
                    franchise=f'["{selected_franchise}"]'
                )
            )
        else:
            return query.filter(
                text("JSON_OVERLAPS(franchises, JSON_ARRAY(:franchise))").bindparams(
                    franchise=selected_franchise
                )
            )

    def filter_by_collection(self, query: Query, selected_collection: str):
        if ROMM_DB_DRIVER == "postgresql":
            return query.filter(
                text("collections @> (:collection)::jsonb").bindparams(
                    collection=f'["{selected_collection}"]'
                )
            )
        else:
            return query.filter(
                text("JSON_OVERLAPS(collections, JSON_ARRAY(:collection))").bindparams(
                    collection=selected_collection
                )
            )

    def filter_by_company(self, query: Query, selected_company: str):
        if ROMM_DB_DRIVER == "postgresql":
            return query.filter(
                text("companies @> (:company)::jsonb").bindparams(
                    company=f'["{selected_company}"]'
                )
            )
        else:
            return query.filter(
                text("JSON_OVERLAPS(companies, JSON_ARRAY(:company))").bindparams(
                    company=selected_company
                )
            )

    def filter_by_age_rating(self, query: Query, selected_age_rating: str):
        if ROMM_DB_DRIVER == "postgresql":
            return query.filter(
                text("age_ratings @> (:age_rating)::jsonb").bindparams(
                    age_rating=f'["{selected_age_rating}"]'
                )
            )
        else:
            return query.filter(
                text("JSON_OVERLAPS(age_ratings, JSON_ARRAY(:age_rating))").bindparams(
                    age_rating=selected_age_rating
                )
            )

    def filter_by_status(self, query: Query, selected_status: str):
        status_filter = RomUser.status == selected_status
        if selected_status == "now_playing":
            status_filter = RomUser.now_playing.is_(True)
        elif selected_status == "backlogged":
            status_filter = RomUser.backlogged.is_(True)
        elif selected_status == "hidden":
            status_filter = RomUser.hidden.is_(True)

        if selected_status == "hidden":
            return query.filter(status_filter)

        return query.filter(status_filter, RomUser.hidden.is_(False))

    def filter_by_region(self, query: Query, selected_region: str):
        if ROMM_DB_DRIVER == "postgresql":
            return query.filter(
                text("regions @> (:region)::jsonb").bindparams(
                    region=f'["{selected_region}"]'
                )
            )
        else:
            return query.filter(
                text("JSON_OVERLAPS(regions, JSON_ARRAY(:region))").bindparams(
                    region=selected_region
                )
            )

    def filter_by_language(self, query: Query, selected_language: str):
        if ROMM_DB_DRIVER == "postgresql":
            return query.filter(
                text("languages @> (:language)::jsonb").bindparams(
                    language=f'["{selected_language}"]'
                )
            )
        else:
            return query.filter(
                text("JSON_OVERLAPS(languages, JSON_ARRAY(:language))").bindparams(
                    language=selected_language
                )
            )

    @begin_session
    def filter_roms(
        self,
        query: Query,
        platform_id: int | None = None,
        collection_id: int | None = None,
        virtual_collection_id: str | None = None,
        search_term: str | None = None,
        unmatched_only: bool = False,
        matched_only: bool = False,
        favourites_only: bool = False,
        duplicates_only: bool = False,
        playables_only: bool = False,
        ra_only: bool = False,
        group_by_meta_id: bool = False,
        selected_genre: str | None = None,
        selected_franchise: str | None = None,
        selected_collection: str | None = None,
        selected_company: str | None = None,
        selected_age_rating: str | None = None,
        selected_status: str | None = None,
        selected_region: str | None = None,
        selected_language: str | None = None,
        user_id: int | None = None,
        session: Session = None,
    ) -> Query:
        if platform_id:
            query = self.filter_by_platform_id(query, platform_id)

        if collection_id:
            query = self.filter_by_collection_id(query, session, collection_id)

        if virtual_collection_id:
            query = self.filter_by_virtual_collection_id(
                query, session, virtual_collection_id
            )

        if search_term:
            query = self.filter_by_search_term(query, search_term)

        if unmatched_only:
            query = self.filter_by_unmatched_only(query)

        if matched_only:
            query = self.filter_by_matched_only(query)

        if favourites_only and user_id:
            query = self.filter_by_favourites_only(query, session, user_id)

        if duplicates_only:
            query = self.filter_by_duplicates_only(query)

        if playables_only:
            query = self.filter_by_playables_only(query)

        if ra_only:
            query = self.filter_by_ra_only(query)

        if group_by_meta_id:

            def build_func(provider: str, column: InstrumentedAttribute):
                if platform_id:
                    return func.concat(provider, "-", Rom.platform_id, "-", column)

                return func.concat(provider, "-", Rom.platform_id, "-", column)

            group_id = case(
                {
                    Rom.igdb_id.isnot(None): build_func("igdb", Rom.igdb_id),
                    Rom.moby_id.isnot(None): build_func("moby", Rom.moby_id),
                    Rom.ss_id.isnot(None): build_func("ss", Rom.ss_id),
                },
                else_=build_func("romm", Rom.id),
            )

            # Convert NULL is_main_sibling to 0 (false) so it sorts after true values
            is_main_sibling_order = (
                func.coalesce(cast(RomUser.is_main_sibling, Integer), 0).desc()
                if user_id
                else literal(1)
            )

            # Create a subquery that identifies the first ROM in each group
            group_subquery = (
                session.query(Rom.id)
                .outerjoin(
                    RomUser, and_(RomUser.rom_id == Rom.id, RomUser.user_id == user_id)
                )
                .add_columns(
                    group_id.label("group_id"),
                    func.row_number()
                    .over(
                        partition_by=group_id,
                        order_by=[is_main_sibling_order, Rom.fs_name_no_ext],
                    )
                    .label("row_num"),
                )
                .subquery()
            )

            # Add a filter to the original query to only include the first ROM from each group
            query = query.filter(
                Rom.id.in_(
                    session.query(group_subquery.c.id).filter(
                        group_subquery.c.row_num == 1
                    )
                )
            )

        if (
            selected_genre
            or selected_franchise
            or selected_collection
            or selected_company
            or selected_age_rating
        ):
            query = query.join(RomMetadata)

        if selected_genre:
            query = self.filter_by_genre(query, selected_genre)

        if selected_franchise:
            query = self.filter_by_franchise(query, selected_franchise)

        if selected_collection:
            query = self.filter_by_collection(query, selected_collection)

        if selected_company:
            query = self.filter_by_company(query, selected_company)

        if selected_age_rating:
            query = self.filter_by_age_rating(query, selected_age_rating)

        if selected_region:
            query = self.filter_by_region(query, selected_region)

        if selected_language:
            query = self.filter_by_language(query, selected_language)

        # The RomUser table is already joined if user_id is set
        if selected_status and user_id:
            query = self.filter_by_status(query, selected_status)
        elif user_id:
            query = query.filter(
                or_(RomUser.hidden.is_(False), RomUser.hidden.is_(None))
            )

        return query

    @with_simple
    @begin_session
    def get_roms_query(
        self,
        *,
        order_by: str = "name",
        order_dir: str = "asc",
        user_id: int | None = None,
        query: Query = None,
        session: Session = None,
    ) -> Query:
        if user_id:
            query = query.outerjoin(
                RomUser, and_(RomUser.rom_id == Rom.id, RomUser.user_id == user_id)
            )

        if user_id and hasattr(RomUser, order_by) and not hasattr(Rom, order_by):
            order_attr = getattr(RomUser, order_by)
            query = query.filter(RomUser.user_id == user_id, order_attr.isnot(None))
        elif hasattr(RomMetadata, order_by) and not hasattr(Rom, order_by):
            order_attr = getattr(RomMetadata, order_by)
            query = query.outerjoin(RomMetadata, RomMetadata.rom_id == Rom.id).filter(
                order_attr.isnot(None)
            )
        elif hasattr(Rom, order_by):
            order_attr = getattr(Rom, order_by)
        else:
            order_attr = Rom.name

        # Handle computed properties
        if order_by == "fs_size_bytes":
            subquery = (
                session.query(
                    RomFile.rom_id,
                    func.sum(RomFile.file_size_bytes).label("total_size"),
                )
                .group_by(RomFile.rom_id)
                .subquery()
            )
            query = query.outerjoin(subquery, Rom.id == subquery.c.rom_id)
            order_attr = func.coalesce(subquery.c.total_size, 0)

        # Ignore case when the order attribute is a number
        if isinstance(order_attr.type, (String, Text)):
            # Remove any leading articles
            order_attr = func.trim(
                func.lower(order_attr).regexp_replace(r"^(the|a|an)\s+", "", "i")
            )

        if order_dir.lower() == "desc":
            order_attr = order_attr.desc()
        else:
            order_attr = order_attr.asc()

        return query.order_by(order_attr)

    @begin_session
    def get_roms_scalar(
        self,
        *,
        session: Session = None,
        **kwargs,
    ) -> Sequence[Rom]:
        query = self.get_roms_query(
            order_by=kwargs.pop("order_by", "name"),
            order_dir=kwargs.pop("order_dir", "asc"),
            user_id=kwargs.pop("user_id", None),
        )
        roms = self.filter_roms(
            query=query,
            platform_id=kwargs.pop("platform_id", None),
            collection_id=kwargs.pop("collection_id", None),
            virtual_collection_id=kwargs.pop("virtual_collection_id", None),
            search_term=kwargs.pop("search_term", None),
            unmatched_only=kwargs.pop("unmatched_only", False),
            matched_only=kwargs.pop("matched_only", False),
            favourites_only=kwargs.pop("favourites_only", False),
            duplicates_only=kwargs.pop("duplicates_only", False),
            selected_genre=kwargs.pop("selected_genre", None),
            selected_franchise=kwargs.pop("selected_franchise", None),
            selected_collection=kwargs.pop("selected_collection", None),
            selected_company=kwargs.pop("selected_company", None),
            selected_age_rating=kwargs.pop("selected_age_rating", None),
            selected_status=kwargs.pop("selected_status", None),
            selected_region=kwargs.pop("selected_region", None),
            selected_language=kwargs.pop("selected_language", None),
            user_id=kwargs.pop("user_id", None),
        )
        return session.scalars(roms).all()

    @begin_session
    def get_char_index(
        self, query: Query, session: Session = None
    ) -> List[Row[Tuple[str, int]]]:
        # Get the row number and first letter for each item
        subquery = query.add_columns(
            func.lower(func.substring(Rom.name, 1, 1)).label("letter"),
            func.row_number().over(order_by=Rom.name).label("position"),
        ).subquery()

        # Get the minimum position for each letter
        return (
            session.query(
                subquery.c.letter, func.min(subquery.c.position - 1).label("position")
            )
            .group_by(subquery.c.letter)
            .order_by(subquery.c.letter)
            .all()
        )

    @begin_session
    @with_details
    def get_rom_by_fs_name(
        self,
        platform_id: int,
        fs_name: str,
        query: Query = None,
        session: Session = None,
    ) -> Rom | None:
        return session.scalar(
            query.filter_by(platform_id=platform_id, fs_name=fs_name).limit(1)
        )

    @begin_session
    @with_details
    def get_roms_by_fs_name(
        self,
        platform_id: int,
        fs_names: Iterable[str],
        query: Query = None,
        session: Session = None,
    ) -> dict[str, Rom]:
        """Retrieve a dictionary of roms by their filesystem names."""
        roms = (
            session.scalars(
                query.filter(Rom.fs_name.in_(fs_names)).filter_by(
                    platform_id=platform_id
                )
            )
            .unique()
            .all()
        )
        return {rom.fs_name: rom for rom in roms}

    @begin_session
    @with_details
    def get_rom_by_fs_name_no_tags(
        self, fs_name_no_tags: str, query: Query = None, session: Session = None
    ) -> Rom | None:
        return session.scalar(query.filter_by(fs_name_no_tags=fs_name_no_tags).limit(1))

    @begin_session
    @with_details
    def get_rom_by_fs_name_no_ext(
        self, fs_name_no_ext: str, query: Query = None, session: Session = None
    ) -> Rom | None:
        return session.scalar(query.filter_by(fs_name_no_ext=fs_name_no_ext).limit(1))

    @begin_session
    def update_rom(self, id: int, data: dict, session: Session = None) -> Rom:
        session.execute(
            update(Rom)
            .where(Rom.id == id)
            .values(**data)
            .execution_options(synchronize_session="evaluate")
        )
        return session.query(Rom).filter_by(id=id).one()

    @begin_session
    def delete_rom(self, id: int, session: Session = None) -> None:
        session.execute(
            delete(Rom)
            .where(Rom.id == id)
            .execution_options(synchronize_session="evaluate")
        )

    @begin_session
    def purge_roms(
        self, platform_id: int, fs_roms_to_keep: list[str], session: Session = None
    ) -> Sequence[Rom]:
        purged_roms = (
            session.scalars(
                select(Rom)
                .order_by(Rom.fs_name.asc())
                .where(
                    and_(
                        Rom.platform_id == platform_id,
                        Rom.fs_name.not_in(fs_roms_to_keep),
                    )
                )
            )
            .unique()
            .all()
        )
        session.execute(
            delete(Rom)
            .where(
                and_(
                    Rom.platform_id == platform_id,
                    Rom.fs_name.not_in(fs_roms_to_keep),
                )
            )
            .execution_options(synchronize_session="evaluate")
        )
        return purged_roms

    @begin_session
    def add_rom_user(
        self, rom_id: int, user_id: int, session: Session = None
    ) -> RomUser:
        return session.merge(RomUser(rom_id=rom_id, user_id=user_id))

    @begin_session
    def get_rom_user(
        self, rom_id: int, user_id: int, session: Session = None
    ) -> RomUser | None:
        return session.scalar(
            select(RomUser).filter_by(rom_id=rom_id, user_id=user_id).limit(1)
        )

    @begin_session
    def get_rom_user_by_id(self, id: int, session: Session = None) -> RomUser | None:
        return session.scalar(select(RomUser).filter_by(id=id).limit(1))

    @begin_session
    def update_rom_user(
        self, id: int, data: dict, session: Session = None
    ) -> RomUser | None:
        session.execute(
            update(RomUser)
            .where(RomUser.id == id)
            .values(**data)
            .execution_options(synchronize_session="evaluate")
        )

        rom_user = self.get_rom_user_by_id(id)
        if not rom_user:
            return None

        if not data.get("is_main_sibling", False):
            return rom_user

        rom = self.get_rom(rom_user.rom_id)
        if not rom:
            return rom_user

        session.execute(
            update(RomUser)
            .where(
                and_(
                    RomUser.rom_id.in_(r.id for r in rom.sibling_roms),
                    RomUser.user_id == rom_user.user_id,
                )
            )
            .values(is_main_sibling=False)
        )

        return session.query(RomUser).filter_by(id=id).one()

    @begin_session
    def add_rom_file(self, rom_file: RomFile, session: Session = None) -> RomFile:
        return session.merge(rom_file)

    @begin_session
    def get_rom_file_by_id(self, id: int, session: Session = None) -> RomFile | None:
        return session.scalar(select(RomFile).filter_by(id=id).limit(1))

    @begin_session
    def update_rom_file(self, id: int, data: dict, session: Session = None) -> RomFile:
        session.execute(
            update(RomFile)
            .where(RomFile.id == id)
            .values(**data)
            .execution_options(synchronize_session="evaluate")
        )

        return session.query(RomFile).filter_by(id=id).one()

    @begin_session
    def purge_rom_files(
        self, rom_id: int, session: Session = None
    ) -> Sequence[RomFile]:
        purged_rom_files = (
            session.scalars(select(RomFile).filter_by(rom_id=rom_id)).unique().all()
        )
        session.execute(
            delete(RomFile)
            .where(RomFile.rom_id == rom_id)
            .execution_options(synchronize_session="evaluate")
        )
        return purged_rom_files

    # Cheat Code Operations

    def _get_cheats_file_path(self, rom):
        """
        Get the path to the cheats.txt file for a ROM.

        Args:
            rom: The ROM object

        Returns:
            tuple: (cheats_dir, cheats_file) paths
        """
        import os

        from config import RESOURCES_BASE_PATH

        cheats_dir = os.path.join(RESOURCES_BASE_PATH, rom.fs_resources_path, "cheats")
        cheats_file = os.path.join(cheats_dir, "cheats.txt")

        return cheats_dir, cheats_file

    def _read_cheats_from_file(self, rom):
        """
        Read cheat codes from the ROM's cheats.txt file.

        Args:
            rom: The ROM object

        Returns:
            list: List of dictionaries containing cheat code data
        """
        from backend.config.cheat_type_manager import cheat_type_manager

        cheats_dir, cheats_file = self._get_cheats_file_path(rom)

        import os

        if not os.path.exists(cheats_file):
            return []

        cheat_codes = []
        current_cheat = {
            "name": "",
            "description": "",
            "type": "raw",  # Default to raw type
            "code": "",
        }

        with open(cheats_file, "r", encoding="utf-8") as f:
            lines = f.readlines()

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Skip empty lines between cheats
            if not line:
                # If we have a code, save the current cheat and start a new one
                if current_cheat["code"]:
                    cheat_codes.append(current_cheat.copy())
                    current_cheat = {
                        "name": "",
                        "description": "",
                        "type": "raw",  # Default to raw type
                        "code": "",
                    }
                i += 1
                continue

            # Parse metadata comments
            if line.startswith("# Name:"):
                current_cheat["name"] = line[len("# Name:") :].strip()
            elif line.startswith("# Description:"):
                current_cheat["description"] = line[len("# Description:") :].strip()
            elif line.startswith("# Type:"):
                type_value = line[len("# Type:") :].strip().lower()
                # Validate type is a valid config value
                valid_types = cheat_type_manager.get_all_type_ids()
                current_cheat["type"] = (
                    type_value if type_value in valid_types else "raw"
                )
            # If not a comment, it's a code
            elif not line.startswith("#"):
                current_cheat["code"] = line

            i += 1

        # Add the last cheat if there is one
        if current_cheat["code"]:
            cheat_codes.append(current_cheat)

        return cheat_codes

    def _write_cheats_to_file(self, rom, session):
        """
        Write all cheat codes for a ROM to cheats.txt in the appropriate directory.
        """
        # Get all cheats for this ROM
        cheat_codes = session.scalars(select(CheatCode).filter_by(rom_id=rom.id)).all()

        # Build cheats.txt content
        lines = []
        for cheat in cheat_codes:
            # Write name and description as comments, then the code
            if cheat.name:
                lines.append(f"# Name: {cheat.name}")
            if cheat.description:
                lines.append(f"# Description: {cheat.description}")
            if cheat.type:
                lines.append(f"# Type: {cheat.type}")
            lines.append(str(cheat.code))
            lines.append("")  # Blank line between cheats

        content = "\n".join(lines).strip() + "\n" if lines else ""

        # Determine cheats directory
        cheats_dir, cheats_file = self._get_cheats_file_path(rom)
        import os

        os.makedirs(cheats_dir, exist_ok=True)

        # Write to file
        with open(cheats_file, "w", encoding="utf-8") as f:
            f.write(content)

    @begin_session
    def sync_cheats(self, rom_id: int, session: Session = None) -> None:
        """
        Synchronize cheat codes between the database and flat file.

        This method:
        1. Reads cheat codes from the flat file
        2. Compares with database cheat codes
        3. Adds missing cheat codes to the database
        4. Updates the flat file with all cheat codes

        Args:
            rom_id: The ROM ID
            session: SQLAlchemy session
        """
        rom = self.get_rom(rom_id)
        if not rom:
            return

        # Get cheat codes from database
        db_cheat_codes = session.scalars(
            select(CheatCode).filter_by(rom_id=rom_id)
        ).all()

        # Get cheat codes from file
        file_cheat_codes = self._read_cheats_from_file(rom)

        # Create a dictionary of existing cheat codes by code value for quick lookup
        existing_codes = {cheat.code: cheat for cheat in db_cheat_codes}

        # Add cheat codes from file that don't exist in the database
        for file_cheat in file_cheat_codes:
            if file_cheat["code"] not in existing_codes:
                # Add new cheat code to database
                from validators.cheat_code import CheatCodeValidator

                # Sanitize input data
                sanitized_data = CheatCodeValidator.sanitize_cheat_code(file_cheat)

                cheat_code = CheatCode(
                    rom_id=rom_id,
                    name=sanitized_data["name"],
                    code=sanitized_data["code"],
                    description=sanitized_data["description"],
                    type=sanitized_data["type"],
                )
                session.add(cheat_code)
            else:
                # Update existing cheat code if metadata differs
                existing_cheat = existing_codes[file_cheat["code"]]
                if (
                    existing_cheat.name != file_cheat["name"]
                    or existing_cheat.description != file_cheat["description"]
                    or existing_cheat.type != file_cheat["type"]
                ):

                    # Prioritize database values over file values
                    # This is a policy decision - we could also choose to prioritize file values
                    # or implement more complex conflict resolution
                    pass

        # Flush changes to get IDs for new cheat codes
        session.flush()

        # Write all cheats back to file (including any that were only in the database)
        self._write_cheats_to_file(rom, session)

    @begin_session
    def add_cheat_code(self, rom_id: int, data: dict, session: Session = None) -> dict:
        """Add a new cheat code for a ROM"""
        from validators.cheat_code import CheatCodeValidator

        # Sanitize input data
        sanitized_data = CheatCodeValidator.sanitize_cheat_code(data)

        # First sync existing cheats to ensure we have the latest from the file
        self.sync_cheats(rom_id, session=session)

        cheat_code = CheatCode(
            rom_id=rom_id,
            name=sanitized_data["name"],
            code=sanitized_data["code"],
            description=sanitized_data["description"],
            type=sanitized_data["type"],
        )
        session.add(cheat_code)
        session.flush()

        # Write all cheats to file
        rom = self.get_rom(rom_id)
        if rom:
            self._write_cheats_to_file(rom, session)

        return {
            "id": cheat_code.id,
            "name": cheat_code.name,
            "code": cheat_code.code,
            "description": cheat_code.description,
            "type": cheat_code.type,
        }

    @begin_session
    def update_cheat_code(
        self, cheat_id: int, data: dict, session: Session = None
    ) -> dict:
        """Update an existing cheat code"""
        from validators.cheat_code import CheatCodeValidator

        # Get the cheat code to update
        cheat_code = session.query(CheatCode).filter_by(id=cheat_id).one_or_none()
        if not cheat_code:
            raise ValueError(f"Cheat code with ID {cheat_id} not found")

        # First sync existing cheats to ensure we have the latest from the file
        self.sync_cheats(cheat_code.rom_id, session=session)

        # Sanitize input data
        sanitized_data = CheatCodeValidator.sanitize_cheat_code(data)

        session.execute(
            update(CheatCode)
            .where(CheatCode.id == cheat_id)
            .values(
                name=sanitized_data["name"],
                code=sanitized_data["code"],
                description=sanitized_data["description"],
                type=sanitized_data["type"],
            )
            .execution_options(synchronize_session="evaluate")
        )
        cheat_code = session.query(CheatCode).filter_by(id=cheat_id).one()

        # Write all cheats to file
        rom = self.get_rom(cheat_code.rom_id)
        if rom:
            self._write_cheats_to_file(rom, session)

        return {
            "id": cheat_code.id,
            "name": cheat_code.name,
            "code": cheat_code.code,
            "description": cheat_code.description,
            "type": cheat_code.type,
        }

    @begin_session
    def delete_cheat_code(self, cheat_id: int, session: Session = None) -> None:
        """Delete a cheat code"""
        # Get the cheat code and its rom_id before deleting
        cheat_code = session.query(CheatCode).filter_by(id=cheat_id).one_or_none()
        rom_id = cheat_code.rom_id if cheat_code else None

        if rom_id:
            # First sync existing cheats to ensure we have the latest from the file
            self.sync_cheats(rom_id, session=session)

        session.execute(
            delete(CheatCode)
            .where(CheatCode.id == cheat_id)
            .execution_options(synchronize_session="evaluate")
        )

        # Write all cheats to file
        if rom_id:
            rom = self.get_rom(rom_id)
            if rom:
                self._write_cheats_to_file(rom, session)

    @begin_session
    def get_cheat_codes(self, rom_id: int, session: Session = None) -> list[dict]:
        """Get all cheat codes for a ROM"""
        # First sync existing cheats to ensure we have the latest from the file
        self.sync_cheats(rom_id, session=session)

        cheat_codes = session.scalars(select(CheatCode).filter_by(rom_id=rom_id)).all()
        return [
            {
                "id": code.id,
                "name": code.name,
                "code": code.code,
                "description": code.description,
                "type": code.type,
            }
            for code in cheat_codes
        ]

    # Cheat File Operations
    @begin_session
    async def upload_cheat_file(
        self, rom_id: int, file_data: dict, session: Session = None
    ) -> dict:
        """Upload a cheat file for a ROM"""
        import os

        from anyio import Path
        from config import RESOURCES_BASE_PATH
        from handler.filesystem import fs_rom_handler

        rom = self.get_rom(rom_id)
        if not rom:
            raise Exception("ROM not found")

        # Create the cheat files directory if it doesn't exist
        cheat_files_path = f"{RESOURCES_BASE_PATH}/{rom.fs_resources_path}/cheats"
        if not os.path.exists(cheat_files_path):
            await Path(cheat_files_path).mkdir(parents=True, exist_ok=True)

        # Save the file to the filesystem
        file_name = file_data.get("file_name", "cheat_file.cht")
        file_path = f"{cheat_files_path}/{file_name}"
        file_content = file_data.get("file_content", "")

        await Path(file_path).write_text(file_content)

        # Store metadata in the database
        cheat_file = CheatFile(
            rom_id=rom_id,
            file_name=file_name,
            file_path=file_path,
            file_size_bytes=len(file_content),
        )
        session.add(cheat_file)
        session.flush()

        return {
            "id": cheat_file.id,
            "rom_id": rom_id,
            "file_name": file_name,
            "file_size": len(file_content),
            "uploaded_at": cheat_file.uploaded_at.isoformat(),
        }

    @begin_session
    def get_cheat_files(self, rom_id: int, session: Session = None) -> list[dict]:
        """Get all cheat files for a ROM"""
        cheat_files = session.scalars(select(CheatFile).filter_by(rom_id=rom_id)).all()
        return [
            {
                "id": file.id,
                "rom_id": file.rom_id,
                "file_name": file.file_name,
                "file_size": file.file_size_bytes,
                "uploaded_at": file.uploaded_at.isoformat(),
            }
            for file in cheat_files
        ]

    @begin_session
    def delete_cheat_file(self, file_id: int, session: Session = None) -> None:
        """Delete a cheat file"""
        cheat_file = session.scalar(select(CheatFile).filter_by(id=file_id))
        if cheat_file:
            # Delete the file from the filesystem
            import os

            if os.path.exists(cheat_file.file_path):
                os.remove(cheat_file.file_path)

            # Delete the record from the database
            session.execute(
                delete(CheatFile)
                .where(CheatFile.id == file_id)
                .execution_options(synchronize_session="evaluate")
            )
