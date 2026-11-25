from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset






T = TypeVar("T", bound="UploadDone")



@_attrs_define
class UploadDone:
    """ 
        Attributes:
            sha256 (str): SHA-256 of the uploaded bytes
            media_type (str | Unset):  Default: 'application/octet-stream'.
     """

    sha256: str
    media_type: str | Unset = 'application/octet-stream'





    def to_dict(self) -> dict[str, Any]:
        sha256 = self.sha256

        media_type = self.media_type


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "sha256": sha256,
        })
        if media_type is not UNSET:
            field_dict["media_type"] = media_type

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        sha256 = d.pop("sha256")

        media_type = d.pop("media_type", UNSET)

        upload_done = cls(
            sha256=sha256,
            media_type=media_type,
        )

        return upload_done

