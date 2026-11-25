from enum import StrEnum

class ValidationInOriginType0(StrEnum):
    SOURCE = "source"
    WRITTEN = "written"

    def __str__(self) -> str:
        return str(self.value)
