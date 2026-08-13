# Meraki Bruno Collection

This Bruno collection contains examples for the Meraki Dashboard API. Bruno is
a local-first API client that stores requests as Git-friendly `.bru` files.
Download it from the [official Bruno website](https://www.usebruno.com/).

## Open the Collection

In Bruno, select **Open Collection** and choose this `meraki/bruno` directory.
The `bruno.json` file at this level defines the collection.

## Authentication

Select the `Meraki Dash` environment and provide `API_KEY` in Bruno. The
variable is marked as secret, so its value is not stored in the checked-in
environment file. Replace the example `organizationId` before running an
organization-specific request.

Use an API key with only the permissions required for the requests you intend
to run. Never commit a real API key.

## Requests

- `GET Organization.bru` lists organizations available to the API key.
- `GET Radius Servers.bru` retrieves RADIUS server settings for the configured
  organization.

Review request URLs, variables, and permissions before sending requests against
a live Meraki organization.
