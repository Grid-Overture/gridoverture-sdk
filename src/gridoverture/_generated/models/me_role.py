from enum import StrEnum

class MeRole(StrEnum):
    ADMINISTRATOR = "administrator"
    EDITOR = "editor"
    READER = "reader"

    def __str__(self) -> str:
        return str(self.value)
