<p align="center">
  <picture>
    <source media="(prefers-color-scheme: dark)" srcset="assets/logo-horizontal-dark.svg">
    <img src="assets/logo-horizontal-light.svg" alt="Grid Overture" width="320">
  </picture>
</p>

<h1 align="center">SDK de Python de Grid Overture</h1>

<p align="center">
  <strong>Modelos de redes eléctricas desde Python: importa, edita, resuelve y lee los resultados como DataFrames.</strong>
</p>

<p align="center"><a href="README.md">English</a></p>

`gridoverture` es el cliente de Python de la plataforma Grid Overture, que lleva modelos de red de
PSS/E, MATPOWER, pandapower, VeraGrid, IEEE CDF y PowerFactory a CGMES 3.0, guarda cada versión y
corre estudios sobre ellas con motores abiertos. Está pensado como la API de Python de
PowerFactory: buscas un objeto, cambias sus atributos, corres un cálculo y lees sus resultados. Un
cálculo es un trabajo asíncrono, los ajustes están tipados y los resultados salen como tablas que
se convierten en DataFrames de pandas.

## Inicio rápido

```bash
pip install "gridoverture[pandas] @ git+https://github.com/Grid-Overture/gridoverture-sdk@v0.1.0"

export GRIDOVERTURE_URL=https://<la dirección de tu plataforma>
export GRIDOVERTURE_TOKEN=gop_...   # Studio: menú de la cuenta, Access tokens, alcance write
```

```python
import gridoverture as go

with go.Client() as client:
    project = client.projects.create("IEEE 14")
    version = project.versions.import_file("IEEE_14_bus.raw").wait()  # está en examples/

    flow = version.power_flow(go.PowerFlowSettings(start="flat")).wait(timeout=120)
    print(flow.converged, flow.summary["losses_mw"])
    print(flow.buses.to_pandas()[["name", "v_pu", "angle_deg"]])
```

## Compatibilidad

El SDK y la plataforma se encuentran en un **contrato de API** versionado. Cada respuesta de la
plataforma lo nombra en la cabecera `Gridoverture-Contract`: una minor más nueva del mismo major
funciona, otro major lanza `IncompatibleContractError`, y una ruta obsoleta (`Deprecation` o
`Sunset`) avisa con un `DeprecatedApiWarning` y sus fechas.

| SDK | Contrato de API | Funciona con |
|---|---|---|
| v0.2.0 | 1.x | una plataforma que habla el contrato 1, sus rutas `/v1` |
| v0.1.0 | ninguno | una plataforma anterior al contrato; las posteriores mantienen sus rutas sin versión como alias obsoletos hasta su retiro |

## Más

- Qué puedes hacer, autenticación, versiones y cómo contribuir: el [README en inglés](README.md),
  que es la fuente.
- Cada clase, argumento y excepción: [la referencia](docs/reference.md), en inglés.
- Licencia: [AGPL-3.0-or-later](LICENSE). El nombre y el logo de Grid Overture son marcas y no
  están cubiertos por la licencia.
