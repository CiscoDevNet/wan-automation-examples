# Catalyst SD-WAN Bruno Collection

This is the current Bruno collection for Cisco Catalyst SD-WAN Manager. Bruno
is a local-first API client that stores requests as Git-friendly `.bru` files.
Download it from the [official Bruno website](https://www.usebruno.com/).

## Open the Collection

In Bruno, select **Open Collection** and choose this `catalystwan/bruno`
directory. The `bruno.json` file at this level defines the collection.

## Coverage

The collection includes examples for:

- API-key authentication and device inventory.
- UX 2.0 system, transport, service, and CLI feature profiles.
- Configuration Group creation, association, variables, and deployment.
- Real-time, simple, aggregate, and bulk monitoring APIs.
- Cleanup of objects created by the collection.

It is also used by the
[Catalyst SD-WAN API Learning Hub](https://jbarozet.github.io/catalyst-sdwan-api-hub/).

## Environments and Authentication

Select either the `demo` or `sandbox` environment. Secret variables are
intentionally stored without values. Provide `vmanage` and `apikey` in Bruno
before running requests. The `sandbox` environment also requires values such
as `aaa_password` and `device_id` for configuration and deployment workflows.

Run `Authentication/01-get-auth-token` first. It exchanges the API key for an
XSRF token and stores that token as a runtime variable for subsequent requests.
Bruno keeps values marked as secret out of the checked-in environment files.

## Safe Use

Review all environment values and request payloads before running create,
deploy, delete, or cleanup requests. Use a lab environment whenever possible,
use credentials with the minimum required privileges, and never commit real
API keys or other secrets.
