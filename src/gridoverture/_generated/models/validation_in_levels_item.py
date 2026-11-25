from enum import StrEnum

class ValidationInLevelsItem(StrEnum):
    CONSISTENCY = "consistency"
    PHYSICS = "physics"
    STRUCTURE = "structure"

    def __str__(self) -> str:
        return str(self.value)
