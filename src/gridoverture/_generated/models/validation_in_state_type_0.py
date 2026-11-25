from enum import StrEnum

class ValidationInStateType0(StrEnum):
    EDITED = "edited"
    SOURCE = "source"
    WRITTEN = "written"

    def __str__(self) -> str:
        return str(self.value)
