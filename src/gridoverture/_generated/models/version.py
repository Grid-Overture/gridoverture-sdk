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
  from ..models.stored_file import StoredFile
  from ..models.version_previews import VersionPreviews
  from ..models.version_summary import VersionSummary





T = TypeVar("T", bound="Version")



@_attrs_define
class Version:
    """ One version of a project, a CGMES 3.0 model in a zip. Its file's kind says who made it:
    `cgmes`, a job, with the profiles alone; `studio-project`, the Studio, a .gostudio that also
    holds the Studio's layout and session files. `job_id` is the job that made it, null for a
    Studio save, and that job has its conversion's result and report.

        Attributes:
            id (UUID):
            project_id (UUID):
            parent_id (None | UUID):
            job_id (None | UUID):
            summary (VersionSummary): What a list shows of it, its bus count for one
            file (StoredFile): A stored file, known by its hash.
            previews (VersionPreviews): The artifact of a picture of its diagram, by theme
            created_at (datetime.datetime):
     """

    id: UUID
    project_id: UUID
    parent_id: None | UUID
    job_id: None | UUID
    summary: VersionSummary
    file: StoredFile
    previews: VersionPreviews
    created_at: datetime.datetime
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.stored_file import StoredFile # noqa: PLC0415
        from ..models.version_previews import VersionPreviews # noqa: PLC0415
        from ..models.version_summary import VersionSummary # noqa: PLC0415
        id = str(self.id)

        project_id = str(self.project_id)

        parent_id: None | str
        if isinstance(self.parent_id, UUID):
            parent_id = str(self.parent_id)
        else:
            parent_id = self.parent_id

        job_id: None | str
        if isinstance(self.job_id, UUID):
            job_id = str(self.job_id)
        else:
            job_id = self.job_id

        summary = self.summary.to_dict()

        file = self.file.to_dict()

        previews = self.previews.to_dict()

        created_at = self.created_at.isoformat()


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "project_id": project_id,
            "parent_id": parent_id,
            "job_id": job_id,
            "summary": summary,
            "file": file,
            "previews": previews,
            "created_at": created_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.stored_file import StoredFile # noqa: PLC0415
        from ..models.version_previews import VersionPreviews # noqa: PLC0415
        from ..models.version_summary import VersionSummary # noqa: PLC0415
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        project_id = UUID(d.pop("project_id"))




        def _parse_parent_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                parent_id_type_0 = UUID(data)



                return parent_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        parent_id = _parse_parent_id(d.pop("parent_id"))


        def _parse_job_id(data: object) -> None | UUID:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                job_id_type_0 = UUID(data)



                return job_id_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(None | UUID, data)

        job_id = _parse_job_id(d.pop("job_id"))


        summary = VersionSummary.from_dict(d.pop("summary"))




        file = StoredFile.from_dict(d.pop("file"))




        previews = VersionPreviews.from_dict(d.pop("previews"))




        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))




        version = cls(
            id=id,
            project_id=project_id,
            parent_id=parent_id,
            job_id=job_id,
            summary=summary,
            file=file,
            previews=previews,
            created_at=created_at,
        )


        version.additional_properties = d
        return version

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
