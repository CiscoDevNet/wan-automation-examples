#!/usr/bin/env bash
set -euo pipefail

GITHUB_HOST="github.com"
REPO_NAME="wan-automation-examples"
UPSTREAM_REPO="CiscoDevNet/wan-automation-examples"
BASE_BRANCH="main"
PR_TEMP_DIR=""

cleanup() {
  if [[ -n "$PR_TEMP_DIR" && -d "$PR_TEMP_DIR" ]]; then
    rm -rf -- "$PR_TEMP_DIR"
  fi
}

fail() {
  echo "ERROR: $*" >&2
  exit 1
}

remote_host_and_path() {
  local remote url remainder authority host path
  remote="$1"
  url="$(git remote get-url "$remote")"

  case "$url" in
    git@*:*)
      host="${url#git@}"
      host="${host%%:*}"
      path="${url#*:}"
      ;;
    ssh://*|http://*|https://*)
      remainder="${url#*://}"
      authority="${remainder%%/*}"
      host="${authority##*@}"
      path="${remainder#*/}"
      ;;
    *)
      fail "Cannot parse the $remote remote URL: $url"
      ;;
  esac

  path="${path%.git}"
  printf '%s\t%s\n' "$host" "$path"
}

reject_target_overrides() {
  local argument
  for argument in "$@"; do
    case "$argument" in
      --base|--base=*|-B|-B*|--head|--head=*|-H|-H*|--repo|--repo=*|-R|-R*)
        fail "Do not override the PR target. This helper always uses $GITHUB_HOST/$UPSTREAM_REPO:$BASE_BRANCH."
        ;;
    esac
  done
}

uses_explicit_pr_content() {
  local argument
  for argument in "$@"; do
    case "$argument" in
      --title|--title=*|-t|-t*|--body|--body=*|-b|-b*|--body-file|--body-file=*|-F|-F*|\
      --fill|--fill-first|--fill-verbose|-f|--editor|-e|--template|--template=*|-T|-T*|\
      --recover|--recover=*)
        return 0
        ;;
    esac
  done
  return 1
}

generate_pr_content() {
  local base_ref output_file schema_file error_file body_file title
  base_ref="$1"
  output_file="$2"
  schema_file="$3"
  error_file="$4"
  body_file="$5"

  command -v codex >/dev/null 2>&1 || return 1
  command -v python3 >/dev/null 2>&1 || return 1
  git rev-parse --verify --quiet "$base_ref^{commit}" >/dev/null || return 1

  cat >"$schema_file" <<'JSON'
{
  "type": "object",
  "properties": {
    "title": { "type": "string" },
    "summary": { "type": "string" },
    "changes": {
      "type": "array",
      "items": { "type": "string" }
    },
    "notes": {
      "type": "array",
      "items": { "type": "string" }
    }
  },
  "required": ["title", "summary", "changes", "notes"],
  "additionalProperties": false
}
JSON

  if ! codex exec \
    --ephemeral \
    --sandbox read-only \
    --output-schema "$schema_file" \
    --output-last-message "$output_file" \
    "Review only the committed pull request changes in $base_ref...HEAD. Ignore uncommitted files. Generate a concise GitHub pull request title and description. The summary must explain the purpose, changes must list the important modifications without repeating the summary, and notes must contain only useful reviewer information or be an empty array. Do not modify files." \
    >/dev/null 2>"$error_file"; then
    return 1
  fi

  title="$(python3 - "$output_file" "$body_file" <<'PY'
import json
import sys

source, destination = sys.argv[1:]
with open(source, encoding="utf-8") as handle:
    content = json.load(handle)

title = " ".join(content.get("title", "").split())
summary = content.get("summary", "").strip()
changes = [item.strip() for item in content.get("changes", []) if item.strip()]
notes = [item.strip() for item in content.get("notes", []) if item.strip()]

if not title or not summary or not changes:
    raise SystemExit("Codex returned incomplete pull request content")

sections = ["## Summary", "", summary, "", "## Changes", ""]
sections.extend(f"- {item}" for item in changes)
if notes:
    sections.extend(["", "## Notes", ""])
    sections.extend(f"- {item}" for item in notes)

with open(destination, "w", encoding="utf-8") as handle:
    handle.write("\n".join(sections) + "\n")

print(title)
PY
  )" || return 1

  printf '%s\n' "$title"
}

main() {
  local branch owner local_sha remote_sha upstream_sha argument mode
  local ai_enabled ai_disabled_by_user ai_title ai_output ai_schema ai_error ai_body
  local origin_host origin_path upstream_host upstream_path
  local -a gh_args

  mode="preview"
  ai_enabled="true"
  ai_disabled_by_user="false"
  gh_args=()
  trap cleanup EXIT

  command -v gh >/dev/null 2>&1 || fail "The GitHub CLI (gh) is required."
  git rev-parse --is-inside-work-tree >/dev/null 2>&1 || fail "Run this command inside the repository."
  git remote get-url origin >/dev/null 2>&1 || fail "The origin remote is required."
  git remote get-url upstream >/dev/null 2>&1 || fail "The upstream remote is required."

  reject_target_overrides "$@"

  for argument in "$@"; do
    case "$argument" in
      --create)
        [[ "$mode" == "preview" ]] || fail "Use only one of --create or --web."
        mode="create"
        ;;
      --web|-w)
        [[ "$mode" == "preview" ]] || fail "Use only one of --create or --web."
        mode="web"
        gh_args+=("$argument")
        ;;
      --no-ai)
        ai_enabled="false"
        ai_disabled_by_user="true"
        ;;
      *)
        gh_args+=("$argument")
        ;;
    esac
  done

  if [[ "${DRY_RUN:-false}" == "true" && "$mode" != "preview" ]]; then
    fail "DRY_RUN=true cannot be combined with --create or --web."
  fi

  IFS=$'\t' read -r origin_host origin_path < <(remote_host_and_path origin)
  IFS=$'\t' read -r upstream_host upstream_path < <(remote_host_and_path upstream)

  [[ "$origin_host" == "$GITHUB_HOST" ]] || fail "origin must use $GITHUB_HOST, not $origin_host."
  [[ "$origin_path" == */"$REPO_NAME" ]] || fail "origin must point to a $REPO_NAME fork."
  [[ "$upstream_host" == "$GITHUB_HOST" ]] || fail "upstream must use $GITHUB_HOST, not $upstream_host."
  [[ "$upstream_path" == "$UPSTREAM_REPO" ]] || fail "upstream must point to $GITHUB_HOST/$UPSTREAM_REPO."

  owner="${origin_path%%/*}"
  [[ "$origin_path" == "$owner/$REPO_NAME" ]] || fail "origin must have the form $GITHUB_HOST/OWNER/$REPO_NAME."

  gh auth status --hostname "$GITHUB_HOST" >/dev/null 2>&1 || fail "Authenticate GitHub CLI with: gh auth login --hostname $GITHUB_HOST"

  branch="$(git symbolic-ref --quiet --short HEAD)" || fail "Detached HEAD cannot be used for a pull request."
  case "$branch" in
    main|master)
      fail "Create a feature branch before opening a pull request; '$branch' is not allowed as the head branch."
      ;;
  esac

  local_sha="$(git rev-parse HEAD)"
  remote_sha="$(git ls-remote --heads origin "refs/heads/$branch" | awk 'NR == 1 { print $1 }')"
  upstream_sha="$(git ls-remote --heads upstream "refs/heads/$BASE_BRANCH" | awk 'NR == 1 { print $1 }')"

  [[ -n "$remote_sha" ]] || fail "origin/$branch does not exist. Push the branch to origin first."
  [[ "$local_sha" == "$remote_sha" ]] || fail "Local HEAD is not pushed to origin/$branch. Push it before creating the PR."
  [[ -n "$upstream_sha" ]] || fail "The required base upstream/$BASE_BRANCH does not exist."

  if [[ -n "$(git status --porcelain)" ]]; then
    echo "WARNING: Local uncommitted files are not part of the remote pull request." >&2
  fi

  echo "Validated pull request direction:"
  echo "  host: $GITHUB_HOST"
  echo "  base: $UPSTREAM_REPO:$BASE_BRANCH"
  echo "  head: $owner:$branch"

  if uses_explicit_pr_content "${gh_args[@]}"; then
    ai_enabled="false"
  fi

  if [[ "$ai_enabled" == "true" ]]; then
    PR_TEMP_DIR="$(mktemp -d "${TMPDIR:-/tmp}/create-upstream-pr.XXXXXX")"
    ai_output="$PR_TEMP_DIR/pr-content.json"
    ai_schema="$PR_TEMP_DIR/pr-content-schema.json"
    ai_error="$PR_TEMP_DIR/codex-error.log"
    ai_body="$PR_TEMP_DIR/pr-body.md"

    echo "Generating a pull request title and description with Codex..."
    if ai_title="$(generate_pr_content "$upstream_sha" "$ai_output" "$ai_schema" "$ai_error" "$ai_body")"; then
      gh_args+=(--title "$ai_title" --body-file "$ai_body")
      echo
      echo "Title: $ai_title"
      echo
      cat "$ai_body"
    else
      echo "WARNING: Codex PR content was unavailable; continuing with the standard GitHub CLI flow." >&2
      if [[ -s "$ai_error" ]]; then
        sed -n '1,3p' "$ai_error" >&2
      fi
    fi
  elif [[ "$ai_disabled_by_user" == "true" ]]; then
    echo "Codex PR content generation disabled."
  fi

  case "$mode" in
    preview)
      echo "Preview only; no pull request was created."
      echo "Review in the browser with: $0 --web"
      echo "Create directly with: $0 --create"
      ;;
    web)
      gh pr create \
        --repo "$UPSTREAM_REPO" \
        --base "$BASE_BRANCH" \
        --head "$owner:$branch" \
        "${gh_args[@]}"
      ;;
    create)
      gh pr create \
        --repo "$UPSTREAM_REPO" \
        --base "$BASE_BRANCH" \
        --head "$owner:$branch" \
        "${gh_args[@]}"
      ;;
  esac
}

if [[ "${BASH_SOURCE[0]}" == "$0" ]]; then
  main "$@"
fi
