from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.problem_field import ProblemField





T = TypeVar("T", bound="Problem")



@_attrs_define
class Problem:
    """ An error, as RFC 9457 describes it, with the id of the request that met it.

        Attributes:
            type_ (str):
            title (str):
            status (int):
            detail (str):
            instance (str):
            request_id (str):
            code (None | str | Unset): Why the caller was refused: sign_in_required, sign_in_again, not_a_member,
                needs_role, second_factor_required or identity_unavailable
            errors (list[ProblemField] | None | Unset): Each problem of a request that is not valid
     """

    type_: str
    title: str
    status: int
    detail: str
    instance: str
    request_id: str
    code: None | str | Unset = UNSET
    errors: list[ProblemField] | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        from ..models.problem_field import ProblemField # noqa: PLC0415
        type_ = self.type_

        title = self.title

        status = self.status

        detail = self.detail

        instance = self.instance

        request_id = self.request_id

        code: None | str | Unset
        if isinstance(self.code, Unset):
            code = UNSET
        else:
            code = self.code

        errors: list[dict[str, Any]] | None | Unset
        if isinstance(self.errors, Unset):
            errors = UNSET
        elif isinstance(self.errors, list):
            errors = []
            for errors_type_0_item_data in self.errors:
                errors_type_0_item = errors_type_0_item_data.to_dict()
                errors.append(errors_type_0_item)


        else:
            errors = self.errors


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "type": type_,
            "title": title,
            "status": status,
            "detail": detail,
            "instance": instance,
            "request_id": request_id,
        })
        if code is not UNSET:
            field_dict["code"] = code
        if errors is not UNSET:
            field_dict["errors"] = errors

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.problem_field import ProblemField # noqa: PLC0415
        d = dict(src_dict)
        type_ = d.pop("type")

        title = d.pop("title")

        status = d.pop("status")

        detail = d.pop("detail")

        instance = d.pop("instance")

        request_id = d.pop("request_id")

        def _parse_code(data: object) -> None | str | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            return cast(None | str | Unset, data)

        code = _parse_code(d.pop("code", UNSET))


        def _parse_errors(data: object) -> list[ProblemField] | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, list):
                    raise TypeError()
                errors_type_0 = []
                _errors_type_0 = data
                for errors_type_0_item_data in (_errors_type_0):
                    errors_type_0_item = ProblemField.from_dict(errors_type_0_item_data)



                    errors_type_0.append(errors_type_0_item)

                return errors_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(list[ProblemField] | None | Unset, data)

        errors = _parse_errors(d.pop("errors", UNSET))


        problem = cls(
            type_=type_,
            title=title,
            status=status,
            detail=detail,
            instance=instance,
            request_id=request_id,
            code=code,
            errors=errors,
        )


        problem.additional_properties = d
        return problem

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
