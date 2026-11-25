from enum import StrEnum

class ExportInPackagingType0(StrEnum):
    FOLDER = "folder"
    ZIP = "zip"

    def __str__(self) -> str:
        return str(self.value)
