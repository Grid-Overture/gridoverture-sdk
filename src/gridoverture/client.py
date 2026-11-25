# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The Client and what it finds: projects, their versions, and the jobs that import, edit and study
them. Everything here speaks to the API through the generated client in gridoverture._generated.
"""

from __future__ import annotations

import io
import json
import os
import uuid
import zipfile
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Literal, get_args

import httpx2

from ._api import Api
from ._generated.api.jobs import get_job_jobs_job_id_get, list_jobs_jobs_get
from ._generated.api.projects import (
    create_project_projects_post,
    get_project_projects_project_id_get,
    list_projects_projects_get,
)
from ._generated.api.versions import (
    create_version_projects_project_id_versions_post,
    get_version_versions_version_id_get,
    list_versions_projects_project_id_versions_get,
)
from ._generated.api.work import (
    export_exports_post,
    power_flow_power_flows_post,
    validation_validations_post,
)
from ._generated.models import ExportIn, PowerFlowIn, ProjectIn, ValidationIn, VersionIn
from ._generated.models import Job as JobBody
from ._generated.models import Project as ProjectBody
from ._generated.models import Version as VersionBody
from .edits import Edit
from .errors import ObjectNotFoundError, ProjectNotFoundError
from .jobs import Job
from .model import CimObject, is_a, objects_of
from .results import ExportedFile, PowerFlowResult, ValidationResult
from .settings import ExportFormat, ExportSettings, PowerFlowSettings, ValidationSettings

SourceFormat = Literal["raw", "matpower", "veragrid", "pandapower", "cgmes", "pf2xml", "cdf"]
"""The formats a model file may be imported from. CGMES and pf2xml come as a zip or a folder."""
DEFAULT_URL = "http://localhost:8780"  # where a local platform serves its public gateway
# a suffix -> the format it tells; a zip or a folder may hold CGMES or pf2xml, so it tells none
SUFFIXES = {
    ".raw": "raw",
    ".m": "matpower",
    ".veragrid": "veragrid",
    ".json": "pandapower",
    ".cdf": "cdf",
}


def format_of(path: Path, given: str | None) -> str:
    """The format of a model file: `given`, or the one its suffix tells; ValueError for neither."""
    formats = get_args(SourceFormat)
    if given is not None:
        if given not in formats:
            raise ValueError(f"{given!r} is not a format: one of {', '.join(formats)}")
        return given
    if path.is_dir() or path.suffix.lower() == ".zip":
        raise ValueError(f"{path.name} may hold CGMES or pf2xml: give its format")
    told = SUFFIXES.get(path.suffix.lower())
    if told is None:
        raise ValueError(f"{path.name} does not tell its format: give one of {', '.join(formats)}")
    return told


def zipped(folder: Path) -> bytes:
    """A folder's files in a zip, by their paths within it, in a stable order."""
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as bundle:
        for path in sorted(p for p in folder.rglob("*") if p.is_file()):
            bundle.write(path, path.relative_to(folder).as_posix())
    return buffer.getvalue()


def as_uuid(value: str | uuid.UUID) -> uuid.UUID:
    return value if isinstance(value, uuid.UUID) else uuid.UUID(str(value))


@dataclass(frozen=True)
class StoredFile:
    """A stored file, known by its hash: a version's model, for one."""

    id: uuid.UUID
    sha256: str
    kind: str
    """Who made it: "cgmes" for a job's CGMES zip, "studio-project" for a Studio save."""
    media_type: str
    size_bytes: int


class Version:
    """
    One version of a project: a CGMES 3.0 model, which never changes. An edit makes a child
    version; a study reads it and makes a result.
    """

    def __init__(self, api: Api, body: VersionBody):
        self._api = api
        self._body = body
        self._objects: list[CimObject] | None = None

    @property
    def id(self) -> uuid.UUID:
        """The version's id."""
        return self._body.id

    @property
    def project_id(self) -> uuid.UUID:
        """The project it belongs to."""
        return self._body.project_id

    @property
    def parent_id(self) -> uuid.UUID | None:
        """The version it was edited from; None for an import."""
        return self._body.parent_id

    @property
    def job_id(self) -> uuid.UUID | None:
        """The job that made it; None for a save of the Studio."""
        return self._body.job_id

    @property
    def created_at(self) -> datetime:
        """When it was made."""
        return self._body.created_at

    @property
    def summary(self) -> dict[str, Any]:
        """What a list shows of it, its bus count for one."""
        return self._body.summary.to_dict()

    @property
    def file(self) -> StoredFile:
        """Its file: a CGMES zip, or the .gostudio of a Studio save."""
        stored = self._body.file
        return StoredFile(
            stored.id, stored.sha256, stored.kind, stored.media_type, stored.size_bytes
        )

    def objects(
        self,
        cim_class: str | Sequence[str] | None = None,
        *,
        name: str | None = None,
        exact: bool = False,
    ) -> list[CimObject]:
        """
        The objects of the version's model, of a class or several, and of a name when given, in
        the order its files list them. The model is downloaded and read once per Version.

        A class takes in its CGMES 3.0 subclasses: "EnergyConsumer" finds ConformLoad and
        NonConformLoad too, "Switch" a Breaker, "GeneratingUnit" a WindGeneratingUnit.

        Args:
            cim_class: A CIM class, as "ACLineSegment", or several; None for every class.
            name: The IdentifiedObject.name to match; None for any.
            exact: Match the class itself only, not its subclasses.
        """
        if self._objects is None:
            self._objects = objects_of(self._api.fetch(self.file.id))
        classes = (cim_class,) if isinstance(cim_class, str) else cim_class

        def of_class(found):
            if classes is None:
                return True
            if exact:
                return found.cim_class in classes
            return any(is_a(found.cim_class, cls) for cls in classes)

        return [
            found
            for found in self._objects
            if of_class(found) and (name is None or found.name == name)
        ]

    def find(self, cim_class: str | Sequence[str], name: str, *, exact: bool = False) -> CimObject:
        """
        The one object of the version's model of that class (or one of those), its subclasses
        included unless `exact`, and of that name.

        Raises:
            ObjectNotFoundError: None has them.
            ValueError: Several have them; `objects` lists them all.
        """
        found = self.objects(cim_class, name=name, exact=exact)
        classes = (cim_class,) if isinstance(cim_class, str) else tuple(cim_class)
        if not found:
            raise ObjectNotFoundError(classes, name)
        if len(found) > 1:
            mrids = ", ".join(item.mrid for item in found)
            raise ValueError(f"{len(found)} objects are named {name!r}: {mrids}")
        return found[0]

    def _source(self) -> dict[str, str]:
        return {"version_id": str(self.id)}

    def edit(self, edits: Sequence[Edit]) -> Job[Version]:
        """
        Queue the edits as a new version, a child of this one, which does not change.

        Args:
            edits: SetAttribute, AddObject and RemoveObject, at least one, applied in order.
        """
        if not edits:
            raise ValueError("an edit needs at least one edit")
        body = {"parent_id": str(self.id), "edits": [edit._body() for edit in edits]}
        return self._queue_version(body)

    def _queue_version(self, body: dict[str, Any]) -> Job[Version]:
        queued = self._api.call(
            create_version_projects_project_id_versions_post,
            project_id=self.project_id,
            body=VersionIn.from_dict(body),
        )
        return Job(self._api, queued, built_version)

    def power_flow(self, settings: PowerFlowSettings | None = None) -> Job[PowerFlowResult]:
        """Queue a power flow of this version, with `settings` or the default ones."""
        body = {"source": self._source(), **(settings or PowerFlowSettings())._body()}
        queued = self._api.call(power_flow_power_flows_post, body=PowerFlowIn.from_dict(body))
        return Job(self._api, queued, built_power_flow)

    def validate(self, settings: ValidationSettings | None = None) -> Job[ValidationResult]:
        """Queue a validation of this version, at every level unless `settings` says which."""
        body = {"source": self._source(), **(settings or ValidationSettings())._body()}
        queued = self._api.call(validation_validations_post, body=ValidationIn.from_dict(body))
        return Job(self._api, queued, built_validation)

    def export(self, settings: ExportSettings | ExportFormat) -> Job[ExportedFile]:
        """
        Queue an export of this version to a file.

        Args:
            settings: An ExportSettings, or only its format: "raw", "matpower", "veragrid",
                "pandapower" or "cgmes".
        """
        if isinstance(settings, str):
            settings = ExportSettings(settings)
        body = {"source": self._source(), **settings._body()}
        queued = self._api.call(export_exports_post, body=ExportIn.from_dict(body))
        return Job(self._api, queued, built_export)

    def download(self, path: str | os.PathLike[str]) -> Path:
        """Write the version's file, its CGMES zip, to `path` and return it."""
        target = Path(path)
        target.write_bytes(self._api.fetch(self.file.id))
        return target

    def __eq__(self, other: object) -> bool:
        return isinstance(other, Version) and other.id == self.id

    def __hash__(self) -> int:
        return hash(self.id)

    def __repr__(self) -> str:
        return f"<Version {self.id} of project {self.project_id}>"


class Versions:
    """A project's versions: listed, the latest, and new ones imported from a file."""

    def __init__(self, api: Api, project_id: uuid.UUID):
        self._api = api
        self._project_id = project_id

    def list(self) -> list[Version]:
        """The project's versions, the newest first."""
        found = self._api.call(
            list_versions_projects_project_id_versions_get, project_id=self._project_id
        )
        return [Version(self._api, body) for body in found]

    def latest(self) -> Version | None:
        """The newest version; None for a project that has none yet."""
        found = self.list()
        return found[0] if found else None

    def import_file(
        self, path: str | os.PathLike[str], format: SourceFormat | None = None
    ) -> Job[Version]:
        """
        Upload a model file and queue its import as a new version, a CGMES 3.0 model.

        Args:
            path: The file. A folder, such as a CGMES model's profiles, is zipped first.
            format: "raw", "matpower", "veragrid", "pandapower", "cgmes", "pf2xml" or "cdf".
                Without it, the suffix tells: .raw, .m, .veragrid, .json (pandapower) and .cdf.
                A .zip or a folder needs it.
        """
        source = Path(path)
        told = format_of(source, format)
        if source.is_dir():
            artifact = self._api.upload(zipped(source), "application/zip")
        else:
            artifact = self._api.upload(source.read_bytes())
        queued = self._api.call(
            create_version_projects_project_id_versions_post,
            project_id=self._project_id,
            body=VersionIn.from_dict({"artifact_id": str(artifact.id), "format": told}),
        )
        return Job(self._api, queued, built_version)


class Project:
    """One network model and its versions, what the Studio calls a saved model."""

    def __init__(self, api: Api, body: ProjectBody):
        self._api = api
        self._body = body
        self.versions = Versions(api, body.id)
        """Its versions."""

    @property
    def id(self) -> uuid.UUID:
        """The project's id."""
        return self._body.id

    @property
    def name(self) -> str:
        """Its name, which need not be unique."""
        return self._body.name

    @property
    def created_at(self) -> datetime:
        """When it was made."""
        return self._body.created_at

    @property
    def mine(self) -> bool:
        """Whether the user made it; only then may they add versions to it."""
        return self._body.mine

    @property
    def shared(self) -> bool:
        """Whether the tenant's other users see it."""
        return self._body.shared

    @property
    def version_count(self) -> int:
        """How many versions it had when it was read."""
        return self._body.version_count

    def __repr__(self) -> str:
        return f"<Project {self.name!r} {self.id}>"


class Projects:
    """The projects the user sees: their own, and the ones the tenant's other users share."""

    def __init__(self, api: Api):
        self._api = api

    def list(self) -> list[Project]:
        """Every project the user sees, the latest saved first."""
        return [Project(self._api, body) for body in self._api.call(list_projects_projects_get)]

    def get(self, name: str) -> Project:
        """
        The project of that name. Names are not unique: of several, the latest saved.

        Raises:
            ProjectNotFoundError: No project the user sees has that name.
        """
        for project in self.list():
            if project.name == name:
                return project
        raise ProjectNotFoundError(name)

    def get_by_id(self, project_id: str | uuid.UUID) -> Project:
        """The project of that id; NotFoundError when the user does not see it."""
        body = self._api.call(get_project_projects_project_id_get, project_id=as_uuid(project_id))
        return Project(self._api, body)

    def create(self, name: str) -> Project:
        """Make a project, with no version yet."""
        body = self._api.call(create_project_projects_post, body=ProjectIn(name=name))
        return Project(self._api, body)


class Jobs:
    """The user's jobs, to pick up one that another script queued."""

    def __init__(self, api: Api):
        self._api = api

    def get(self, job_id: str | uuid.UUID) -> Job[Any]:
        """The job of that id; what `wait` returns follows its kind."""
        return self._job(self._api.call(get_job_jobs_job_id_get, job_id=as_uuid(job_id)))

    def list(self) -> list[Job[Any]]:
        """The jobs the user queued, the newest first, at most 50."""
        return [self._job(body) for body in self._api.call(list_jobs_jobs_get)]

    def _job(self, body: JobBody) -> Job[Any]:
        return Job(self._api, body, builder_of(body.kind))


def result_json(api: Api, job: JobBody, output: str = "result") -> dict[str, Any]:
    """One of the JSON outputs a job of the Studio's work stored."""
    outputs = job.result.to_dict()["outputs"]
    return json.loads(api.fetch(outputs[output]))


def built_version(api: Api, job: JobBody) -> Version:
    version_id = as_uuid(job.result.to_dict()["version_id"])
    return Version(api, api.call(get_version_versions_version_id_get, version_id=version_id))


def built_power_flow(api: Api, job: JobBody) -> PowerFlowResult:
    return PowerFlowResult(result_json(api, job))


def built_validation(api: Api, job: JobBody) -> ValidationResult:
    return ValidationResult(result_json(api, job))


def built_export(api: Api, job: JobBody) -> ExportedFile:
    report = result_json(api, job)
    file_id = as_uuid(job.result.to_dict()["outputs"]["file"])
    form = job.params.to_dict().get("format") or report.get("format", "")
    return ExportedFile(form, file_id, report, api.fetch)


def built_result(api: Api, job: JobBody) -> dict[str, Any] | None:
    return None if job.result is None else job.result.to_dict()


BUILDERS: dict[str, Callable[[Api, JobBody], Any]] = {
    "import": built_version,
    "edit": built_version,
    "power_flow": built_power_flow,
    "validation": built_validation,
    "export": built_export,
}


def builder_of(kind: str) -> Callable[[Api, JobBody], Any]:
    """What a job of `kind` makes: for a kind the SDK has no class for, its result as a dict."""
    return BUILDERS.get(kind, built_result)


class Client:
    """
    The way into the platform, over HTTP.

    Args:
        base_url: The platform's address: its public gateway, or an API reached directly.
            Without it, GRIDOVERTURE_URL, and without that, http://localhost:8780, where a
            local platform serves its gateway.
        token: Sent as `Authorization: Bearer <token>`, a personal access token through the
            gateway. Without it, GRIDOVERTURE_TOKEN. Without either no header is sent, which
            only an API in local mode accepts.
        timeout: Seconds for each HTTP request; a job's wait has its own.
        http_client: The httpx2.Client to speak to the API with, for tests or a proxy. Its own
            base URL is used, and the token is added to its headers.
        files_client: The httpx2.Client for the signed URLs of uploads and downloads. It never
            carries the token, since those URLs go to storage, not to the API.
    """

    def __init__(
        self,
        base_url: str | None = None,
        token: str | None = None,
        *,
        timeout: float = 30.0,
        http_client: httpx2.Client | None = None,
        files_client: httpx2.Client | None = None,
    ):
        token = token or os.environ.get("GRIDOVERTURE_TOKEN") or None
        self._owned: list[httpx2.Client] = []
        if http_client is None:
            address = (base_url or os.environ.get("GRIDOVERTURE_URL") or DEFAULT_URL).rstrip("/")
            http_client = httpx2.Client(base_url=address, timeout=timeout)
            self._owned.append(http_client)
        if token:
            http_client.headers["Authorization"] = f"Bearer {token}"
        if files_client is None:
            files_client = httpx2.Client(timeout=timeout, follow_redirects=True)
            self._owned.append(files_client)
        self._base_url = str(http_client.base_url).rstrip("/")
        self._api = Api(http_client, files_client)
        self.projects = Projects(self._api)
        """The projects the user sees."""
        self.jobs = Jobs(self._api)
        """The jobs the user queued."""

    @property
    def base_url(self) -> str:
        """The address of the API it speaks to."""
        return self._base_url

    def get_version(self, version_id: str | uuid.UUID) -> Version:
        """The version of that id; NotFoundError when the user does not see it."""
        body = self._api.call(get_version_versions_version_id_get, version_id=as_uuid(version_id))
        return Version(self._api, body)

    def close(self) -> None:
        """Close the HTTP clients it made itself; the ones it was given are left open."""
        for owned in self._owned:
            owned.close()

    def __enter__(self) -> Client:
        return self

    def __exit__(self, *exception: object) -> None:
        self.close()

    def __repr__(self) -> str:
        return f"<Client {self.base_url}>"
