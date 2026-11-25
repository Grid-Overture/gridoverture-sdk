# SPDX-License-Identifier: AGPL-3.0-or-later
"""
gridoverture, the Python SDK of the Grid Overture platform: projects, versions, edits and studies
over HTTP, with asynchronous jobs, typed settings and results as tables.

    import gridoverture as go

    client = go.Client("http://localhost:8780", token="gop_...")
    version = client.projects.get("IEEE 14").versions.latest()
    flow = version.power_flow(go.PowerFlowSettings(start="flat")).wait(timeout=120)
    buses = flow.buses.to_pandas()
"""

from .client import Client, Jobs, Project, Projects, SourceFormat, StoredFile, Version, Versions
from .contract import CONTRACT, SDK_VERSION
from .edits import AddObject, Edit, RemoveObject, SetAttribute
from .errors import (
    ApiError,
    AuthenticationError,
    ConflictError,
    DeprecatedApiWarning,
    ForbiddenError,
    GridOvertureError,
    IncompatibleContractError,
    InvalidRequestError,
    JobCancelledError,
    JobFailedError,
    JobTimeoutError,
    NotFoundError,
    ObjectNotFoundError,
    ProblemField,
    ProjectNotFoundError,
    RateLimitedError,
    ServerError,
)
from .jobs import Job
from .model import CimObject
from .results import ExportedFile, PowerFlowResult, Table, ValidationResult
from .settings import ExportFormat, ExportSettings, PowerFlowSettings, ValidationSettings

__version__ = SDK_VERSION
"""The version of this SDK."""

__all__ = [
    "CONTRACT",
    "AddObject",
    "ApiError",
    "AuthenticationError",
    "CimObject",
    "Client",
    "ConflictError",
    "DeprecatedApiWarning",
    "Edit",
    "ExportFormat",
    "ExportSettings",
    "ExportedFile",
    "ForbiddenError",
    "GridOvertureError",
    "IncompatibleContractError",
    "InvalidRequestError",
    "Job",
    "JobCancelledError",
    "JobFailedError",
    "JobTimeoutError",
    "Jobs",
    "NotFoundError",
    "ObjectNotFoundError",
    "PowerFlowResult",
    "PowerFlowSettings",
    "ProblemField",
    "Project",
    "ProjectNotFoundError",
    "RateLimitedError",
    "Projects",
    "RemoveObject",
    "ServerError",
    "SetAttribute",
    "SourceFormat",
    "StoredFile",
    "Table",
    "ValidationResult",
    "ValidationSettings",
    "Version",
    "Versions",
]
