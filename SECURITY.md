# Security

This repository contains learning and demonstration examples for Cisco
Catalyst SD-WAN Manager and the Meraki Dashboard. The examples are not a
production-supported SDK or application and do not have a formal release or
security-support lifecycle.

## Using the Examples Safely

Review and test each example before using it in your environment. In
particular:

- Use a lab environment whenever possible.
- Use credentials with the minimum required privileges.
- Store credentials in local environment files or a secret store; never commit
  them to the repository.
- Keep TLS certificate verification enabled. Use `--insecure` only in an
  isolated lab when no trusted certificate is available.
- Review configuration-changing requests before running them and use only
  systems you are authorized to manage.
- Do not commit Terraform state, customer configurations, API responses, or
  generated payloads containing environment data.
- Review dependencies according to your organization's security requirements.

## Reporting a Problem in an Example

If an example handles credentials unsafely, exposes sensitive information, or
has another security-related problem, open a
[GitHub issue](https://github.com/CiscoDevNet/wan-automation-examples/issues)
with the affected file and a description of the problem.

Do not include real API keys, passwords, tokens, certificates, customer data,
private configurations, or other sensitive information. If demonstrating the
problem would require publishing sensitive details, open an issue with only a
high-level description and ask the maintainers how to share the remaining
information privately.

Fixes are made against the latest code on the `main` branch. Older commits,
forks, and copied examples are not maintained.

## Cisco Product Vulnerabilities

This repository contains API clients and examples; it does not implement
Cisco Catalyst SD-WAN Manager or the Meraki Dashboard. A vulnerability in a
Cisco product or Cisco-hosted service should be reported through the
[Cisco Product Security Incident Response Team
(PSIRT)](https://sec.cloudapps.cisco.com/security/center/resources/security_vulnerability_policy.html),
not as an issue in this examples repository.
