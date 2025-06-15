import re
from typing import Dict, Optional, Union

from backend.config.cheat_type_manager import cheat_type_manager


class CheatCodeValidator:
    """Validator for cheat code inputs"""

    @staticmethod
    def validate_cheat_code(data: Dict) -> Dict[str, Union[str, Dict[str, str]]]:
        """
        Validate cheat code data

        Args:
            data: Dictionary containing cheat code data

        Returns:
            Dictionary with validation errors if any
        """
        errors = {}

        # Validate name
        if "name" not in data or not data["name"]:
            errors["name"] = "Cheat code name is required"
        elif not isinstance(data["name"], str):
            errors["name"] = "Cheat code name must be a string"
        elif len(data["name"]) > 255:
            errors["name"] = "Cheat code name must be 255 characters or less"

        # Validate code
        if "code" not in data or not data["code"]:
            errors["code"] = "Cheat code is required"
        elif not isinstance(data["code"], str):
            errors["code"] = "Cheat code must be a string"
        elif len(data["code"]) > 255:
            errors["code"] = "Cheat code must be 255 characters or less"

        # Validate description (optional but must be string if provided)
        if "description" in data and data["description"] is not None:
            if not isinstance(data["description"], str):
                errors["description"] = "Description must be a string"

        # Validate type
        if "type" not in data or not data["type"]:
            errors["type"] = "Cheat code type is required"
        else:
            # Check if type is valid
            valid_types = cheat_type_manager.get_all_type_ids()
            if data["type"] not in valid_types:
                errors["type"] = (
                    f"Invalid cheat code type. Must be one of: {', '.join(valid_types)}"
                )

        # Validate code format based on type
        if (
            "code" in data
            and "type" in data
            and not errors.get("code")
            and not errors.get("type")
        ):
            code_format_error = CheatCodeValidator.validate_code_format(
                data["code"], data["type"]
            )
            if code_format_error:
                errors["code"] = code_format_error

        return errors

    @staticmethod
    def validate_code_format(code: str, code_type: str) -> Optional[str]:
        """
        Validate the format of a cheat code based on its type

        Args:
            code: The cheat code string
            code_type: The type of cheat code

        Returns:
            Error message if validation fails, None otherwise
        """
        # Remove spaces for validation
        clean_code = code.replace(" ", "")

        if code_type == "raw":
            # Raw codes can be any format, but should not be empty
            if not clean_code:
                return "Raw code cannot be empty"
            return None

        # Get the pattern for this cheat type
        pattern = cheat_type_manager.get_validation_pattern(code_type)

        # Test the code against the pattern
        if not re.match(pattern, clean_code):
            # Get the name of the cheat type for the error message
            cheat_type_info = cheat_type_manager.get_cheat_type(code_type)
            type_name = (
                cheat_type_info["name"] if cheat_type_info else code_type.capitalize()
            )
            return f"{type_name} codes must match the required format"

        return None

    @staticmethod
    def sanitize_cheat_code(data: Dict) -> Dict:
        """
        Sanitize cheat code data to prevent injection attacks

        Args:
            data: Dictionary containing cheat code data

        Returns:
            Sanitized data dictionary
        """
        sanitized = {}

        # Sanitize name
        if "name" in data:
            sanitized["name"] = str(data["name"]).strip()

        # Sanitize code
        if "code" in data:
            sanitized["code"] = str(data["code"]).strip()

        # Sanitize description
        if "description" in data:
            sanitized["description"] = str(data["description"] or "").strip()
        else:
            sanitized["description"] = ""

        # Sanitize type
        if "type" in data:
            type_value = str(data["type"]).strip().lower()
            # Ensure type is a valid config value
            valid_types = cheat_type_manager.get_all_type_ids()
            sanitized["type"] = type_value if type_value in valid_types else "raw"
        else:
            sanitized["type"] = "raw"

        return sanitized
