# Legacy Catalyst SD-WAN API Lab Scripts

## Why This Directory Is Retained

The scripts in this directory accompany older Cisco Catalyst SD-WAN API lab
material and are retained as a historical reference. Some of them are still
referenced by Cisco's
[Basic Management Examples](https://developer.cisco.com/docs/sdwan/basic-management-examples/)
and related API learning content. Keeping the original filenames and behavior
here prevents those references from becoming dead ends.

These files are not the recommended starting point for new Python automation.
They may still be useful when following the older documentation or comparing
legacy API workflows with current examples.

## Recommended Examples

Use the maintained examples under [`../python/`](../python/) for new work. They
provide:

- API-key authentication rather than username/password session login.
- Shared HTTP, authentication, CLI, output, and error-handling utilities.
- TLS verification by default, with explicit lab-only overrides.
- Bounded request timeouts and safer handling of credentials.
- A modular structure for administration, configuration, inventory, and
  monitoring examples.
- Python 3.12 dependency management with `uv` and unit tests.

See the [current Python examples README](../python/README.md) for setup and
usage. For guided Catalyst SD-WAN API lessons, visit the
[Catalyst SD-WAN API Learning Hub](https://jbarozet.github.io/catalyst-sdwan-api-hub/).

## Important Limitations

The legacy scripts are preserved substantially as originally published and
are not actively modernized. In particular, they:

- Use username/password session authentication with `JSESSIONID` and an XSRF
  token.
- Disable TLS certificate verification in API requests.
- Pin old Python dependencies in `requirements.txt`.
- Reflect older vManage terminology, API behavior, and lab environments.
- May not work with current Cisco Catalyst SD-WAN Manager releases without
  changes.

Do not use these scripts unchanged in production. Never commit credentials or
run configuration-changing examples against a system you are not authorized
to manage.

## Contents

| File | Historical purpose |
| --- | --- |
| `vmanage_apis.py` | Device inventory and monitoring examples |
| `vmanage_config_apis.py` | Device template and policy configuration examples |
| `monitor-app-route-stats.py` | Application-aware routing statistics and reports |
| `alarms_apis.py` | Alarm queries and consumed-event details |
| `webhook.py` | Example alarm webhook receiver |
| `hub_list.yaml` | Input data used by an application-route example |
| `requirements.txt` | Original pinned dependency set |
