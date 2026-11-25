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
  from ..models.upload_headers import UploadHeaders





T = TypeVar("T", bound="Upload")



@_attrs_define
class Upload:
    """ Where to upload one file: a PUT of it to `url`, with `headers`, before `expires_at`.

        Attributes:
            upload_id (UUID):
            url (str):
            headers (UploadHeaders):
            expires_at (datetime.datetime):
     """

    upload_id: UUID
    url: str
    headers: UploadHeaders
    expires_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.upload_headers import UploadHeaders # noqa: PLC0415
        upload_id = str(self.upload_id)

        url = self.url

        headers = self.headers.to_dict()

        expires_at = self.expires_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "upload_id": upload_id,
            "url": url,
            "headers": headers,
            "expires_at": expires_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.upload_headers import UploadHeaders # noqa: PLC0415
        d = dict(src_dict)
        upload_id = UUID(d.pop("upload_id"))




        url = d.pop("url")

        headers = UploadHeaders.from_dict(d.pop("headers"))




        expires_at = datetime.datetime.fromisoformat(d.pop("expires_at"))




        upload = cls(
            upload_id=upload_id,
            url=url,
            headers=headers,
            expires_at=expires_at,
        )


        upload.additional_properties = d
        return upload

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
