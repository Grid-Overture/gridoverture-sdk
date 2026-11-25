# SPDX-License-Identifier: AGPL-3.0-or-later
"""
What keeps the SDK honest with the API: its generated client is what openapi.public.json makes
today, so it calls the public routes only, and it names no engine except in the power flow's
optional `engine`, as the API's contract does: a study has a kind, not an engine.
"""

import ast
import dataclasses
import filecmp
import pathlib

import generate

import gridoverture as go

ROOT = pathlib.Path(__file__).resolve().parents[1]
SDK = ROOT / "src" / "gridoverture"
GENERATED = SDK / "_generated"
OPEN_ENGINES = ("openloadflow", "veragrid", "pandapower")
FORBIDDEN = ("dynawo", "powerfactory", "emtp", *OPEN_ENGINES)
# the lines that may name an open engine: the power flow's engine, and the formats of files that
# two of them read, as the API's schemas.py allows
ALLOWED = {
    ("settings.py", 'Engine = Literal["openloadflow", "veragrid", "pandapower"]'),
    ("settings.py", 'ExportFormat = Literal["raw", "matpower", "veragrid", "pandapower", "cgmes"]'),
    (
        "client.py",
        'SourceFormat = Literal["raw", "matpower", "veragrid", "pandapower", "cgmes", "pf2xml", '
        '"cdf"]',
    ),
    ("client.py", '".veragrid": "veragrid",'),
    ("client.py", '".json": "pandapower",'),
}


def differences(comparison, where=""):
    found = [f"{where}{name}" for name in comparison.left_only + comparison.right_only]
    found += [f"{where}{name}" for name in comparison.diff_files + comparison.funny_files]
    for name, sub in comparison.subdirs.items():
        found += differences(sub, f"{where}{name}/")
    return found


def test_the_generated_client_is_what_the_public_openapi_makes(tmp_path):
    generate.generate(tmp_path / "fresh")
    ignored = ["__pycache__"]
    stale = differences(filecmp.dircmp(GENERATED, tmp_path / "fresh", ignore=ignored))
    assert not stale, f"gridoverture._generated is stale, run 'make generate': {stale}"


def code_lines(source):
    """The lines of a module that are code: not its docstrings, comments or blank lines."""
    prose = set()
    for node in ast.walk(ast.parse(source)):
        docstring = isinstance(node, ast.Expr) and isinstance(node.value, ast.Constant)
        if docstring and isinstance(node.value.value, str):
            prose.update(range(node.lineno, (node.end_lineno or node.lineno) + 1))
    return [
        (number, line.strip())
        for number, line in enumerate(source.splitlines(), 1)
        if number not in prose and line.strip() and not line.strip().startswith("#")
    ]


def test_the_sdk_names_no_engine_but_the_power_flows():
    offenses = []
    for path in sorted(SDK.glob("*.py")):
        for number, line in code_lines(path.read_text(encoding="utf-8")):
            named = [engine for engine in FORBIDDEN if engine in line.lower()]
            if named and (path.name, line) not in ALLOWED:
                offenses.append(f"{path.name}:{number}: {line}")
    assert not offenses, "the SDK names an engine outside the power flow:\n" + "\n".join(offenses)


def test_only_the_power_flow_settings_take_an_engine():
    settings = [go.PowerFlowSettings, go.ValidationSettings, go.ExportSettings]
    with_engine = [
        cls.__name__
        for cls in settings
        if any("engine" in field.name for field in dataclasses.fields(cls))
    ]
    assert with_engine == ["PowerFlowSettings"]


def test_every_public_object_has_a_docstring():
    missing = []
    for name in go.__all__:
        public = getattr(go, name)
        if not isinstance(public, type):
            continue  # a type alias, as SourceFormat, has no __doc__ of its own
        if not (getattr(public, "__doc__", None) or "").strip():
            missing.append(name)
        for member_name, member in vars(public).items():
            if (
                member_name.startswith("_")
                or not callable(member)
                and not isinstance(member, property)
            ):
                continue
            if not (member.__doc__ or "").strip():
                missing.append(f"{name}.{member_name}")
    assert not missing, f"public objects without a docstring: {missing}"
