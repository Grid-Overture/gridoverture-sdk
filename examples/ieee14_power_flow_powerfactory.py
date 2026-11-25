# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The study of ieee14_power_flow.py in PowerFactory's own Python API, for comparison: it runs only
inside a PowerFactory installation, with its license, on the user's machine, and never on the
platform. It assumes a project "IEEE 14" with the case already imported and a study case active.

What changes with the SDK: the project is named, not active; the edit makes a child version instead
of changing the project in place; the load flow is a job, and its result a table. It stops before
the export: CGMES in PowerFactory is a paid add-on with an export of its own, and the SDK's
export needs neither.
"""

import sys

import powerfactory

LOAD = "Load 3 1"
EXTRA_MW = 20.0


def voltages(app):
    """Each terminal's name and voltage in pu, after a load flow."""
    return {
        terminal.loc_name: terminal.GetAttribute("m:u")
        for terminal in app.GetCalcRelevantObjects("*.ElmTerm")
    }


def main():
    app = powerfactory.GetApplication()
    if app.ActivateProject("IEEE 14") != 0:
        sys.exit("no project IEEE 14")

    load_flow = app.GetFromStudyCase("ComLdf")
    load_flow.iopt_net = 0  # AC, balanced
    load_flow.iopt_lim = 1  # reactive limits of the generators
    if load_flow.Execute() != 0:
        sys.exit("the base case did not converge")
    before = voltages(app)

    (load,) = app.GetCalcRelevantObjects(f"{LOAD}.ElmLod")
    load.plini += EXTRA_MW  # changes the active project in place
    if load_flow.Execute() != 0:
        sys.exit(f"with {EXTRA_MW} MW more at {LOAD} it did not converge")
    after = voltages(app)

    for name in sorted(before, key=lambda terminal: after[terminal] - before[terminal]):
        change = after[name] - before[name]
        print(f"{name:12} {before[name]:.4f} {after[name]:.4f} {change:+.4f}")


if __name__ == "__main__":
    main()
