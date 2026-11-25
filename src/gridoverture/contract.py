# SPDX-License-Identifier: AGPL-3.0-or-later
"""
The platform's API contract, checked on every answer of the API: its Gridoverture-Contract header
names the contract the platform speaks, as one or more semver versions. Another major than the one
the SDK was generated from is an IncompatibleContractError, raised before the answer is read; any
minor of the same major works, since a minor only adds. A Deprecation (RFC 9745) or Sunset
(RFC 8594) header becomes a DeprecatedApiWarning, once per client for each distinct notice.
Storage's answers, through the signed URLs, are not the platform's and are not checked.
"""

from __future__ import annotations

import re
import warnings
from datetime import UTC, datetime
from email.utils import parsedate_to_datetime
from importlib.metadata import PackageNotFoundError, version

import httpx2

from ._generated.contract import CONTRACT
from .errors import DeprecatedApiWarning, IncompatibleContractError

SEMVER = re.compile(r"^(\d+)\.(\d+)\.(\d+)(?:[-+].*)?$")

try:
    SDK_VERSION = version("gridoverture")
except PackageNotFoundError:  # a checkout on the path, not installed
    SDK_VERSION = "unknown"


def major_of(contract: str) -> int | None:
    """The major version of a contract, or None when it is not semver."""
    match = SEMVER.match(contract.strip())
    return int(match.group(1)) if match else None


def notice_date(value: str | None) -> str | None:
    """A Deprecation or Sunset date as YYYY-MM-DD: RFC 9745's @seconds or an HTTP-date."""
    if not value:
        return None
    value = value.strip()
    if re.fullmatch(r"@-?\d+", value):
        return datetime.fromtimestamp(int(value[1:]), UTC).date().isoformat()
    try:
        return parsedate_to_datetime(value).date().isoformat()
    except (TypeError, ValueError):
        return None


class ContractCheck:
    """A response hook of the API's HTTP client: the contract check and the deprecation notices."""

    def __init__(self) -> None:
        self.noticed: set[tuple[str | None, str | None, str | None]] = set()

    def __call__(self, response: httpx2.Response) -> None:
        self.check_contract(response.headers.get("gridoverture-contract"))
        self.notice_deprecation(response)

    @staticmethod
    def check_contract(header: str | None) -> None:
        if not header:
            return  # a platform from before the contract
        ours = major_of(CONTRACT)
        offered = [contract.strip() for contract in header.split(",")]
        majors = [major_of(contract) for contract in offered]
        if None in majors or ours in majors:
            return  # a header that is not semver is not the platform's to fail on
        raise IncompatibleContractError(offered[-1], CONTRACT, SDK_VERSION)

    def notice_deprecation(self, response: httpx2.Response) -> None:
        deprecation = response.headers.get("deprecation")
        sunset = response.headers.get("sunset")
        if not deprecation and not sunset:
            return
        links = response.links
        link = (links.get("deprecation") or links.get("sunset") or {}).get("url")
        notice = (deprecation, sunset, link)
        if notice in self.noticed:
            return
        self.noticed.add(notice)
        route = f"{response.request.method} {response.request.url.path}"
        parts = [f"the platform deprecates {route}"]
        if deprecation and (since := notice_date(deprecation)):
            parts.append(f"as of {since},")
        if sunset and (until := notice_date(sunset)):
            parts.append(f"and it stops answering on {until}")
        message = " ".join(parts)
        if link:
            message += f"; see {link}"
        warnings.warn(message, DeprecatedApiWarning, stacklevel=2)
