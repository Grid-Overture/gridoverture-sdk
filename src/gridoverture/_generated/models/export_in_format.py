from enum import StrEnum

class ExportInFormat(StrEnum):
    CGMES = "cgmes"
    MATPOWER = "matpower"
    PANDAPOWER = "pandapower"
    RAW = "raw"
    VERAGRID = "veragrid"

    def __str__(self) -> str:
        return str(self.value)
