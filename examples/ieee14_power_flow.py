# SPDX-License-Identifier: AGPL-3.0-or-later
"""
IEEE 14 with the gridoverture SDK: import the case, run an AC power flow with reactive limits, raise
a load in a child version, run it again, compare the bus voltages, and export the edited model to
CGMES. ieee14_power_flow_powerfactory.py is the same study in PowerFactory's Python API.

Set GRIDOVERTURE_URL to the platform's address and GRIDOVERTURE_TOKEN to your personal access
token, then, from the repository's root:

    uv run python examples/ieee14_power_flow.py

It needs pandas (pip install "gridoverture[pandas]"). IEEE_14_bus.raw, next to it, is the public
IEEE 14-bus test case as PSS/E RAW.
"""

import sys
from pathlib import Path

import gridoverture as go

CASE = Path(__file__).resolve().parent / "IEEE_14_bus.raw"
LOAD = "Load 3 1"  # the load at bus 3, as the RAW case names it
EXTRA_MW = 20.0


def main():
    settings = go.PowerFlowSettings(reactive_limits=True)
    with go.Client() as client:
        project = client.projects.create("IEEE 14, SDK example")
        base = project.versions.import_file(CASE).wait(timeout=300)
        print(f"imported {CASE.name}: version {base.id}, {base.summary['buses']} buses")

        before = base.power_flow(settings).wait(timeout=300)
        if not before.converged:
            sys.exit(f"the base case ended {before.status}")

        load = base.find("EnergyConsumer", LOAD)  # a ConformLoad or a NonConformLoad too
        edit = go.SetAttribute(load.mrid, "EnergyConsumer.p", load["EnergyConsumer.p"] + EXTRA_MW)
        heavier = base.edit([edit]).wait(timeout=300)
        after = heavier.power_flow(settings).wait(timeout=300)
        if not after.converged:
            sys.exit(f"with {EXTRA_MW} MW more at {LOAD} it ended {after.status}")

        voltages = before.buses.to_pandas()[["name", "v_pu"]]
        voltages["v_pu_after"] = after.buses.to_pandas()["v_pu"]
        voltages["dv_pu"] = voltages["v_pu_after"] - voltages["v_pu"]
        print(voltages.sort_values("dv_pu").round(4).to_string())
        print(
            f"losses: {before.summary['losses_mw']:.2f} MW -> {after.summary['losses_mw']:.2f} MW"
        )

        exported = heavier.export("cgmes").wait(timeout=300)
        path = exported.download("ieee14-heavier-cgmes.zip")
        print(f"edited model written to {path}")


if __name__ == "__main__":
    main()
