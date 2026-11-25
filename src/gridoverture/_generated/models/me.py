from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.me_account_kind_type_0 import MeAccountKindType0
from ..models.me_role import MeRole
from ..types import UNSET, Unset
from typing import cast
from uuid import UUID






T = TypeVar("T", bound="Me")



@_attrs_define
class Me:
    """ Whom a request acts for: the tenant, the user within it, and their role there.

        Attributes:
            tenant_id (UUID):
            tenant_name (None | str):
            user_id (UUID):
            email (None | str):
            name (None | str):
            role (MeRole): The role the request acts with: an editor at most for no work account
            account_kind (MeAccountKindType0 | None | Unset): work: an organization's account, as its provider says;
                personal: anyone's; null while no sign-in has told
     """

    tenant_id: UUID
    tenant_name: None | str
    user_id: UUID
    email: None | str
    name: None | str
    role: MeRole
    account_kind: MeAccountKindType0 | None | Unset = UNSET
    additional_properties: dict[str, Any] = _attrs_field(init=False, factory=dict)





    def to_dict(self) -> dict[str, Any]:
        tenant_id = str(self.tenant_id)

        tenant_name: None | str
        tenant_name = self.tenant_name

        user_id = str(self.user_id)

        email: None | str
        email = self.email

        name: None | str
        name = self.name

        role = self.role.value

        account_kind: None | str | Unset
        if isinstance(self.account_kind, Unset):
            account_kind = UNSET
        elif isinstance(self.account_kind, MeAccountKindType0):
            account_kind = self.account_kind.value
        else:
            account_kind = self.account_kind


        field_dict: dict[str, Any] = {}
        field_dict.update(self.additional_properties)
        field_dict.update({
            "tenant_id": tenant_id,
            "tenant_name": tenant_name,
            "user_id": user_id,
            "email": email,
            "name": name,
            "role": role,
        })
        if account_kind is not UNSET:
            field_dict["account_kind"] = account_kind

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        d = dict(src_dict)
        tenant_id = UUID(d.pop("tenant_id"))




        def _parse_tenant_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        tenant_name = _parse_tenant_name(d.pop("tenant_name"))


        user_id = UUID(d.pop("user_id"))




        def _parse_email(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        email = _parse_email(d.pop("email"))


        def _parse_name(data: object) -> None | str:
            if data is None:
                return data
            return cast(None | str, data)

        name = _parse_name(d.pop("name"))


        role = MeRole(d.pop("role"))




        def _parse_account_kind(data: object) -> MeAccountKindType0 | None | Unset:
            if data is None:
                return data
            if isinstance(data, Unset):
                return data
            try:
                if not isinstance(data, str):
                    raise TypeError()
                account_kind_type_0 = MeAccountKindType0(data)



                return account_kind_type_0
            except (TypeError, ValueError, AttributeError, KeyError):
                pass
            return cast(MeAccountKindType0 | None | Unset, data)

        account_kind = _parse_account_kind(d.pop("account_kind", UNSET))


        me = cls(
            tenant_id=tenant_id,
            tenant_name=tenant_name,
            user_id=user_id,
            email=email,
            name=name,
            role=role,
            account_kind=account_kind,
        )


        me.additional_properties = d
        return me

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
