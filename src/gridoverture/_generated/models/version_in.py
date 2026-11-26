from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.version_in_format_type_0 import VersionInFormatType0
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID

if TYPE_CHECKING:
  from ..models.add_object import AddObject
  from ..models.remove_object import RemoveObject
  from ..models.set_attribute import SetAttribute





T = TypeVar("T", bound="VersionIn")



@_attrs_define
class VersionIn:
    """ A version from an uploaded file in a format the converter reads (`artifact_id` and `format`),
    or from a version of the same project and CIM edits to it (`parent_id` and `edits`). A CGMES
    model or a pf2xml export is uploaded as a zip of its files. `time_zone` is the requester's, an
    IANA name ("America/Santiago"), which the conversion report is dated in; UTC when it is not
    given or not known.

        Attributes:
            artifact_id (None | Unset | UUID):
            format_ (None | Unset | VersionInFormatType0):
            parent_id (None | Unset | UUID):
            edits (list[AddObject | RemoveObject | SetAttribute] | None | Unset):
            time_zone (None | str | Unset):
     """

    artifact_id: None | Unset | UUID = UNSET
    format_: None | Unset | VersionInFormatType0 = UNSET
    parent_id: None | Unset | UUID = UNSET
    edits: list[AddObject | RemoveObject | SetAttribute] | None | Unset = UNSET
    time_zone: None | str | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.add_object import AddObject # noqa: PLC0415
        from ..models.remove_object import RemoveObject # noqa: PLC0415
        from ..models.set_attribute import SetAttribute # noqa: PLC0415
        artifact_id: None | str | Unset
        if isinstance(self.artifact_id, Unset):
            artifact_id = UNSET
        elif isinstance(self.artifact_id, UUID):
            artifact_id = str(self.artifact_id)
        else:
            artifact_id = self.artifact_id

        format_: None | str | Unset
        if isinstance(self.format_, Unset):
            format_ = UNSET
        elif isinstance(self.format_, VersionInFormatType0):
            format_ = self.format_.value
        else:
            format_ = self.format_

        parent_id: None | str | Unset
        if isinstance(self.parent_id, Unset):
            parent_id = UNSET
        elif isinstance(self.parent_id, UUID):
            parent_id = str(self.parent_id)
        else:
            parent_id = self.parent_id

        edits: list[dict[str, Any]] | None | Unset
        if isinstance(self.edits, Unset):
            edits = UNSET
        elif isinstance(self.edits, list):
            edits = []
            for edits_type_0_item_data in self.edits:
                edits_type_0_item: dict[str, Any]
                if isinstance(edits_type_0_item_data, SetAttribute):
                    edits_type_0_item = edits_type_0_item_data.to_dict()
                elif isinstance(edits_type_0_item_data, AddObject):
                    edits_type_0_item = edits_type_0_item_data.to_dict()
                else:
                    edits_type_0_item = edits_type_0_item_data.to_dict()

                edits.append(edits_type_0_item)


        else:
            edits = self.edits

        time_zone: None | str | Unset
        if isinstance(self.time_zone, Unset):
            time_zone = UNSET
        else:
            time_zone = self.time_zone


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if artifact_id is not UNSET:
            field_dict["artifact_id"] = artifact_id
        if format_ is not UNSET:
            field_dict["format"] = format_
        if parent_id is not UNSET:
            field_dict["parent_id"] = parent_id
        if edits is not UNSET:
            field_dict["edits"] = edits
        if time_zone is not UNSET:
            field_dict["time_zone"] = time_zone

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.add_object import AddObject # noqa: PLC0415
        from ..models.remove_object import RemoveObject # noqa: PLC0415
        from ..models.set_attribute import SetAttribute # noqa: PLC0415
        d = dict(src_dict)
        def _parse_artifact_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                artifact_id_type_0 = UUID(data)



                return artifact_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        artifact_id = _parse_artifact_id(d.pop("artifact_id", UNSET))


        def _parse_format_(data: object) -> None | Unset | VersionInFormatType0:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                format_type_0 = VersionInFormatType0(data)



                return format_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | VersionInFormatType0, data)

        format_ = _parse_format_(d.pop("format", UNSET))


        def _parse_parent_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                parent_id_type_0 = UUID(data)



                return parent_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        parent_id = _parse_parent_id(d.pop("parent_id", UNSET))


        def _parse_edits(data: object) -> list[AddObject | RemoveObject | SetAttribute] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                edits_type_0 = []
                _edits_type_0 = data
                for edits_type_0_item_data in (_edits_type_0):
                    def _parse_edits_type_0_item(data: object) -> AddObject | RemoveObject | SetAttribute:
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            edits_type_0_item_type_0 = SetAttribute.from_dict(data)



                            return edits_type_0_item_type_0
                        except (TypeError, ValueError, AttributeError, KeyError):
                            pass
                        try:
                            if not isinstance(data, dict):
                                raise TypeError()
                            edits_type_0_item_type_1 = AddObject.from_dict(data)



                            return edits_type_0_item_type_1
                        except (TypeError, ValueError, AttributeError, KeyError):
                            pass
                        if not isinstance(data, dict):
                            raise TypeError()
                        edits_type_0_item_type_2 = RemoveObject.from_dict(data)



                        return edits_type_0_item_type_2

                    edits_type_0_item = _parse_edits_type_0_item(edits_type_0_item_data)

                    edits_type_0.append(edits_type_0_item)

                return edits_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[AddObject | RemoveObject | SetAttribute] | None | Unset, data)

        edits = _parse_edits(d.pop("edits", UNSET))


        def _parse_time_zone(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        time_zone = _parse_time_zone(d.pop("time_zone", UNSET))


        version_in = cls(
            artifact_id=artifact_id,
            format_=format_,
            parent_id=parent_id,
            edits=edits,
            time_zone=time_zone,
        )

        return version_in

