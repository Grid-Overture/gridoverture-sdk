# SPDX-License-Identifier: AGPL-3.0-or-later
"""
A read of a version's CGMES model, client-side, with the standard library: every CIM object of its
profiles, with its class, its name and its attributes, so a script finds what to edit by class and
name, as PowerFactory's GetCalcRelevantObjects does, instead of by mRID alone.

An object's attributes come from every profile that describes it (EQ, SSH, SV ...), merged. A value
reads as a bool or a float when CGMES writes it as one; a reference reads as the mRID it points at;
the rest, names and identifiers among them, stay text.
"""

from __future__ import annotations

import io
import re
import xml.etree.ElementTree as ElementTree
import zipfile
from collections.abc import Mapping
from dataclasses import dataclass, field
from typing import Any

from ._generated.cim_classes import PARENTS

RDF = "{http://www.w3.org/1999/02/22-rdf-syntax-ns#}"
NUMBER = re.compile(r"^[+-]?(\d+\.?\d*|\.\d+)([eE][+-]?\d+)?$")
TEXT_ONLY = ("IdentifiedObject.",)  # a name or a code that looks like a number stays text


def key_of(reference: str) -> str:
    """
    The mRID an rdf:ID, an rdf:about or an rdf:resource names, the same in every form; for an
    enumeration's value, as http://iec.ch/TC57/CIM100#WindingConnection.D, its own name.
    """
    if reference.startswith(("http://", "https://")):
        return reference.rpartition("#")[2]
    return reference.removeprefix("#").removeprefix("urn:uuid:").removeprefix("_")


def is_a(cim_class: str, ancestor: str) -> bool:
    """Whether a CGMES 3.0 class is `ancestor` or specializes it: a NonConformLoad is a load."""
    while cim_class is not None:
        if cim_class == ancestor:
            return True
        cim_class = PARENTS.get(cim_class)
    return False


def typed(attribute: str, text: str | None) -> Any:
    if text is None or attribute.startswith(TEXT_ONLY):
        return text
    stripped = text.strip()
    if stripped in ("true", "false"):
        return stripped == "true"
    if NUMBER.match(stripped):
        return float(stripped)
    return text


@dataclass(frozen=True)
class CimObject:
    """
    One object of a version's CGMES model.

    Attributes:
        mrid: Its mRID, which an edit names it by.
        cim_class: Its concrete class, as "NonConformLoad".
        values: Its attributes by CIM name, as {"EnergyConsumer.p": 94.2}, from every profile.
    """

    mrid: str
    cim_class: str
    values: Mapping[str, Any] = field(default_factory=dict)

    @property
    def name(self) -> str | None:
        """Its IdentifiedObject.name; None when it has none."""
        return self.values.get("IdentifiedObject.name")

    def __getitem__(self, attribute: str) -> Any:
        return self.values[attribute]

    def get(self, attribute: str, default: Any = None) -> Any:
        """The value of an attribute by its CIM name, or `default` when the model gives none."""
        return self.values.get(attribute, default)


def objects_of(data: bytes) -> list[CimObject]:
    """Every CIM object of a model's zip, a CGMES model or a .gostudio, in the order first read."""
    classes: dict[str, str] = {}
    values: dict[str, dict[str, Any]] = {}
    with zipfile.ZipFile(io.BytesIO(data)) as bundle:
        for member in sorted(bundle.namelist()):
            if member.lower().endswith(".xml"):
                with bundle.open(member) as file:
                    read(file, classes, values)
    return [CimObject(mrid, cls, values.get(mrid, {})) for mrid, cls in classes.items()]


def read(file, classes: dict[str, str], values: dict[str, dict[str, Any]]) -> None:
    for _, element in ElementTree.iterparse(file, events=("end",)):
        identifier = element.get(f"{RDF}ID") or element.get(f"{RDF}about")
        if identifier is None or not element.tag.startswith("{"):
            continue
        namespace, _, cls = element.tag[1:].partition("}")
        # CIM's own classes, not the header of each file (ModelDescription's FullModel)
        if not namespace.startswith("http://iec.ch/TC57/") or "ModelDescription" in namespace:
            continue
        mrid = key_of(identifier)
        # the profile that defines it (rdf:ID) says its class; another only describes it
        if element.get(f"{RDF}ID") is not None or mrid not in classes:
            classes[mrid] = cls
        kept = values.setdefault(mrid, {})
        for child in element:
            attribute = child.tag.rpartition("}")[2]
            resource = child.get(f"{RDF}resource")
            kept[attribute] = (
                key_of(resource) if resource is not None else typed(attribute, child.text)
            )
        element.clear()
