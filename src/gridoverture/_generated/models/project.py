from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from uuid import UUID
import datetime

if TYPE_CHECKING:
  from ..models.version import Version





T = TypeVar("T", bound="Project")



@_attrs_define
class Project:
    """ One network model and its versions, what the Studio calls a saved model. A user sees their own
    and the ones the tenant's other users share.

        Attributes:
            id (UUID):
            name (str):
            created_at (datetime.datetime):
            mine (bool): Whether the user made it; only then may they change it
            shared (bool): Whether the tenant's other users see it
            version_count (int):
            latest_version (None | Version):
     """

    id: UUID
    name: str
    created_at: datetime.datetime
    mine: bool
    shared: bool
    version_count: int
    latest_version: None | Version
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.version import Version # noqa: PLC0415
        id = str(self.id)

        name = self.name

        created_at = self.created_at.isoformat()

        mine = self.mine

        shared = self.shared

        version_count = self.version_count

        latest_version: dict[str, Any] | None
        if isinstance(self.latest_version, Version):
            latest_version = self.latest_version.to_dict()
        else:
            latest_version = self.latest_version


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "name": name,
            "created_at": created_at,
            "mine": mine,
            "shared": shared,
            "version_count": version_count,
            "latest_version": latest_version,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.version import Version # noqa: PLC0415
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        name = d.pop("name")

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))




        mine = d.pop("mine")

        shared = d.pop("shared")

        version_count = d.pop("version_count")

        def _parse_latest_version(data: object) -> None | Version:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                latest_version_type_0 = Version.from_dict(data)



                return latest_version_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | Version, data)

        latest_version = _parse_latest_version(d.pop("latest_version"))


        project = cls(
            id=id,
            name=name,
            created_at=created_at,
            mine=mine,
            shared=shared,
            version_count=version_count,
            latest_version=latest_version,
        )


        project.additional_properties = d
        return project

    @property
    def additional_keys(self) -> list[str]:
        return list(self.additional_properties.keys())

    def __getitem__(self, key: str) -> Any:
        return self.additional_properties[key]

    def __setitem__(self, key: str, value: Any) -> None:
        self.additional_properties[key] = value

    def __delitem__(self, key: str) -> None:
        del self.additional_properties[key]

    def __contains__(self, key: str) -> bool:
        return key in self.additional_properties
