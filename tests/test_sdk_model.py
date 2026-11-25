# SPDX-License-Identifier: AGPL-3.0-or-later
"""
A version's model read client-side: objects by class and name, a class taking in its CGMES 3.0
subclasses unless exact, their attributes merged from every profile and typed, references as
mRIDs, and the model downloaded once per Version.
"""

import io
import zipfile

import httpx2
import pytest
from sdk_fakes import STORAGE, artifact_body, ok, project_body, version_body

import gridoverture as go
from gridoverture.model import is_a

HEAD = (
    '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"'
    ' xmlns:cim="http://iec.ch/TC57/CIM100#"'
    ' xmlns:md="http://iec.ch/TC57/61970-552/ModelDescription/1#">'
    '<md:FullModel rdf:about="urn:uuid:header"><md:Model.created>2026</md:Model.created>'
    "</md:FullModel>"
)
EQ = HEAD + (
    '<cim:NonConformLoad rdf:ID="_load-3">'
    "<cim:IdentifiedObject.name>Load 3 1</cim:IdentifiedObject.name>"
    '<cim:EnergyConsumer.LoadResponse rdf:resource="#_response"/>'
    "</cim:NonConformLoad>"
    '<cim:EnergyConsumer rdf:ID="_load-4">'
    "<cim:IdentifiedObject.name>Load 4 1</cim:IdentifiedObject.name>"
    "</cim:EnergyConsumer>"
    '<cim:ACLineSegment rdf:ID="_line-1">'
    "<cim:IdentifiedObject.name>1</cim:IdentifiedObject.name>"
    "<cim:ACLineSegment.r>0.0194</cim:ACLineSegment.r>"
    "</cim:ACLineSegment>"
    '<cim:ACLineSegment rdf:ID="_line-2">'
    "<cim:IdentifiedObject.name>1</cim:IdentifiedObject.name>"
    "</cim:ACLineSegment>"
    '<cim:PowerTransformerEnd rdf:ID="_end-1">'
    '<cim:PowerTransformerEnd.connectionKind rdf:resource="http://iec.ch/TC57/CIM100#WindingConnection.D"/>'
    "</cim:PowerTransformerEnd>"
    "</rdf:RDF>"
)
SSH = HEAD + (
    '<cim:NonConformLoad rdf:about="#_load-3">'
    "<cim:Equipment.inService>true</cim:Equipment.inService>"
    "<cim:EnergyConsumer.p>94.2</cim:EnergyConsumer.p>"
    "</cim:NonConformLoad>"
    "</rdf:RDF>"
)


@pytest.fixture
def version(client, api):
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as bundle:
        bundle.writestr("model_EQ.xml", EQ)
        bundle.writestr("model_SSH.xml", SSH)
    body = version_body(project_body()["id"])
    url = f"{STORAGE}/download/model"
    api.on("GET", f"/versions/{body['id']}", ok(body))
    api.on("GET", f"/artifacts/{body['file']['id']}", ok(artifact_body(body["file"]["id"], url)))
    api.on("GET", "/download/model", httpx2.Response(200, content=buffer.getvalue()))
    return client.get_version(body["id"])


def test_an_object_is_found_by_class_and_name_with_its_profiles_merged(version):
    load = version.find("NonConformLoad", "Load 3 1")
    assert (load.mrid, load.cim_class, load.name) == ("load-3", "NonConformLoad", "Load 3 1")
    assert load["EnergyConsumer.p"] == 94.2
    assert load.get("Equipment.inService") is True
    assert load["EnergyConsumer.LoadResponse"] == "response"
    assert load.get("EnergyConsumer.q") is None


def test_a_class_takes_in_its_subclasses_unless_exact(version):
    assert version.find("EnergyConsumer", "Load 3 1").cim_class == "NonConformLoad"
    assert [load.mrid for load in version.objects("EnergyConsumer")] == ["load-3", "load-4"]
    assert [load.mrid for load in version.objects("EnergyConsumer", exact=True)] == ["load-4"]
    assert [item.mrid for item in version.objects("Conductor")] == ["line-1", "line-2"]
    with pytest.raises(go.ObjectNotFoundError):
        version.find("EnergyConsumer", "Load 3 1", exact=True)


@pytest.mark.parametrize(
    ("cim_class", "ancestor"),
    [
        ("NonConformLoad", "EnergyConsumer"),
        ("ConformLoad", "EnergyConsumer"),
        ("ACLineSegment", "Conductor"),
        ("Breaker", "Switch"),
        ("WindGeneratingUnit", "GeneratingUnit"),
        ("SynchronousMachine", "RotatingMachine"),
        ("PowerTransformer", "ConductingEquipment"),
        ("LinearShuntCompensator", "ShuntCompensator"),
        ("EnergyConsumer", "EnergyConsumer"),
    ],
)
def test_the_hierarchy_is_cgmes_3s(cim_class, ancestor):
    assert is_a(cim_class, ancestor)


def test_a_class_is_not_its_siblings_or_its_subclasses():
    assert not is_a("EnergyConsumer", "NonConformLoad")
    assert not is_a("ACLineSegment", "Switch")
    assert not is_a("NoSuchClass", "IdentifiedObject")


def test_objects_are_listed_by_class_or_classes_in_file_order(version, api):
    loads = version.objects(["ConformLoad", "NonConformLoad"])
    assert [load.mrid for load in loads] == ["load-3"]
    assert [obj.mrid for obj in version.objects("ACLineSegment", name="1")] == ["line-1", "line-2"]
    assert len(version.objects()) == 5
    assert version.objects("Breaker") == []
    assert len(api.sent("GET", "/download/model")) == 1


def test_names_and_enumerations_stay_text(version):
    line = version.objects("ACLineSegment")[0]
    assert (line.name, line["ACLineSegment.r"]) == ("1", 0.0194)
    end = version.objects("PowerTransformerEnd")[0]
    assert end["PowerTransformerEnd.connectionKind"] == "WindingConnection.D"


def test_find_refuses_none_and_several(version):
    with pytest.raises(go.ObjectNotFoundError) as missing:
        version.find("EnergyConsumer", "Load 99 1")
    assert isinstance(missing.value, LookupError)
    assert str(missing.value) == "no EnergyConsumer named 'Load 99 1'"
    with pytest.raises(ValueError, match="2 objects are named '1': line-1, line-2"):
        version.find("ACLineSegment", "1")
