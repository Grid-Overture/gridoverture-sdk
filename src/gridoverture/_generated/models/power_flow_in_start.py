from enum import StrEnum

class PowerFlowInStart(StrEnum):
    DC = "dc"
    FLAT = "flat"
    SOLUTION = "solution"

    def __str__(self) -> str:
        return str(self.value)
