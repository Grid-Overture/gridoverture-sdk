from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from typing import Literal, cast

if TYPE_CHECKING:
  from ..models.add_object_values import AddObjectValues





T = TypeVar("T", bound="AddObject")



@_attrs_define
class AddObject:
    """ Adds an object of a concrete CGMES 3.0 class, with a new mRID and its values.

        Attributes:
            op (Literal['add']):
            cim_class (str):
            mrid (str):
            values (AddObjectValues | Unset):
     """

    op: Literal['add']
    cim_class: str
    mrid: str
    values: AddObjectValues | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.add_object_values import AddObjectValues # noqa: PLC0415
        op = self.op

        cim_class = self.cim_class

        mrid = self.mrid

        values: dict[str, Any] | Unset = UNSET
        if not isinstance(self.values, Unset):
            values = self.values.to_dict()


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "op": op,
            "cim_class": cim_class,
            "mrid": mrid,
        })
        if values is not UNSET:
            field_dict["values"] = values

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.add_object_values import AddObjectValues # noqa: PLC0415
        d = dict(src_dict)
        op = cast(Literal['add'] , d.pop("op"))
        if op != 'add':
            raise ValueError(f"op must match const 'add', got '{op}'")

        cim_class = d.pop("cim_class")

        mrid = d.pop("mrid")

        _values = d.pop("values", UNSET)
        values: AddObjectValues | Unset
        if isinstance(_values,  Unset):
            values = UNSET
        else:
            values = AddObjectValues.from_dict(_values)




        add_object = cls(
            op=op,
            cim_class=cim_class,
            mrid=mrid,
            values=values,
        )

        return add_object

