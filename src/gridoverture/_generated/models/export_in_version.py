from enum import IntEnum

class ExportInVersion(IntEnum):
    VALUE_33 = 33
    VALUE_35 = 35

    def __str__(self) -> str:
        return str(self.value)
