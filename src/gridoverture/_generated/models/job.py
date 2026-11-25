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
  from ..models.job_params import JobParams
  from ..models.job_progress_type_0 import JobProgressType0
  from ..models.job_result_type_0 import JobResultType0





T = TypeVar("T", bound="Job")



@_attrs_define
class Job:
    """ Work the engine does outside the request. `result` says what it made once it is done.

        Attributes:
            id (UUID):
            kind (str):
            status (str):
            params (JobParams):
            result (JobResultType0 | None):
            error (None | str):
            attempts (int):
            progress (JobProgressType0 | None): The stage it is at: waiting, starting, reading, running or storing
            cancel_requested_at (datetime.datetime | None):
            created_at (datetime.datetime):
            started_at (datetime.datetime | None):
            finished_at (datetime.datetime | None):
     """

    id: UUID
    kind: str
    status: str
    params: JobParams
    result: JobResultType0 | None
    error: None | str
    attempts: int
    progress: JobProgressType0 | None
    cancel_requested_at: datetime.datetime | None
    created_at: datetime.datetime
    started_at: datetime.datetime | None
    finished_at: datetime.datetime | None
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.job_params import JobParams # noqa: PLC0415
        from ..models.job_progress_type_0 import JobProgressType0 # noqa: PLC0415
        from ..models.job_result_type_0 import JobResultType0 # noqa: PLC0415
        id = str(self.id)

        kind = self.kind

        status = self.status

        params = self.params.to_dict()

        result: dict[str, Any] | None
        if isinstance(self.result, JobResultType0):
            result = self.result.to_dict()
        else:
            result = self.result

        error: None | str
        error = self.error

        attempts = self.attempts

        progress: dict[str, Any] | None
        if isinstance(self.progress, JobProgressType0):
            progress = self.progress.to_dict()
        else:
            progress = self.progress

        cancel_requested_at: None | str
        if isinstance(self.cancel_requested_at, datetime.datetime):
            cancel_requested_at = self.cancel_requested_at.isoformat()
        else:
            cancel_requested_at = self.cancel_requested_at

        created_at = self.created_at.isoformat()

        started_at: None | str
        if isinstance(self.started_at, datetime.datetime):
            started_at = self.started_at.isoformat()
        else:
            started_at = self.started_at

        finished_at: None | str
        if isinstance(self.finished_at, datetime.datetime):
            finished_at = self.finished_at.isoformat()
        else:
            finished_at = self.finished_at


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "id": id,
            "kind": kind,
            "status": status,
            "params": params,
            "result": result,
            "error": error,
            "attempts": attempts,
            "progress": progress,
            "cancel_requested_at": cancel_requested_at,
            "created_at": created_at,
            "started_at": started_at,
            "finished_at": finished_at,
        })

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.job_params import JobParams # noqa: PLC0415
        from ..models.job_progress_type_0 import JobProgressType0 # noqa: PLC0415
        from ..models.job_result_type_0 import JobResultType0 # noqa: PLC0415
        d = dict(src_dict)
        id = UUID(d.pop("id"))




        kind = d.pop("kind")

        status = d.pop("status")

        params = JobParams.from_dict(d.pop("params"))




        def _parse_result(data: object) -> JobResultType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                result_type_0 = JobResultType0.from_dict(data)



                return result_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(JobResultType0 | None, data)

        result = _parse_result(d.pop("result"))


        def _parse_error(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        error = _parse_error(d.pop("error"))


        attempts = d.pop("attempts")

        def _parse_progress(data: object) -> JobProgressType0 | None:
            if data is None:
                return data
            try:
                if not isinstance(data, dict):
                    raise TypeError()
                progress_type_0 = JobProgressType0.from_dict(data)



                return progress_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(JobProgressType0 | None, data)

        progress = _parse_progress(d.pop("progress"))


        def _parse_cancel_requested_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                cancel_requested_at_type_0 = datetime.datetime.fromisoformat(data)



                return cancel_requested_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        cancel_requested_at = _parse_cancel_requested_at(d.pop("cancel_requested_at"))


        created_at = datetime.datetime.fromisoformat(d.pop("created_at"))




        def _parse_started_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                started_at_type_0 = datetime.datetime.fromisoformat(data)



                return started_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        started_at = _parse_started_at(d.pop("started_at"))


        def _parse_finished_at(data: object) -> datetime.datetime | None:
            if data is None:
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                finished_at_type_0 = datetime.datetime.fromisoformat(data)



                return finished_at_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(datetime.datetime | None, data)

        finished_at = _parse_finished_at(d.pop("finished_at"))


        job = cls(
            id=id,
            kind=kind,
            status=status,
            params=params,
            result=result,
            error=error,
            attempts=attempts,
            progress=progress,
            cancel_requested_at=cancel_requested_at,
            created_at=created_at,
            started_at=started_at,
            finished_at=finished_at,
        )


        job.additional_properties = d
        return job

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
