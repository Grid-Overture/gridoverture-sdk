# SPDX-License-Identifier: AGPL-3.0-or-later
"""Takes a newer openapi.public.json from the platform: vendors it into spec/, records the platform
version it came from in spec/PLATFORM_REF, regenerates gridoverture._generated, and prints the
routes added and removed, as Markdown, for the pull request that carries the change.

Usage: sync_openapi.py <platform_ref> <openapi.public.json>

<platform_ref> is the platform's tag, or the commit when the spec is not released yet; the file is
services/api/openapi.public.json at that ref. The sync-openapi workflow fetches it; by hand, copy it
from a checkout of the platform. The hand-written layer is not touched: a route that changed shape
shows up as a failing test or a type the SDK no longer matches, and is fixed in the same pull
request.
"""

import json
import pathlib
import sys

from generate import OPENAPI, OUT, SPEC, generate

PLATFORM_REF = SPEC / "PLATFORM_REF"
METHODS = ("get", "put", "post", "delete", "patch")


def routes(spec: dict) -> set[str]:
    """Each route of an OpenAPI document, as "POST /power-flows"."""
    return {
        f"{method.upper()} {path}"
        for path, operations in spec.get("paths", {}).items()
        for method in operations
        if method in METHODS
    }


def changes(old: dict, new: dict) -> str:
    """The routes added and removed, as a Markdown list."""
    added = sorted(routes(new) - routes(old))
    removed = sorted(routes(old) - routes(new))
    lines = [f"- added `{route}`" for route in added]
    lines += [f"- removed `{route}`" for route in removed]
    if not lines:
        lines = ["- no route added or removed; schemas may still have changed"]
    return "\n".join(lines)


def sync(platform_ref: str, source: pathlib.Path) -> str:
    """Vendor `source` as the spec of `platform_ref` and regenerate. The routes that changed."""
    new = json.loads(source.read_text(encoding="utf-8"))
    if "paths" not in new or "openapi" not in new:
        raise ValueError(f"{source} is not an OpenAPI document")
    old = json.loads(OPENAPI.read_text(encoding="utf-8"))
    OPENAPI.write_text(source.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
    PLATFORM_REF.write_text(platform_ref.strip() + "\n", encoding="utf-8", newline="\n")
    generate(OUT)
    return changes(old, new)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit(__doc__)
    print(sync(sys.argv[1], pathlib.Path(sys.argv[2])))
