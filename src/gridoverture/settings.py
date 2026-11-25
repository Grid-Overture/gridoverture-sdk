# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The typed settings of each study, as PowerFactory's ComLdf is for its load flow. Each is a frozen
dataclass that refuses a value outside the allowed ones when it is built, before any request.

Only the power flow names an engine, and only an open one: a study has a kind, and the platform
chooses what runs it.
"""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from typing import Any, Literal, get_args

Engine = Literal["openloadflow", "veragrid", "pandapower"]
Start = Literal["dc", "flat", "solution"]
Level = Literal["structure", "consistency", "physics"]
ExportFormat = Literal["raw", "matpower", "veragrid", "pandapower", "cgmes"]
"""The formats a version may be exported to."""
RawVersion = Literal[33, 35]
Packaging = Literal["zip", "folder"]


def one_of(name, value, allowed):
    """Refuse `value` unless it is one of the Literal `allowed`."""
    choices = get_args(allowed)
    # bool is an int, and True == 1: a flag passed where a number goes must not slip through
    if isinstance(value, bool) or value not in choices:
        raise ValueError(f"{name} is {value!r}: one of {', '.join(map(repr, choices))}")


def flag(name, value):
    if not isinstance(value, bool):
        raise ValueError(f"{name} is {value!r}: True or False")


@dataclass(frozen=True)
class PowerFlowSettings:
    """
    How a power flow runs.

    Attributes:
        engine: The open engine to run it on: "openloadflow", "veragrid" or "pandapower". None
            leaves the choice to the API, whose default is "openloadflow".
        start: Where the iterations start from: "dc" (a DC power flow), "flat" (1 pu, 0 degrees)
            or "solution" (the model's own solved voltages).
        reactive_limits: Hold machines within their reactive limits.
        controls: Let tap changers and switched shunts regulate.
    """

    engine: Engine | None = None
    start: Start = "dc"
    reactive_limits: bool = True
    controls: bool = False

    def __post_init__(self):
        if self.engine is not None:
            one_of("engine", self.engine, Engine)
        one_of("start", self.start, Start)
        flag("reactive_limits", self.reactive_limits)
        flag("controls", self.controls)

    def _body(self) -> dict[str, Any]:
        body: dict[str, Any] = {
            "start": self.start,
            "reactive_limits": self.reactive_limits,
            "controls": self.controls,
        }
        if self.engine is not None:
            body["engine"] = self.engine
        return body


@dataclass(frozen=True)
class ValidationSettings:
    """
    Which levels of checks a validation runs.

    Attributes:
        levels: Any of "structure" (the model is well formed), "consistency" (its parts agree with
            each other) and "physics" (its values are plausible). All three by default.
    """

    levels: Sequence[Level] = ("structure", "consistency", "physics")

    def __post_init__(self):
        levels = (self.levels,) if isinstance(self.levels, str) else tuple(self.levels)
        if not levels:
            raise ValueError(
                "levels is empty: give at least one of structure, consistency, physics"
            )
        for level in levels:
            one_of("a level", level, Level)
        object.__setattr__(self, "levels", levels)

    def _body(self) -> dict[str, Any]:
        return {"levels": list(self.levels)}


@dataclass(frozen=True)
class ExportSettings:
    """
    The file an export writes.

    Attributes:
        format: "raw" (PSS/E), "matpower", "veragrid", "pandapower" or "cgmes" (CGMES 3.0).
        raw_version: The PSS/E RAW version, 33 or 35, for format="raw".
        packaging: For format="cgmes", "zip" or "folder" (a zip of the profiles' folder). None
            leaves it to the API.
    """

    format: ExportFormat
    raw_version: RawVersion = 33
    packaging: Packaging | None = None

    def __post_init__(self):
        one_of("format", self.format, ExportFormat)
        one_of("raw_version", self.raw_version, RawVersion)
        if self.packaging is not None:
            one_of("packaging", self.packaging, Packaging)

    def _body(self) -> dict[str, Any]:
        body: dict[str, Any] = {"format": self.format, "version": self.raw_version}
        if self.packaging is not None:
            body["packaging"] = self.packaging
        return body
