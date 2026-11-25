# The SDK's reference

Every public class and function of `gridoverture`, with what it takes, returns and raises. The
[README](../README.md) is the place to start; this is where to look things up. Every public object
also has a docstring, so `help(go.Version)` says the same.

## Install

| | |
|---|---|
| Distribution | `gridoverture` |
| Import | `import gridoverture` |
| Python | 3.11 or later |
| Dependencies | `httpx2`, `attrs` |
| Extra | `gridoverture[pandas]` adds pandas, which `Table.to_pandas()` needs |

## Layers

- `gridoverture._generated` holds a low-level client generated with openapi-python-client, on
  httpx2 (the successor of httpx that the generator uses), from `spec/openapi.public.json`: the
  platform's public routes only, the ones its gateway lets through. Next to it, the CGMES 3.0 class
  hierarchy, generated from `spec/cgmes-3.0-class-parents.json`, which comes from ENTSO-E's RDFS.
  It is private, never edited by hand, and regenerated with `make generate`. A test fails when it
  is stale against either file.
- Everything else, documented below, is written by hand on top of it, and is the public API.
  Every public object has a docstring.

## Client

```python
Client(
    base_url: str | None = None,
    token: str | None = None,
    *,
    timeout: float = 30.0,
    http_client: httpx2.Client | None = None,
    files_client: httpx2.Client | None = None,
)
```

- `base_url`: the platform's address, its public gateway. Without it, `GRIDOVERTURE_URL`, and
  without that, `http://localhost:8780`, where a platform running on your own machine serves it.
- `token`: sent as `Authorization: Bearer <token>`. Without it, `GRIDOVERTURE_TOKEN`. The gateway
  takes a personal access token only, one that starts with `gop_`. Without either, no header is
  sent, which only a platform's API in local mode, reached directly, accepts.
- `timeout`: seconds for each HTTP request, not for a job (see `Job.wait`).
- `http_client`: the `httpx2.Client` to speak to the API with, for tests or proxies. The token, when
  there is one, is added to its headers; its own base URL is used.
- `files_client`: the `httpx2.Client` for the signed URLs of uploads and downloads. It never carries
  the token, since those URLs go to storage, not to the API.

`Client` is a context manager; `close()` closes the HTTP clients it made itself.

| Member | Returns |
|---|---|
| `client.projects` | `Projects` |
| `client.jobs` | `Jobs` |
| `client.get_version(version_id: str \| uuid.UUID)` | `Version`, by its id |

## Projects and versions

```python
class Projects:
    def list(self) -> list[Project]            # the API's order: the latest saved first
    def get(self, name: str) -> Project        # by name; ProjectNotFoundError when none has it
    def get_by_id(self, project_id: str | uuid.UUID) -> Project
    def create(self, name: str) -> Project
```

Names are not unique. When several projects the user sees share a name, `get` returns the first in
the API's order, the latest saved.

```python
class Project:
    id: uuid.UUID
    name: str
    created_at: datetime
    mine: bool                 # whether the user made it; only then may they change it
    shared: bool               # whether the tenant's other users see it
    version_count: int
    versions: Versions

class Versions:
    def list(self) -> list[Version]            # newest first
    def latest(self) -> Version | None         # None for a project with no version yet
    def import_file(self, path: str | os.PathLike, format: SourceFormat | None = None) -> Job[Version]
```

`import_file` uploads the file through a signed URL (the upload flow stays inside the SDK) and
queues the import that makes a new version, a CGMES 3.0 model. `SourceFormat` is one of `raw`,
`matpower`, `veragrid`, `pandapower`, `cgmes`, `pf2xml`, `cdf`. Without `format` it is told from
the suffix: `.raw` raw, `.m` matpower, `.veragrid` veragrid, `.json` pandapower, `.cdf` cdf. A
`.zip` or a folder needs `format`, since a CGMES model and a pf2xml export are both one; a folder
is zipped before it is uploaded. Any other suffix without `format` is a `ValueError`.

```python
class Version:
    id: uuid.UUID
    project_id: uuid.UUID
    parent_id: uuid.UUID | None      # the version it was edited from
    job_id: uuid.UUID | None         # the job that made it; None for a Studio save
    created_at: datetime
    summary: dict[str, Any]          # what a list shows of it, its bus count for one
    file: StoredFile                 # its CGMES zip (or .gostudio for a Studio save)

    def edit(self, edits: Sequence[Edit]) -> Job[Version]
    def power_flow(self, settings: PowerFlowSettings | None = None) -> Job[PowerFlowResult]
    def validate(self, settings: ValidationSettings | None = None) -> Job[ValidationResult]
    def export(self, settings: ExportSettings | ExportFormat) -> Job[ExportedFile]
    def download(self, path: str | os.PathLike) -> pathlib.Path   # its file, written to path
    def objects(self, cim_class: str | Sequence[str] | None = None, *, name: str | None = None, exact: bool = False) -> list[CimObject]
    def find(self, cim_class: str | Sequence[str], name: str, *, exact: bool = False) -> CimObject

class StoredFile:
    id: uuid.UUID
    sha256: str
    kind: str
    media_type: str
    size_bytes: int
```

## The model's objects

`objects` and `find` read the version's CGMES model on the client, with the standard library, as
PowerFactory's `GetCalcRelevantObjects` finds objects: the API has no list of a model's elements,
so the SDK downloads the version's file once per `Version` object and reads every profile. mRIDs
differ from one project to another (they derive from the project), so a script finds what to edit
by class and name rather than by a fixed mRID.

```python
class CimObject:
    mrid: str
    cim_class: str                   # the concrete class, as "NonConformLoad"
    name: str | None                 # its IdentifiedObject.name
    values: Mapping[str, Any]        # its attributes by CIM name, from every profile
    def __getitem__(self, attribute: str) -> Any
    def get(self, attribute: str, default: Any = None) -> Any
```

- `objects(cim_class, name=...)` lists the objects of one class or several, of that name when
  given, in the order the files list them; with no class, every object.
- `find(cim_class, name)` returns the one object of that class (or classes) and name.
  `ObjectNotFoundError` when none has them, `ValueError` naming their mRIDs when several do.
- A class takes in its subclasses, as CGMES 3.0 declares them: `"EnergyConsumer"` finds a
  `ConformLoad` and a `NonConformLoad` too, `"Switch"` a `Breaker`, `"GeneratingUnit"` a
  `WindGeneratingUnit`. `exact=True` matches the class itself only. The hierarchy is generated
  into `gridoverture._generated` from ENTSO-E's CGMES 3.0 vocabularies (`make generate`). A
  version is always CGMES 3.0, so CGMES 2.4.15's hierarchy is not needed.
- A value is a `bool` or a `float` when CGMES writes it as one, a reference is the mRID it points
  at, an enumeration is its name (`WindingConnection.D`), and the rest, names among them, is text.

## Edits

An edit names an object by its mRID and an attribute by its CIM name, the class that declares it
and its own name, as in `EnergyConsumer.p`. The API checks their shape and the engine checks each
against ENTSO-E's CGMES 3.0 schema; a wrong one comes back as an error, never silently ignored.

```python
SetAttribute(mrid: str, attribute: str, value: bool | int | float | str | list | None)
AddObject(cim_class: str, mrid: str, values: Mapping[str, Value] | None = None)
RemoveObject(mrid: str, dependents: bool = False)
Edit = SetAttribute | AddObject | RemoveObject
```

`value=None` removes an attribute's value; a reference takes the mRID it points at.
`dependents=True` also removes what exists only for the object: its terminals, their flows and
limits, a transformer's ends. `edit` needs at least one edit (`ValueError` otherwise) and makes a
child version; the version it is called on does not change.

## Settings

Typed settings objects, as PowerFactory's ComLdf is for its load flow. They are frozen dataclasses,
and a value outside the allowed ones is a `ValueError` when the object is built, before any
request.

```python
PowerFlowSettings(
    engine: Literal["openloadflow", "veragrid", "pandapower"] | None = None,  # None: the API's default
    start: Literal["dc", "flat", "solution"] = "dc",
    reactive_limits: bool = True,    # hold machines within their reactive limits
    controls: bool = False,          # let tap changers and switched shunts regulate
)
ValidationSettings(
    levels: Sequence[Literal["structure", "consistency", "physics"]] = ("structure", "consistency", "physics"),
)
ExportSettings(
    format: Literal["raw", "matpower", "veragrid", "pandapower", "cgmes"],
    raw_version: Literal[33, 35] = 33,           # the PSS/E RAW version, for format="raw"
    packaging: Literal["zip", "folder"] | None = None,   # for format="cgmes"
)
```

`engine` exists only on `PowerFlowSettings`, and only open engines: a study has a kind, and the
platform chooses what runs it. Nothing else in the SDK names an engine, and a test fails if
something does. `version.export("cgmes")` is short for
`version.export(ExportSettings("cgmes"))`.

## Jobs

Every calculation, import and edit is a job the engine runs outside the request. A method that
queues one returns at once with a `Job[T]`; `T` is what the job makes.

```python
class Job(Generic[T]):
    id: uuid.UUID
    kind: str                  # "import", "edit", "power_flow", "validation" or "export"
    status: str                # "pending", "running", "done", "failed" or "cancelled", as last read
    progress: str | None       # the stage it is at: waiting, starting, reading, running, storing
    error: str | None          # the engine's message, for a failed job
    params: dict[str, Any]     # what it was asked to do, as the API keeps it
    done: bool                 # status is done, failed or cancelled, as last read

    def refresh(self) -> Job[T]                # reads the job again; returns itself
    def wait(self, timeout: float | None = None, poll_interval: float = 0.5) -> T
    def cancel(self) -> None

class Jobs:
    def get(self, job_id: str | uuid.UUID) -> Job[Any]   # T chosen by its kind
    def list(self) -> list[Job[Any]]                     # the user's, newest first, at most 50
```

- `wait` polls the job, starting at `poll_interval` seconds and doubling up to 5 seconds, until it
  ends. `timeout=None` waits for as long as it takes.
  - `done`: returns its `T`, which may take more requests (a result to download, a version to read).
    Calling `wait` again returns the same `T` without asking again.
  - `failed`: raises `JobFailedError` with the engine's message.
  - `cancelled`: raises `JobCancelledError`.
  - more than `timeout` seconds: raises `JobTimeoutError`. The job is not cancelled: it carries on,
    and `wait` may be called again, or `cancel`.
- `cancel` ends a pending job at once; a running one stops at the engine's next check and stores
  nothing. A job that has already ended raises `ConflictError`. It does not wait: call `wait` to
  see it end, which then raises `JobCancelledError`.
- `Jobs.get` lets a script pick up a job queued by another one, by its id.

## Results

```python
class Table:
    rows: list[dict[str, Any]]       # one dict per row, snake_case keys
    columns: list[str]
    def __len__(self) -> int
    def __iter__(self) -> Iterator[dict[str, Any]]
    def to_pandas(self) -> pandas.DataFrame     # indexed by "id"; ImportError without the extra

class PowerFlowResult:
    converged: bool
    status: str                      # "valid", "unbalanced" or "notConverged"
    engine: str
    seconds: float
    iterations: int | None
    summary: dict[str, float]        # generation, load and losses of the whole network
    buses: Table
    branches: Table
    violations: Table
    raw: dict[str, Any]              # the whole result as the engine gave it

class ValidationResult:
    passed: bool                     # no finding of severity "error"
    counts: dict[str, int]
    findings: Table
    raw: dict[str, Any]

class ExportedFile:
    format: str
    artifact_id: uuid.UUID
    report: dict[str, Any]           # what the export kept, changed and lost
    def download(self, path: str | os.PathLike) -> pathlib.Path
    def content(self) -> bytes
```

A row holds a record's scalar fields; a branch's ends are flattened into numbered columns, and any
other list or object of a record stays only in `raw`. The columns, all snake_case, are the
result's own fields:

- `buses`: `id` (the node's key), `name`, `v_pu`, `v_kv`, `angle_deg`, `nominal_kv`, `island`,
  `bus`, `voltage_level`, `substation`, `area`.
- `branches`: `id` (the equipment's mRID), `name`, `circuit`, `losses_mw`, `losses_mvar`,
  `loading_pct`, `limit_ka`, `limit_mva`, and per end `n` (1, 2, and 3 for a three-winding
  transformer): `node{n}`, `p{n}_mw`, `q{n}_mvar`, `i{n}_ka`. An end a branch does not have is
  empty (NaN in pandas).
- `violations`: `id` (the mRID), `kind`, `name`, `value`, `limit`, `unit`, `severity`.
- `findings`: `id` (the mRID, when the finding has one), `level`, `severity`, `rule`, `cim_class`,
  `message`, `anticipated`.

pandas is imported only inside `to_pandas`, so the SDK works without it; without the extra,
`to_pandas` raises `ImportError` saying `pip install "gridoverture[pandas]"`.

## Errors

```text
GridOvertureError
├── ApiError                   the API answered with an error
│   ├── AuthenticationError    401, no valid token
│   ├── ForbiddenError         403
│   ├── NotFoundError          404 (also a LookupError)
│   ├── ConflictError          409
│   ├── InvalidRequestError    422
│   ├── RateLimitedError       429, too many requests in a minute
│   └── ServerError            5xx
├── ProjectNotFoundError       Projects.get found no project of that name (also a LookupError)
├── ObjectNotFoundError        Version.find found no object of that class and name (also a LookupError)
├── JobFailedError             job_id, kind, message
├── JobCancelledError          job_id, kind
└── JobTimeoutError            job_id, kind, timeout (also a TimeoutError)
```

An `ApiError` carries the API's problem+json (RFC 9457): `status` (the HTTP code), `title`,
`detail`, `type`, `instance`, `request_id`, and `errors`, a list of `ProblemField(where, problem)`
for a request that is not valid, such as `body.edits[0].attribute`. Its message reads
`422 the request is not valid: body.edits[0].attribute: ... (request 3f2a...)`, so the request id
that finds it in the API's logs is always at hand. A status with no class of its own is an
`ApiError`. An answer that is not problem+json, from a proxy for one, still becomes one, with its
text as `detail` and the `X-Request-ID` header, when present, as `request_id`.

A network failure (no connection, a timeout of one request) is httpx2's own
`httpx2.TransportError`.

## Examples

[`examples/ieee14_power_flow.py`](../examples/ieee14_power_flow.py) imports IEEE 14, runs an AC
power flow with reactive limits, raises a load in a child version, runs it again, compares the bus
voltages as DataFrames and exports the edited model to CGMES.
[`examples/ieee14_power_flow_powerfactory.py`](../examples/ieee14_power_flow_powerfactory.py) is the
same study in PowerFactory's Python API, for comparison.
