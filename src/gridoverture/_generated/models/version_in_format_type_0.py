from enum import StrEnum

class VersionInFormatType0(StrEnum):
    CDF = "cdf"
    CGMES = "cgmes"
    MATPOWER = "matpower"
    PANDAPOWER = "pandapower"
    PF2XML = "pf2xml"
    RAW = "raw"
    VERAGRID = "veragrid"

    def __str__(self) -> str:
        return str(self.value)
