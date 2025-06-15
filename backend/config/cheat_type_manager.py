import json
import os
import re
from typing import Dict, List, Optional


class CheatTypeManager:
    def __init__(self, config_path: str = "backend/config/cheat_types.json"):
        self.config_path = config_path
        self._cheat_types = {}
        self.load_config()

    def load_config(self) -> None:
        """Load cheat types from the config file"""
        if not os.path.exists(self.config_path):
            # Create default config if it doesn't exist
            self._cheat_types = {
                "raw": {
                    "name": "Raw",
                    "description": "Raw cheat code with no specific format",
                    "pattern": "^.+$",
                    "example": "ABCDEF",
                }
            }
            self.save_config()
            return

        with open(self.config_path, "r", encoding="utf-8") as f:
            try:
                self._cheat_types = json.load(f)
            except json.JSONDecodeError:
                print(f"Error: Invalid JSON in {self.config_path}")
                self._cheat_types = {}

    def save_config(self) -> None:
        """Save cheat types to the config file"""
        with open(self.config_path, "w", encoding="utf-8") as f:
            json.dump(self._cheat_types, f, indent=4)

    def get_all_type_ids(self) -> List[str]:
        """Get all cheat type IDs"""
        return list(self._cheat_types.keys())

    def get_cheat_types(self) -> Dict[str, Dict]:
        """Get all cheat types"""
        return self._cheat_types

    def get_cheat_type(self, type_id: str) -> Optional[Dict]:
        """Get a cheat type by ID"""
        return self._cheat_types.get(type_id)

    def get_validation_pattern(self, type_id: str) -> str:
        """Get the validation pattern for a cheat type"""
        cheat_type = self.get_cheat_type(type_id)
        if cheat_type:
            return cheat_type.get("pattern", "^.+$")
        return "^.+$"  # Default pattern for unknown types

    def add_cheat_type(self, type_id: str, type_data: Dict) -> None:
        """Add a new cheat type"""
        self._cheat_types[type_id] = type_data
        self.save_config()

    def update_cheat_type(self, type_id: str, type_data: Dict) -> None:
        """Update an existing cheat type"""
        if type_id in self._cheat_types:
            self._cheat_types[type_id] = type_data
            self.save_config()
        else:
            raise ValueError(f"Cheat type '{type_id}' does not exist")

    def delete_cheat_type(self, type_id: str) -> None:
        """Delete a cheat type"""
        if type_id in self._cheat_types:
            del self._cheat_types[type_id]
            self.save_config()
        else:
            raise ValueError(f"Cheat type '{type_id}' does not exist")


# Singleton instance
cheat_type_manager = CheatTypeManager()
