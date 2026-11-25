from enum import StrEnum

class PowerFlowInEngine(StrEnum):
    OPENLOADFLOW = "openloadflow"
    PANDAPOWER = "pandapower"
    VERAGRID = "veragrid"

    def __str__(self) -> str:
        return str(self.value)
