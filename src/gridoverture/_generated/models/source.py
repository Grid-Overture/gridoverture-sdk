from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="Source")



@_attrs_define
class Source:
    """ What a job of the Studio's work reads: a version, or an artifact (a session's snapshot).

        Attributes:
            version_id (None | Unset | UUID):
            artifact_id (None | Unset | UUID):
     """

    version_id: None | Unset | UUID = UNSET
    artifact_id: None | Unset | UUID = UNSET





    def to_dict(self) -> dict[str, Any]:
        version_id: None | str | Unset
        if isinstance(self.version_id, Unset):
            version_id = UNSET
        elif isinstance(self.version_id, UUID):
            version_id = str(self.version_id)
        else:
            version_id = self.version_id

        artifact_id: None | str | Unset
        if isinstance(self.artifact_id, Unset):
            artifact_id = UNSET
        elif isinstance(self.artifact_id, UUID):
            artifact_id = str(self.artifact_id)
        else:
            artifact_id = self.artifact_id


        field_dict: dict[str, Any] = {}

        field_dict.update({
        })
        if version_id is not UNSET:
            field_dict["version_id"] = version_id
        if artifact_id is not UNSET:
            field_dict["artifact_id"] = artifact_id

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        def _parse_version_id(data: object) -> None | Unset | UUID:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                version_id_type_0 = UUID(data)



                return version_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Unset | UUID, data)

        version_id = _parse_version_id(d.pop("version_id", UNSET))


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


        source = cls(
            version_id=version_id,
            artifact_id=artifact_id,
        )

        return source

