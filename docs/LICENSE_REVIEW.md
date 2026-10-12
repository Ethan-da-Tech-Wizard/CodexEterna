# License review — CodexEterna

Reviewed 2026-10-12. Original project code retains **MIT** terms in [LICENSE](../LICENSE).

The owner selected MIT for previously unlicensed original code. Existing licenses were preserved. This choice does not relicense copied code, dependencies, datasets, model weights, fonts, logos, or game assets.

## Preserved notices

- [LICENSE](../LICENSE)

## Dependency evidence

[DEPENDENCIES.csv](DEPENDENCIES.csv) lists 10 manifest and lockfile records. Repeated packages can appear under different manifests, versions, or development scopes. Registry metadata is evidence, not a replacement for the actual license text. For unpinned ranges, `metadata_version` is the version inspected and is not a claim about every install. Go and system/build tools can require notices beyond package-manager metadata.

| Component | Declared version | License evidence |
| --- | --- | --- |
| NuGet: Microsoft.AspNetCore.SignalR | 1.1.0 | [Custom/URL terms — inspect linked license](https://raw.githubusercontent.com/aspnet/AspNetCore/2.0.0/LICENSE.txt) |
| NuGet: Swashbuckle.AspNetCore | 6.5.0 | [MIT](https://api.nuget.org/v3-flatcontainer/swashbuckle.aspnetcore/6.5.0/swashbuckle.aspnetcore.6.5.0.nupkg) |
| PyPI: fastapi | ==0.104.1 | [OSI Approved :: MIT License](https://pypi.org/pypi/fastapi/0.104.1/json) |
| PyPI: uvicorn | ==0.24.0 | [OSI Approved :: BSD License](https://pypi.org/pypi/uvicorn/0.24.0/json) |
| PyPI: sqlalchemy | ==2.0.23 | [MIT](https://pypi.org/pypi/sqlalchemy/2.0.23/json) |
| PyPI: psycopg2-binary | ==2.9.9 | [LGPL with exceptions](https://pypi.org/pypi/psycopg2-binary/2.9.9/json) |
| PyPI: requests | ==2.31.0 | [Apache 2.0](https://pypi.org/pypi/requests/2.31.0/json) |
| PyPI: pydantic | ==2.5.0 | [OSI Approved :: MIT License](https://pypi.org/pypi/pydantic/2.5.0/json) |
| PyPI: python-dotenv | ==1.0.0 | [BSD-3-Clause](https://pypi.org/pypi/python-dotenv/1.0.0/json) |
| PyPI: alembic | ==1.12.1 | [MIT](https://pypi.org/pypi/alembic/1.12.1/json) |

## Project-specific considerations

Throughput and production-readiness claims in older notes are historical claims, not newly verified performance guarantees. Data-provider terms remain separate from the source license.

## Remaining work before binary distribution

No unresolved registry-license lookup remains in the listed package records. System packages, downloaded tools/models, optional plugins, release binaries, and externally obtained assets need a build-specific inventory. This source review is not a blanket legal certification or a claim that every release artifact has been audited.
