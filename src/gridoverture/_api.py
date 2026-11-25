# SPDX-License-Identifier: AGPL-3.0-or-later
"""
How the hand-written layer speaks HTTP: to the API through the generated client, turning every
error answer into an ApiError, and to storage through the signed URLs the API hands out, with a
client of its own that never carries the token.
"""

from __future__ import annotations

import hashlib
import uuid
from typing import Any

import httpx2

from ._generated.api.artifacts import get_artifact_artifacts_artifact_id_get
from ._generated.api.uploads import (
    complete_upload_uploads_upload_id_complete_post,
    request_upload_uploads_post,
)
from ._generated.client import Client as GeneratedClient
from ._generated.models import Artifact, UploadDone
from .errors import error_from


class Api:
    def __init__(self, http_client: httpx2.Client, files_client: httpx2.Client):
        self.generated = GeneratedClient(base_url=str(http_client.base_url))
        self.generated.set_httpx_client(http_client)
        self.files = files_client

    def call(self, endpoint: Any, **arguments: Any) -> Any:
        """Call a generated endpoint and return what it parsed; an ApiError for an error answer."""
        response = endpoint.sync_detailed(client=self.generated, **arguments)
        if response.status_code >= 400:
            raise error_from(response.status_code, response.content, response.headers)
        return response.parsed

    def artifact(self, artifact_id: uuid.UUID | str) -> Artifact:
        return self.call(
            get_artifact_artifacts_artifact_id_get, artifact_id=uuid.UUID(str(artifact_id))
        )

    def fetch(self, artifact_id: uuid.UUID | str) -> bytes:
        """The bytes of a stored file, downloaded from its signed URL."""
        response = self.files.get(self.artifact(artifact_id).download_url)
        if response.status_code >= 400:
            raise error_from(response.status_code, response.content, response.headers)
        return response.content

    def upload(self, data: bytes, media_type: str = "application/octet-stream") -> Artifact:
        """Upload bytes through a signed URL and return the artifact they became."""
        signed = self.call(request_upload_uploads_post)
        response = self.files.put(signed.url, content=data, headers=signed.headers.to_dict())
        if response.status_code >= 400:
            raise error_from(response.status_code, response.content, response.headers)
        done = UploadDone(sha256=hashlib.sha256(data).hexdigest(), media_type=media_type)
        return self.call(
            complete_upload_uploads_upload_id_complete_post, upload_id=signed.upload_id, body=done
        )
