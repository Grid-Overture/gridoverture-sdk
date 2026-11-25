# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The result objects built from the JSON an engine job stores: tables with snake_case columns, a
branch's ends flattened to numbered columns, findings renamed, and DataFrames indexed by id, with
pandas only when it is installed.
"""

import sys

import pytest

import gridoverture as go

FLOW = {
    "engine": "openloadflow",
    "converged": True,
    "status": "valid",
    "seconds": 0.2,
    "summary": {"generationMw": 10.0, "lossesMw": 0.5},
    "buses": {
        "n1": {"vPu": 1.02, "vKv": 112.2, "angleDeg": 0.0, "name": "Bus 1", "area": None},
        "n2": {"vPu": 0.98, "vKv": 107.8, "angleDeg": -3.1, "name": "Bus 2", "area": None},
    },
    "branches": {
        "line": {
            "name": "Line 1-2",
            "lossesMw": 0.5,
            "loadingPct": 40.0,
            "areas": [{"number": 1, "name": "Coast"}],
            "ends": [
                {"terminal": "t1", "node": "n1", "pMw": 10.0, "qMvar": 1.0, "iKa": 0.05},
                {"terminal": "t2", "node": "n2", "pMw": -9.5, "qMvar": -0.8, "iKa": 0.05},
            ],
        },
        "transformer": {
            "name": "T3",
            "lossesMw": 0.1,
            "loadingPct": None,
            "areas": [],
            "ends": [
                {"terminal": "a", "node": "n1", "pMw": 1.0, "qMvar": 0.0, "iKa": 0.01},
                {"terminal": "b", "node": "n2", "pMw": -0.5, "qMvar": 0.0, "iKa": 0.01},
                {"terminal": "c", "node": "n3", "pMw": -0.4, "qMvar": 0.0, "iKa": 0.01},
            ],
        },
    },
    "violations": [
        {
            "kind": "undervoltage",
            "mrid": "n2",
            "name": "Bus 2",
            "value": 0.98,
            "limit": 0.99,
            "unit": "pu",
            "severity": "warning",
        }
    ],
}

VALIDATION = {
    "seconds": 0.1,
    "counts": {"error": 1, "warning": 0},
    "findings": [
        {
            "level": "structure",
            "severity": "error",
            "rule": "terminal-without-node",
            "mrid": "t9",
            "cls": "Terminal",
            "message": "Terminal t9 has no node",
            "anticipated": False,
        }
    ],
}


def test_buses_are_rows_with_snake_case_columns():
    flow = go.PowerFlowResult(FLOW)
    assert len(flow.buses) == 2
    assert flow.buses.columns == ["id", "v_pu", "v_kv", "angle_deg", "name", "area"]
    assert list(flow.buses)[1] == {
        "id": "n2",
        "v_pu": 0.98,
        "v_kv": 107.8,
        "angle_deg": -3.1,
        "name": "Bus 2",
        "area": None,
    }
    assert flow.raw is FLOW


def test_a_branchs_ends_become_numbered_columns():
    rows = {row["id"]: row for row in go.PowerFlowResult(FLOW).branches}
    line, transformer = rows["line"], rows["transformer"]
    assert (line["p1_mw"], line["q2_mvar"], line["i2_ka"], line["node2"]) == (
        10.0,
        -0.8,
        0.05,
        "n2",
    )
    assert "p3_mw" not in line
    assert (transformer["node3"], transformer["p3_mw"]) == ("n3", -0.4)
    assert "ends" not in line and "areas" not in line


def test_findings_name_their_class_and_say_whether_the_model_passed():
    validation = go.ValidationResult(VALIDATION)
    assert not validation.passed
    assert validation.counts == {"error": 1, "warning": 0}
    (finding,) = validation.findings
    assert (finding["id"], finding["cim_class"], finding["rule"]) == (
        "t9",
        "Terminal",
        "terminal-without-node",
    )
    assert go.ValidationResult({"counts": {}, "findings": []}).passed


def test_a_table_becomes_a_dataframe_indexed_by_id():
    pandas = pytest.importorskip("pandas")
    flow = go.PowerFlowResult(FLOW)
    buses = flow.buses.to_pandas()
    assert list(buses.index) == ["n1", "n2"]
    assert buses.loc["n2", "v_pu"] == 0.98
    branches = flow.branches.to_pandas()
    assert pandas.isna(branches.loc["line", "p3_mw"])
    assert branches.loc["transformer", "p3_mw"] == -0.4
    empty = go.Table([]).to_pandas()
    assert empty.empty


def test_without_pandas_to_pandas_says_how_to_get_it(monkeypatch):
    monkeypatch.setitem(sys.modules, "pandas", None)
    with pytest.raises(ImportError, match=r'pip install "gridoverture\[pandas\]"'):
        go.PowerFlowResult(FLOW).buses.to_pandas()
