from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.validation_in_levels_item import ValidationInLevelsItem
from ..models.validation_in_origin_type_0 import ValidationInOriginType0
from ..models.validation_in_state_type_0 import ValidationInStateType0
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.source import Source





T = TypeVar("T", bound="ValidationIn")



@_attrs_define
class ValidationIn:
    """ A validation at the levels asked, worded by where the model's solution comes from.

        Attributes:
            source (Source): What a job of the Studio's work reads: a version, or an artifact (a session's snapshot).
            levels (list[ValidationInLevelsItem]):
            state (None | Unset | ValidationInStateType0):
            origin (None | Unset | ValidationInOriginType0):
            touched (list[str] | Unset):
     """

    source: Source
    levels: list[ValidationInLevelsItem]
    state: None | Unset | ValidationInStateType0 = UNSET
    origin: None | Unset | ValidationInOriginType0 = UNSET
    touched: list[str] | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.source import Source # noqa: PLC0415
        source = self.source.to_dict()

        levels = []
        for levels_item_data in self.levels:
            levels_item = levels_item_data.value
            levels.append(levels_item)



        state: None | str | Unset
        if isinstance(self.state, Unset):
            state = UNSET
        elif isinstance(self.state, ValidationInStateType0):
            state = self.state.value
        else:
            state = self.state

        origin: None | str | Unset
        if isinstance(self.origin, Unset):
            origin = UNSET
        elif isinstance(self.origin, ValidationInOriginType0):
            origin = self.origin.value
        else:
            origin = self.origin

        touched: list[str] | Unset = UNSET
        if not isinstance(self.touched, Unset):
            touched = self.touched




        field_dict: dict[str, Any] = {}

        field_dict.update({
            "source": source,
            "levels": levels,
        })
        if state is not UNSET:
            field_dict["state"] = state
        if origin is not UNSET:
            field_dict["origin"] = origin
        if touched is not UNSET:
            field_dict["touched"] = touched

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source import Source # noqa: PLC0415
        d = dict(src_dict)
        source = Source.from_dict(d.pop("source"))




        levels = []
        _levels = d.pop("levels")
        for levels_item_data in (_levels):
            levels_item = ValidationInLevelsItem(levels_item_data)



            levels.append(levels_item)


        def _parse_state(data: object) -> None | Unset | ValidationInStateType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                state_type_0 = ValidationInStateType0(data)



                return state_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | ValidationInStateType0, data)

        state = _parse_state(d.pop("state", UNSET))


        def _parse_origin(data: object) -> None | Unset | ValidationInOriginType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                origin_type_0 = ValidationInOriginType0(data)



                return origin_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | ValidationInOriginType0, data)

        origin = _parse_origin(d.pop("origin", UNSET))


        touched = cast(list[str], d.pop("touched", UNSET))


        validation_in = cls(
            source=source,
            levels=levels,
            state=state,
            origin=origin,
            touched=touched,
        )

        return validation_in

