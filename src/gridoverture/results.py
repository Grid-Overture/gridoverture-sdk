# SPDX-License-Identifier: AGPL-3.0-or-later
"""
What a finished study gives back, built from the JSON its engine job stores. Each result keeps that
JSON whole as `raw`, and shows its parts as Tables: one row per bus, branch, violation or finding,
with snake_case columns and an `id`, which a DataFrame takes as its index.

A row holds a record's scalar fields. What is nested in it (a branch's ends) is flattened into
numbered columns; any other list or object stays only in `raw`.
"""

from __future__ import annotations

import re
import uuid
from collections.abc import Callable, Iterator, Mapping
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas

SCALARS = (str, int, float, bool, type(None))
BRANCH_END = {"node": "node{n}", "pMw": "p{n}_mw", "qMvar": "q{n}_mvar", "iKa": "i{n}_ka"}


def snake(name: str) -> str:
    """A camelCase name in snake_case: vPu is v_pu, voltageLevel is voltage_level."""
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def scalars(record: Mapping[str, Any], renamed: Mapping[str, str] | None = None) -> dict[str, Any]:
    """The scalar fields of a record, with snake_case names unless `renamed` names them."""
    renamed = renamed or {}
    return {
        renamed.get(key, snake(key)): value
        for key, value in record.items()
        if isinstance(value, SCALARS)
    }


class Table:
    """
    Rows of a result, each a dict with the same snake_case columns. Iterate over it for the rows,
    or turn it into a pandas DataFrame with `to_pandas`.
    """

    def __init__(self, rows: list[dict[str, Any]]):
        self.rows = rows
        """One dict per row."""

    @property
    def columns(self) -> list[str]:
        """Every column any row has, in the order they first appear."""
        return list(dict.fromkeys(key for row in self.rows for key in row))

    def __len__(self) -> int:
        return len(self.rows)

    def __iter__(self) -> Iterator[dict[str, Any]]:
        return iter(self.rows)

    def __repr__(self) -> str:
        return f"<Table of {len(self.rows)} rows: {', '.join(self.columns)}>"

    def to_pandas(self) -> pandas.DataFrame:
        """
        The rows as a pandas DataFrame indexed by `id`. A column a row does not have is NaN there.
        It needs pandas: `pip install "gridoverture[pandas]"`.
        """
        try:
            import pandas
        except ImportError as missing:
            raise ImportError(
                'Table.to_pandas needs pandas: pip install "gridoverture[pandas]"'
            ) from missing
        frame = pandas.DataFrame(self.rows, columns=self.columns)
        return frame.set_index("id") if "id" in frame.columns else frame


def branch_row(key: str, branch: Mapping[str, Any]) -> dict[str, Any]:
    row = {"id": key, **scalars(branch)}
    for n, end in enumerate(branch.get("ends") or (), start=1):
        for field, column in BRANCH_END.items():
            row[column.format(n=n)] = end.get(field)
    return row


class PowerFlowResult:
    """
    The result of a power flow: whether it converged, the network's totals, and a row per bus,
    branch and violation.
    """

    def __init__(self, raw: dict[str, Any]):
        self.raw = raw
        """The whole result, as the engine gave it."""

    @property
    def converged(self) -> bool:
        """Whether the power flow converged."""
        return bool(self.raw.get("converged"))

    @property
    def status(self) -> str:
        """ "valid", "unbalanced" (it converged and a bus keeps a mismatch) or "notConverged"."""
        return self.raw.get("status", "")

    @property
    def engine(self) -> str:
        """The open engine it ran on."""
        return self.raw.get("engine", "")

    @property
    def seconds(self) -> float:
        """How long the engine took."""
        return float(self.raw.get("seconds", 0.0))

    @property
    def iterations(self) -> int | None:
        """The Newton-Raphson iterations the engine reports; None when it does not say."""
        return self.raw.get("iterations")

    @property
    def summary(self) -> dict[str, Any]:
        """Generation, load and losses of the whole network, in MW and Mvar."""
        return scalars(self.raw.get("summary") or {})

    @property
    def buses(self) -> Table:
        """
        A row per node: id, name, v_pu, v_kv, angle_deg, nominal_kv, island, bus, voltage_level,
        substation, area.
        """
        buses = self.raw.get("buses") or {}
        return Table([{"id": key, **scalars(bus)} for key, bus in buses.items()])

    @property
    def branches(self) -> Table:
        """
        A row per line, cable, transformer or switch, by its mRID: name, circuit, losses_mw,
        losses_mvar, loading_pct, limit_ka, limit_mva, and node{n}, p{n}_mw, q{n}_mvar and i{n}_ka
        per end n (1, 2, and 3 for a three-winding transformer).
        """
        branches = self.raw.get("branches") or {}
        return Table([branch_row(key, branch) for key, branch in branches.items()])

    @property
    def violations(self) -> Table:
        """A row per limit broken: id (the mRID), kind, name, value, limit, unit, severity."""
        rows = [scalars(item, {"mrid": "id"}) for item in self.raw.get("violations") or ()]
        return Table(rows)

    def __repr__(self) -> str:
        return f"<PowerFlowResult {self.status} on {self.engine}, {len(self.buses)} buses>"


class ValidationResult:
    """The findings of a validation, and their count by severity."""

    def __init__(self, raw: dict[str, Any]):
        self.raw = raw
        """The whole result, as the engine gave it."""

    @property
    def counts(self) -> dict[str, int]:
        """How many findings of each severity."""
        return dict(self.raw.get("counts") or {})

    @property
    def findings(self) -> Table:
        """
        A row per finding: id (the mRID, when it has one), level, severity, rule, cim_class,
        message, anticipated (the import declared it, so its severity is info).
        """
        renamed = {"mrid": "id", "cls": "cim_class"}
        return Table([scalars(item, renamed) for item in self.raw.get("findings") or ()])

    @property
    def passed(self) -> bool:
        """Whether no finding has severity "error"."""
        return not any(item.get("severity") == "error" for item in self.raw.get("findings") or ())

    def __repr__(self) -> str:
        return f"<ValidationResult {'passed' if self.passed else 'failed'} {self.counts}>"


class ExportedFile:
    """The file an export wrote, its report, and how to download it."""

    def __init__(
        self,
        format: str,
        artifact_id: uuid.UUID,
        report: dict[str, Any],
        fetch: Callable[[uuid.UUID], bytes],
    ):
        self.format = format
        """The format it was written in."""
        self.artifact_id = artifact_id
        """The stored file's id."""
        self.report = report
        """What the export kept, changed and lost, as the engine gave it."""
        self._fetch = fetch

    def content(self) -> bytes:
        """The file's bytes."""
        return self._fetch(self.artifact_id)

    def download(self, path: str | Path) -> Path:
        """Write the file to `path` and return it."""
        target = Path(path)
        target.write_bytes(self.content())
        return target

    def __repr__(self) -> str:
        return f"<ExportedFile {self.format} {self.artifact_id}>"
