# Bruno Collection Examples

This collection provides several examples of working with the Cisco Catalyst SD-WAN and Meraki Dashboard APIs.

## Collections

This repository has 3 collections:

- Cisco-SD-WAN: Includes examples for Cisco Catalyst SD-WAN Manager.
- Meraki: Features examples for the Meraki Dashboard API.
- Misc: Additional examples and resources.

Start Bruno.app then open collections from the "Collections" folder.

- SD-WAN collection: click "Open Collection", find and select "Cisco-SD-WAN" folder
- Meraki collection: click "Open Collection, find and select "Meraki" folder
- Various examples: click "Open Collection, find and select "Misc" folder

## Secrets Management

### Overview

In any collection, there are secrets that need to be managed. These secrets can be anything such as API keys, passwords, or tokens.

A common practice is to store these secrets in environment variables.

There are two ways in which developers share bruno collections:

- Check-in the collection folder to source control (like git)
- Export the collection to a file and share it

In both these cases we want to ensure that the secrets are stripped out of the collection before it is shared.

Bruno offers three (3) approaches to manage secrets in collections.

- Secret Variables
- DotEnv File
- Integration with a Secret Manager

### Secret Variables

In this approach, you can check the secret checkbox for any variable in your environment. Bruno will manage your secrets internally and will not write them into the environment file.

![secrets](../bruno/assets/secret-variables.webp)

Your environment file at `<collection-name</environments/<name>.bru` would look like

```bru
vars {
  url: https://echo.usebruno.com
}
vars:secret [
  jwt-token
]
```

And now you can safely check in your collection to source control without worrying about exposing your secrets.

When you export your collection as a file, Bruno will not export the secret variables.

### DotEnv File

Environment variables are used to store sensitive data such as API keys, tokens, and configuration settings outside the source code. This helps keep your code secure and makes it easier to manage different settings for various environments (e.g., local, staging, production). In **Bruno**, environment variables can be managed through .env files.

In Bruno, you can store your secrets (e.g., API keys, JWT tokens) in a .env file located at the root of your collection folder.

You cannot create the .env file directly inside Bruno. You need to manually create the .env file at the root of your Bruno collection folder to store your secrets. Once created, you can access those variables within your Bruno collection.

Folder Structure Example
Below is an example folder structure for your collection:

bruno-collection

- api-folder
- .env
- .gitignore
- bruno.json
- package.json

Create a .env file manually in the root of your collection folder. This file will store your sensitive environment variables.

Define your secrets in the .env file. For example:

```env
JWT_TOKEN=your_jwt_token_value
API_KEY=your_api_key_value
```

These secrets will be accessible in your Bruno collection via the process.env object.

![env](../bruno/assets/dot-env-vars.webp)

### Integration with Secret managers Premium

For users of Bruno Ultimate, you can take your secret management one step further and perform an integration with a secret vault.

Currently, we support integrations with:

- [HashiCorp vault](https://docs.usebruno.com/secrets-management/secret-managers/secret-managers/hashicorp-vault)
- [AWS Secrets Manager](https://docs.usebruno.com/secrets-management/secret-managers/secret-managers/aws-secrets-manager)
- [Azure Key Vault](https://docs.usebruno.com/secrets-management/secret-managers/secret-managers/azure-key-vault)

### Using Bruno API Client to test JWT-based authentication

If you use [Bruno](https://www.usebruno.com/) API client: to assign the `token` and `csrf` values from the JSON response to a variable in Bruno, you'll typically use a "Tests" script or a similar post-response script feature available in Bruno. This allows you to parse the response body and extract specific values.

```javascript
// The 'res' variable is automatically available in post-request scripts
// and contains the response object.

// Always check if the 'res' object and its 'body' property exist
// before trying to access them.
if (res && res.body) {
    // The 'res.body' is automatically parsed as JSON
    // if the Content-Type of the response is 'application/json'.
    // So, you can directly access its properties.
    const responseJson = res.body;

    // Extract the csrf token
    const csrfToken = responseJson.csrf;

    // Extract the main JWT token
    const jwtToken = responseJson.token;

    // Set environment variables for both tokens
    bru.setVar("csrf_token", csrfToken);
    bru.setVar("jwt_token", jwtToken);

    // Optional: Log the values to the console for debugging
    console.log("Extracted CSRF Token:", csrfToken);
    console.log("Extracted JWT Token:", jwtToken);
} else {
    // Log an error if the response or its body is not as expected
    console.error("Error: Response or response body is undefined or empty.");
    // You might also want to assert a failure if this is critical for your test
    // bru.assert(false, "Failed to get response body or it was empty.");
}
```

Define a new request with:

The API endpoint to authenticate: `https://{{vmanage}}:{{port}}/jwt/login`

Define content-type as `application/json` in the "Headers" tab content:

![headers](assets/Bruno-auth-tab-headers.png)

The "Body" tab content has a json payload with username, password and optional duration.

![body](assets/Bruno-auth-tab-body.png)

The "Tests" tab content has the script to save JWT token and and XSRF token in variables (jwt_token and csrf_token) :

![tests](assets/Bruno-auth-tab-tests.png)

Then use the JWT token (jwt_token variable) along with the XSRF token (csrf_token variable) for further API requests. The following figure shows an API call with Bruno.

Headers tab content - Re-use jwt_token and csrf_token saved in the authentication:

![headers](assets/Bruno-call-tab-headers.png)
