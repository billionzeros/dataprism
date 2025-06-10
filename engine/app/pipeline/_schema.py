from enum import Enum

class GenerativeModel(str, Enum):
    """
    An enumeration for Large Language Model identifiers.
    """
    GEMINI_2_0_FLASH = "gemini/gemini-2.0-flash"
    GEMINI_1_5_PRO = "gemini/gemini-1.5-pro-latest"
    GEMINI_1_0_PRO = "gemini/gemini-1.0-pro"

    def __str__(self):
        """Ensures the string representation is the model's value."""
        return self.value