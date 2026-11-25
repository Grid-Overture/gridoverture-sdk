from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.export_in_format import ExportInFormat
from ..models.export_in_packaging_type_0 import ExportInPackagingType0
from ..models.export_in_version import ExportInVersion
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.source import Source





T = TypeVar("T", bound="ExportIn")



@_attrs_define
class ExportIn:
    """ An export of the model to a file, with its report.

        Attributes:
            source (Source): What a job of the Studio's work reads: a version, or an artifact (a session's snapshot).
            format_ (ExportInFormat):
            version (ExportInVersion | Unset):  Default: ExportInVersion.VALUE_33.
            packaging (ExportInPackagingType0 | None | Unset):
     """

    source: Source
    format_: ExportInFormat
    version: ExportInVersion | Unset = ExportInVersion.VALUE_33
    packaging: ExportInPackagingType0 | None | Unset = UNSET





    def to_dict(self) -> dict[str, Any]:
        from ..models.source import Source # noqa: PLC0415
        source = self.source.to_dict()

        format_ = self.format_.value

        version: int | Unset = UNSET
        if not isinstance(self.version, Unset):
            version = self.version.value


        packaging: None | str | Unset
        if isinstance(self.packaging, Unset):
            packaging = UNSET
        elif isinstance(self.packaging, ExportInPackagingType0):
            packaging = self.packaging.value
        else:
            packaging = self.packaging


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "source": source,
            "format": format_,
        })
        if version is not UNSET:
            field_dict["version"] = version
        if packaging is not UNSET:
            field_dict["packaging"] = packaging

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source import Source # noqa: PLC0415
        d = dict(src_dict)
        source = Source.from_dict(d.pop("source"))




        format_ = ExportInFormat(d.pop("format"))




        _version = d.pop("version", UNSET)
        version: ExportInVersion | Unset
        if isinstance(_version,  Unset):
            version = UNSET
        else:
            version = ExportInVersion(_version)




        def _parse_packaging(data: object) -> ExportInPackagingType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                packaging_type_0 = ExportInPackagingType0(data)



                return packaging_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(ExportInPackagingType0 | None | Unset, data)

        packaging = _parse_packaging(d.pop("packaging", UNSET))


        export_in = cls(
            source=source,
            format_=format_,
            version=version,
            packaging=packaging,
        )

        return export_in

