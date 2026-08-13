# Repository Guidance for Coding Agents

## Purpose and Scope

This repository contains learning and demonstration examples for automating:

- Cisco Catalyst SD-WAN Manager with Python, Bruno, Terraform, and an MCP server.
- Cisco Meraki Dashboard with Python, Bruno, and Terraform.

The examples are not production-supported SDKs or applications. Keep changes
small, readable, safe for lab use, and focused on a practical automation task.
Read the nearest area-specific `README.md` before modifying an example.

## Repository Layout

```text
catalystwan/
├── bruno/       Current Catalyst SD-WAN Bruno collection
├── lab/         Archived Python scripts retained for older Cisco documentation
├── mcp-sdwan/   Podman-based Catalyst SD-WAN MCP server
├── python/      Maintained Catalyst SD-WAN Python examples
└── terraform/   Provider and NetAsCode module examples
meraki/
├── bruno/       Meraki Dashboard Bruno collection
├── python/      Meraki Python examples
└── terraform/   Provider and NetAsCode module examples
scripts/         Contribution helpers
```

Keep examples with their architecture: Catalyst SD-WAN changes belong under
`catalystwan/`; Meraki changes belong under `meraki/`. Bruno collections stay
beside the Python and Terraform examples for the same platform.

Do not add a general documentation tree. Guided Cisco Catalyst SD-WAN lessons,
API concepts, and hands-on labs belong in the external
[Catalyst SD-WAN API Learning Hub](https://jbarozet.github.io/catalyst-sdwan-api-hub/).
The URL is provisional and may be updated when an official URL is available.

## Authoritative Documentation

Use primary documentation and verify current API paths, schemas, and product
version compatibility before adding or changing requests:

- [Catalyst SD-WAN API documentation](https://developer.cisco.com/docs/sdwan/)
- [Catalyst SD-WAN API Learning Hub](https://jbarozet.github.io/catalyst-sdwan-api-hub/)
- [Meraki Dashboard API documentation](https://developer.cisco.com/meraki/api-v1/)
- [CiscoDevNet SD-WAN Terraform provider](https://registry.terraform.io/providers/CiscoDevNet/sdwan/latest/docs)
- [CiscoDevNet Meraki Terraform provider](https://registry.terraform.io/providers/CiscoDevNet/meraki/latest/docs)
- [NetAsCode Catalyst SD-WAN module](https://netascode.cisco.com/docs/start/sdwan/first_steps/)
- [NetAsCode Meraki module](https://netascode.cisco.com/docs/start/meraki/first_steps/)

This repository does not contain a checked-in OpenAPI specification. Do not
invent endpoints or payload fields. Note that
`catalystwan/python/administration/legacy_settings.py` intentionally contains
undocumented, version-dependent compatibility routes.

Use an appropriate authorized environment for integration tests. Cisco DevNet
sandboxes can be found at <https://devnetsandbox.cisco.com/DevNet>.

## Catalyst SD-WAN Python

The maintained Python project is `catalystwan/python/`, requires Python 3.12,
and is managed with `uv`. Run its commands from that directory:

```bash
cd catalystwan/python
uv python install
uv sync
uv run python -m unittest discover -s tests
uvx ruff check .
```

The client uses API-key authentication and shared code in `utilities/` for
transport, CLI options, output, and errors. Preserve these design rules:

- Accept the API key only through the environment or an ignored `.env` file.
- Exchange it through `/dataservice/client/token` and keep tokens in memory.
- Keep TLS verification enabled by default; retain explicit lab-only overrides.
- Use bounded request timeouts and avoid logging credentials or tokens.
- Reuse `utilities/` rather than duplicating authentication or HTTP handling.
- Add reusable monitoring cases to the registry in `monitoring/cases.py`.
- Add or update unit tests for reusable behavior; tests must not call live APIs.

Use `.env.example` for variable names and placeholders. Never read, print, or
commit values from a developer's `.env` file.

`catalystwan/lab/` is a historical record still referenced by Cisco's older
[Basic Management Examples](https://developer.cisco.com/docs/sdwan/basic-management-examples/).
Do not modernize, reorganize, or recommend those scripts for new work unless a
task explicitly targets the legacy material. Direct users to
`catalystwan/python/` instead.

The scripts in `meraki/python/` are separate, older standalone examples. Do not
silently refactor them into the Catalyst Python project or assume its utilities
and test commands apply to them.

## Bruno Collections

Open `catalystwan/bruno/` or `meraki/bruno/` as the collection root in Bruno.
Preserve Git-friendly `.bru` files and platform naming conventions.

- Catalyst SD-WAN uses API-key authentication followed by XSRF token exchange.
- Meraki uses the secret `API_KEY` environment variable.
- Keep checked-in secret variables empty and sample IDs unmistakably fictional.
- Review dependencies and request order before changing collection workflows.
- Treat create, deploy, delete, and cleanup requests as potentially destructive.

The Catalyst collection is also consumed by the external Learning Hub, so
avoid unnecessary request renames or moves that could break guided lessons.

## Terraform

Each platform has separate `provider/` and `module/` examples. Preserve that
separation and format all changed Terraform files:

```bash
terraform fmt -check -recursive catalystwan/terraform
terraform fmt -check -recursive meraki/terraform
```

For each changed provider or module directory, run
`terraform init -backend=false` and `terraform validate` when provider downloads
are available.
Do not run `terraform apply` or `terraform destroy` merely to validate a change.
Run `terraform plan` only against an authorized lab with local, untracked
configuration. Never commit `config.yaml`, state files, plan files, generated
defaults, logs, or credentials.

## MCP Server

`catalystwan/mcp-sdwan/` is an optional Podman-based MCP server, not a dependency
for the rest of the repository. Follow its README for building and configuring
it. Keep connection values in Podman secrets, do not expose secret values in
logs, and do not start containers or connect to an SD-WAN Manager unless the
task explicitly requires it and the environment is authorized.

## Safety and Validation

- Never commit API keys, passwords, tokens, certificates, customer data,
  private topologies, API responses, `.env` files, or Terraform state.
- Prefer placeholders, `.env.example`, and `config-example.yaml`.
- Do not make live API calls by default. Static checks and mocked unit tests are
  the normal validation path.
- Before any live test, identify whether the operation reads, creates, deploys,
  changes, or deletes data. Require explicit authorization for mutating calls.
- Do not weaken TLS verification or remove timeouts to make an example pass.
- Preserve sample behavior unless fixing a bug or documenting an intentional
  compatibility change.
- Update the nearest README when setup, dependencies, configuration, commands,
  request ordering, or behavior changes.

Follow `SECURITY.md` for example-related security concerns. Cisco product or
hosted-service vulnerabilities belong with Cisco PSIRT, not this repository.

## Contribution and Pull Requests

Use `origin` for the contributor fork and `upstream` for
`CiscoDevNet/wan-automation-examples`. Work on a feature branch based on
`upstream/main`; do not commit directly to `main`. Use focused commits with
concise imperative subjects. Conventional Commit prefixes such as `docs:`,
`feat:`, `fix:`, and `chore:` are encouraged. Keep unrelated change blocks in
separate commits.

The optional `scripts/create-upstream-pr.sh` helper validates remotes and the
pushed branch before targeting `CiscoDevNet/wan-automation-examples:main`:

```bash
./scripts/create-upstream-pr.sh          # validate and preview only
./scripts/create-upstream-pr.sh --web    # review and submit in GitHub
./scripts/create-upstream-pr.sh --create # create immediately
./scripts/create-upstream-pr.sh --no-ai  # disable optional Codex text generation
```

When available, Codex proposes a title and a body with `Summary`, `Changes`,
and optional `Notes`. Codex is not required: failures fall back to the normal
GitHub CLI workflow, and explicit `gh` title/body/fill options take precedence.
Prefer `--web` when a person should review and edit the final PR before
submission.

See `CONTRIBUTING.md` for the complete fork, branch, validation, commit, rebase,
and pull-request workflow.
