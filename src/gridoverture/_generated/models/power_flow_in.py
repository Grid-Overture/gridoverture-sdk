from __future__ import annotations

from collections.abc import Mapping
from typing import Any, TypeVar, BinaryIO, TextIO, TYPE_CHECKING, Generator

from attrs import define as _attrs_define
from attrs import field as _attrs_field

from ..types import UNSET, Unset

from ..models.power_flow_in_engine import PowerFlowInEngine
from ..models.power_flow_in_start import PowerFlowInStart
from ..types import UNSET, Unset
from typing import cast

if TYPE_CHECKING:
  from ..models.source import Source





T = TypeVar("T", bound="PowerFlowIn")



@_attrs_define
class PowerFlowIn:
    """ A load flow, the Studio's LoadFlowResult. `engine` is optional and an open one.

        Attributes:
            source (Source): What a job of the Studio's work reads: a version, or an artifact (a session's snapshot).
            engine (PowerFlowInEngine | Unset):  Default: PowerFlowInEngine.OPENLOADFLOW.
            start (PowerFlowInStart | Unset):  Default: PowerFlowInStart.DC.
            reactive_limits (bool | Unset):  Default: True.
            controls (bool | Unset):  Default: False.
            edited (bool | Unset): Whether the session's model was edited Default: False.
     """

    source: Source
    engine: PowerFlowInEngine | Unset = PowerFlowInEngine.OPENLOADFLOW
    start: PowerFlowInStart | Unset = PowerFlowInStart.DC
    reactive_limits: bool | Unset = True
    controls: bool | Unset = False
    edited: bool | Unset = False





    def to_dict(self) -> dict[str, Any]:
        from ..models.source import Source # noqa: PLC0415
        source = self.source.to_dict()

        engine: str | Unset = UNSET
        if not isinstance(self.engine, Unset):
            engine = self.engine.value


        start: str | Unset = UNSET
        if not isinstance(self.start, Unset):
            start = self.start.value


        reactive_limits = self.reactive_limits

        controls = self.controls

        edited = self.edited


        field_dict: dict[str, Any] = {}

        field_dict.update({
            "source": source,
        })
        if engine is not UNSET:
            field_dict["engine"] = engine
        if start is not UNSET:
            field_dict["start"] = start
        if reactive_limits is not UNSET:
            field_dict["reactive_limits"] = reactive_limits
        if controls is not UNSET:
            field_dict["controls"] = controls
        if edited is not UNSET:
            field_dict["edited"] = edited

        return field_dict



    @classmethod
    def from_dict(cls: type[T], src_dict: Mapping[str, Any]) -> T:
        from ..models.source import Source # noqa: PLC0415
        d = dict(src_dict)
        source = Source.from_dict(d.pop("source"))




        _engine = d.pop("engine", UNSET)
        engine: PowerFlowInEngine | Unset
        if isinstance(_engine,  Unset):
            engine = UNSET
        else:
            engine = PowerFlowInEngine(_engine)




        _start = d.pop("start", UNSET)
        start: PowerFlowInStart | Unset
        if isinstance(_start,  Unset):
            start = UNSET
        else:
            start = PowerFlowInStart(_start)




        reactive_limits = d.pop("reactive_limits", UNSET)

        controls = d.pop("controls", UNSET)

        edited = d.pop("edited", UNSET)

        power_flow_in = cls(
            source=source,
            engine=engine,
            start=start,
            reactive_limits=reactive_limits,
            controls=controls,
            edited=edited,
        )

        return power_flow_in

