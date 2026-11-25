from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import Literal, cast






T = TypeVar("T", bound="RemoveObject")



@_attrs_define
class RemoveObject:
    """ Removes an object, and with `dependents` the objects that exist only for it: its terminals,
    their flows and limits, a transformer's ends. Once every edit applies, nothing may point at
    what was removed.

        Attributes:
            op (Literal['remove']):
            mrid (str):
            dependents (bool | Unset):  Default: False.
     """

    op: Literal['remove']
    mrid: str
    dependents: bool | Unset = False





    def to_dict(self) -> dict[str, Any]:
        op = self.op

        mrid = self.mrid

        dependents = self.dependents


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "op": op,
            "mrid": mrid,
        })
        if dependents is not UNSET:
            field_dict["dependents"] = dependents

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        op = cast(Literal['remove'] , d.pop("op"))
        if op != 'remove':
            raise ValueError(f"op must match const 'remove', got '{op}'")

        mrid = d.pop("mrid")

        dependents = d.pop("dependents", UNSET)

        remove_object = cls(
            op=op,
            mrid=mrid,
            dependents=dependents,
        )

        return remove_object

