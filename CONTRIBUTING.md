# Contributing to WAN Automation Examples

Thank you for helping improve WAN Automation Examples. This repository contains
Python, Terraform, and Bruno examples for automating Cisco Catalyst SD-WAN
Manager and the Meraki Dashboard.

The examples are intended for learning and demonstration. Keep changes easy to
understand, safe to run in a lab, and focused on a practical automation task.

## Before You Start

Read [README.md](README.md) for the repository overview and the README in the
area you plan to change. [AGENTS.md](AGENTS.md) contains additional guidance for
coding agents.

This repository focuses on runnable examples. Guided Catalyst SD-WAN API
lessons and lab documentation belong in the
[Catalyst SD-WAN API Learning Hub](https://jbarozet.github.io/catalyst-sdwan-api-hub/).

Use GitHub issues in
[CiscoDevNet/wan-automation-examples](https://github.com/CiscoDevNet/wan-automation-examples/issues)
to report bugs or discuss substantial changes before beginning a large rewrite.
For security-related concerns, follow [SECURITY.md](SECURITY.md).

## 1. One-Time Setup

Fork
[CiscoDevNet/wan-automation-examples](https://github.com/CiscoDevNet/wan-automation-examples)
to your GitHub account, then clone your fork:

```bash
git clone git@github.com:<your-username>/wan-automation-examples.git
cd wan-automation-examples
```

Add the CiscoDevNet repository as `upstream`:

```bash
git remote add upstream git@github.com:CiscoDevNet/wan-automation-examples.git
git remote -v
```

In this setup, `origin` is your fork and `upstream` is the shared CiscoDevNet
repository. Push contribution branches to `origin`; do not push them directly
to `upstream`.

Install the tools needed for the part of the repository you will change. The
current Catalyst SD-WAN Python examples use Python 3.12 and
[uv](https://docs.astral.sh/uv/):

```bash
cd catalystwan/python
uv python install
uv sync
cd ../..
```

Terraform and Bruno changes require their respective CLIs. See
[Catalyst SD-WAN Terraform](catalystwan/terraform/README.md),
[Meraki Terraform](meraki/terraform/README.md), and
[Catalyst SD-WAN Bruno](catalystwan/bruno/README.md) or
[Meraki Bruno](meraki/bruno/README.md) for area-specific setup.

## 2. Make and Submit a Change

### Start a Branch

Fetch the latest shared branch and create a branch for your change:

```bash
git fetch upstream
git switch --create feature/describe-change upstream/main
```

Do not make changes directly on `main`. Use a short, lowercase branch name with
a descriptive prefix, for example:

```text
docs/clarify-api-key-setup
feature/add-device-health-example
fix/handle-empty-api-response
chore/update-terraform-version
```

### Make Focused Changes

- Put Catalyst SD-WAN examples under `catalystwan/` and Meraki examples under
  `meraki/`.
- Keep Python examples small, readable, and consistent with the structure and
  shared utilities documented in [catalystwan/python/README.md](catalystwan/python/README.md).
- Keep Terraform provider examples separate from module examples and format all
  changed `.tf` files.
- Update nearby documentation when commands, configuration, dependencies, or
  behavior change.
- Preserve existing sample behavior unless fixing a bug or documenting an
  intentional compatibility change.

Never commit real credentials, API keys, tokens, customer data, private
topologies, `.env` files, Terraform state, generated caches, or editor files.
Use `.env.example`, `config-example.yaml`, reserved documentation addresses,
and obvious placeholder values for sample data.

### Validate Your Work

Run checks appropriate to the files you changed. For the Catalyst SD-WAN Python
examples:

```bash
cd catalystwan/python
uv run python -m unittest discover -s tests
uvx ruff check .
cd ../..
```

Add or update unit tests for reusable Python behavior. Tests must not require
production credentials or make live API calls.

For Terraform changes, first check formatting from the repository root:

```bash
terraform fmt -check -recursive catalystwan/terraform
terraform fmt -check -recursive meraki/terraform
```

Also run `terraform validate` in each changed provider or module directory
after `terraform init -backend=false`. Run `terraform plan` only against an
authorized lab using local, untracked configuration. Do not apply or destroy
infrastructure merely to validate a contribution.

For examples that call a live API, perform optional integration testing only
against a system you are authorized to use. Note the product release and test
environment in the pull request, without including secrets or identifying
customer details.

### Commit and Push

Write concise, imperative commit subjects. Conventional Commit prefixes are
encouraged:

```text
docs: clarify API key setup
feat: add device health example
fix: handle empty monitoring response
```

Keep unrelated changes in separate commits, then push the branch to your fork:

```bash
git add <changed-files>
git commit -m "docs: describe the change"
git push -u origin feature/describe-change
```

### Open the Pull Request

Open a pull request with:

- base repository: `CiscoDevNet/wan-automation-examples`
- base branch: `main`
- head repository: your fork
- compare branch: your working branch

Include a concise explanation of the problem and change, the checks you ran,
and a linked issue when applicable. Mention any required product version,
feature flag, or lab setup. Keep the pull request small enough to review as one
coherent change.

The optional helper validates the configured remotes, branch, and pushed HEAD
before targeting `CiscoDevNet/wan-automation-examples:main`:

```bash
./scripts/create-upstream-pr.sh          # validate and preview
./scripts/create-upstream-pr.sh --web    # finish the PR in a browser
./scripts/create-upstream-pr.sh --create # create the PR directly
./scripts/create-upstream-pr.sh --no-ai  # skip optional Codex generation
```

It requires an authenticated [GitHub CLI](https://cli.github.com/) session and
expects `origin` to be your `wan-automation-examples` fork and `upstream` to be
`CiscoDevNet/wan-automation-examples`. When the Codex CLI is available, the
helper proposes a title and a description containing `Summary`, `Changes`, and,
when useful, `Notes`. If Codex is unavailable or generation fails, the helper
continues with the standard GitHub CLI workflow. Explicit GitHub CLI content
options such as `--title`, `--body`, or `--fill` also take precedence over Codex.

By participating, you agree to follow [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md).

## 3. Keep an Existing Branch Current

If `upstream/main` changes after you push your branch, rebase your own branch:

```bash
git status
git fetch upstream
git switch feature/describe-change
git rebase upstream/main
git push --force-with-lease origin feature/describe-change
```

Start with a clean working tree. Rebase only your own contribution branches,
never a shared branch, and never use plain `--force`.

If conflicts occur, resolve them, stage the files, and continue:

```bash
git add <resolved-files>
git rebase --continue
```

Use `git rebase --abort` to return the branch to its pre-rebase state.

After the pull request is merged, update your local `main` and optionally
delete the contribution branch:

```bash
git fetch upstream
git switch main
git merge --ff-only upstream/main
git branch -d feature/describe-change
git push origin --delete feature/describe-change
```
