from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from typing import Literal, cast






T = TypeVar("T", bound="SetAttribute")



@_attrs_define
class SetAttribute:
    """ Sets one attribute of an object; null removes its value. A reference takes an mRID.

        Attributes:
            op (Literal['set']):
            mrid (str):
            attribute (str): The class that declares the attribute and its name, as EnergyConsumer.p
            value (bool | float | int | list[bool | float | int | str] | None | str):
     """

    op: Literal['set']
    mrid: str
    attribute: str
    value: bool | float | int | list[bool | float | int | str] | None | str





    def to_dict(self) -> dict[str, Any]:
        op = self.op

        mrid = self.mrid

        attribute = self.attribute

        value: bool | float | int | list[bool | float | int | str] | None | str
        if isinstance(self.value, list):
            value = []
            for value_type_4_item_data in self.value:
                value_type_4_item: bool | float | int | str
                value_type_4_item = value_type_4_item_data
                value.append(value_type_4_item)


        else:
            value = self.value


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "op": op,
            "mrid": mrid,
            "attribute": attribute,
            "value": value,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        op = cast(Literal['set'] , d.pop("op"))
        if op != 'set':
            raise ValueError(f"op must match const 'set', got '{op}'")

        mrid = d.pop("mrid")

        attribute = d.pop("attribute")

        def _parse_value(data: object) -> bool | float | int | list[bool | float | int | str] | None | str:
            if data is None:
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                value_type_4 = []
                _value_type_4 = data
                for value_type_4_item_data in (_value_type_4):
                    def _parse_value_type_4_item(data: object) -> bool | float | int | str:
                        return cast(bool | float | int | str, data)

                    value_type_4_item = _parse_value_type_4_item(value_type_4_item_data)

                    value_type_4.append(value_type_4_item)

                return value_type_4
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(bool | float | int | list[bool | float | int | str] | None | str, data)

        value = _parse_value(d.pop("value"))


        set_attribute = cls(
            op=op,
            mrid=mrid,
            attribute=attribute,
            value=value,
        )

        return set_attribute

