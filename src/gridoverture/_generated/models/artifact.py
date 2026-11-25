from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from typing import cast
from uuid import UUID
import datetime






T = TypeVar("T", bound="Artifact")



@_attrs_define
class Artifact:
    """ A stored file and where to download it from; `download_url` is valid for 30 minutes.

        Attributes:
            id (UUID):
            sha256 (str):
            kind (str):
            media_type (str):
            size_bytes (int):
            created_at (datetime.datetime):
            download_url (str):
     """

    id: UUID
    sha256: str
    kind: str
    media_type: str
    size_bytes: int
    created_at: datetime.datetime
    download_url: str
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        id = str(self.id)

        sha256 = self.sha256

        kind = self.kind

        media_type = self.media_type

        size_bytes = self.size_bytes

        created_at = self.created_at.isoformat()

        download_url = self.download_url


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "sha256": sha256,
            "kind": kind,
            "media_type": media_type,
            "size_bytes": size_bytes,
            "created_at": created_at,
            "download_url": download_url,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        sha256 = d.pop("sha256")

        kind = d.pop("kind")

        media_type = d.pop("media_type")

        size_bytes = d.pop("size_bytes")

        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))




        download_url = d.pop("download_url")

        artifact = cls(
            id=id,
            sha256=sha256,
            kind=kind,
            media_type=media_type,
            size_bytes=size_bytes,
            created_at=created_at,
            download_url=download_url,
        )


        artifact.additional_properties = d
        return artifact

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
