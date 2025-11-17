# Getting Started

## API Reference

The following categories organize the Cisco Catalyst SD-WAN Manager API:

+ **Administration and Setting:** Includes global parameters in SD-WAN Manager, user, group and tenant management, software maintenance, backup and restore, and container management.

+ **UX 1.0 Configuration:** Includes original device configuration, policy configuration, device templates, and feature templates.

+ **UX 2.0 Configuration:** Includes the new configuration framework, with Configuration Groups, Policy Groups, and Topology Groups.

+ **Feature Profiles:** Includes feature profiles associated with UX 2.0 configuration.

  + **Feature Profiles: SD-WAN Solution, System**
  API operations related to core system configurations, device management, and platform-level settings.

  + **Feature Profiles: SD-WAN Solution, Transport**
  API operations that are related to transport layer features such as interface and tunnel configurations.

  + **Feature Profiles: SD-WAN Solution, Service**
  API operations that are related to service-related features including voice, security, and application optimization.

  + **Feature Profiles: SD-WAN Solution, Others (mobility, nfvirtual)**
  API operations supporting mobility features and Network Function Virtualization (NFV) configurations.

  + **Feature Profiles: SD-Routing Solution** 
  API operations for software-defined routing features and autonomous router management.

  + **Feature Profiles: Others**
  API operations for additional feature profiles not covered in the above categories.

+ **SD-WAN Services:** Includes SD-WAN services, such as Cloud OnRamp for SaaS, Multicloud and so on.

+ **Partner Integrations:** Includes access to services from Webex, Secure Access, and others.

+ **Monitoring and Troubleshooting:** Includes monitoring of devices, links, applications, systems, and so on (statistics APIs, real-time APIs, statistics bulk APIs, device state). Includes the alarm and event notification configuration, and alarm, event, and audit log queries.

## Base URI

Every API request will begin with the following Base URI.

```example
https://<vmanage-server>:<port>/dataservice
```

Except for a few file upload APIs, most of the request payloads are in JSON format.

## API User Requirements

Your user role must have API access permission.

### JWT-based Authentication

Log in with a username and password to receive a JWT token.

+ `POST /jwt/login` with content type `application/json` in the request header.
+ Submit the mandatory "username" and "password" attributes `{"username": "your_username", "password": "your_password"}`. Add an optional "duration" attribute in seconds for the access token in the POST request body.
+ The response body contains a JSON object with the following claims: JWT access token and "csrf" that contains a cross-site request forgery (XSRF) prevention token required for most POST operations. The "csrf" token is included directly in the login response and does not require a separate API call to retrieve the XSRF token.

Read more about authenticating, including generating an access token [here](./02-Authentication.md#jwt-based-authentication).

### Session-based Authentication

Log in with a username and password to establish a session.

+ `POST /j_security_check` with `content type x-www-form-urlencoded`
+ Submit the username and password as `j_username` and `j_password`
+ The session token is in the response http cookie, `JSESSIONID={session hash}`.

Get a cross-site request forgery prevention token, necessary for most POST operations:

+ `GET /dataservice/client/token` with `content type application/json`
+ You need the `JSESSIONID={session hash}` cookie to authenticate.
+ The XSRF token is in the response body.
+ Use the XSRF token along with the JESSIONID cookie for ongoing API requests.

Read more about authenticating, including generating an access token [here](./02-Authentication.md#session-based-authentication).
