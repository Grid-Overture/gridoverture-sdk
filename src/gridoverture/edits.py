# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The edits a child version is made with. A version holds a CGMES 3.0 model, so an edit names an
object by its mRID and an attribute by its CIM name: the class that declares it and its own name,
as in "EnergyConsumer.p". The API checks their shape and the engine checks each against ENTSO-E's
schema; a wrong one comes back as an error, never silently ignored.
"""

from __future__ import annotations

from collections.abc import Mapping
from dataclasses import dataclass
from typing import Any

Scalar = bool | int | float | str
Value = Scalar | list[Scalar] | None


@dataclass(frozen=True)
class SetAttribute:
    """
    Set one attribute of an object, as PowerFactory's SetAttribute does.

    Attributes:
        mrid: The object's mRID.
        attribute: The attribute's CIM name, as "EnergyConsumer.p".
        value: Its new value; None removes it. A reference takes the mRID it points at.
    """

    mrid: str
    attribute: str
    value: Value

    def _body(self) -> dict[str, Any]:
        return {"op": "set", "mrid": self.mrid, "attribute": self.attribute, "value": self.value}


@dataclass(frozen=True)
class AddObject:
    """
    Add an object of a concrete CGMES 3.0 class, with a new mRID and its values.

    Attributes:
        cim_class: The class, as "EnergyConsumer".
        mrid: The new object's mRID.
        values: Its attributes by CIM name, as {"IdentifiedObject.name": "Load 7"}.
    """

    cim_class: str
    mrid: str
    values: Mapping[str, Value] | None = None

    def _body(self) -> dict[str, Any]:
        return {
            "op": "add",
            "cim_class": self.cim_class,
            "mrid": self.mrid,
            "values": dict(self.values or {}),
        }


@dataclass(frozen=True)
class RemoveObject:
    """
    Remove an object. Once every edit applies, nothing may point at what was removed.

    Attributes:
        mrid: The object's mRID.
        dependents: Also remove the objects that exist only for it: its terminals, their flows and
            limits, a transformer's ends.
    """

    mrid: str
    dependents: bool = False

    def _body(self) -> dict[str, Any]:
        return {"op": "remove", "mrid": self.mrid, "dependents": self.dependents}


Edit = SetAttribute | AddObject | RemoveObject
"""Any of the three edits."""
