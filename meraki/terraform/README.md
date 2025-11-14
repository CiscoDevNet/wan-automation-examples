# Meraki Terraform Examples

This folder provides Terraform examples for interacting with Cisco Meraki Dashboard APIs,
using the Meraki Terraform Provider as well as the Meraki Terraform modules for even better abstraction.

Please note these examples are for demonstration purposes only and not production-ready.

## Overview

When working with Cisco Meraki Dashboard APIs using Terraform, you have two primary approaches: directly leveraging the CiscoDevNet/meraki provider or utilizing the higher-level netascode/nac-meraki/meraki module. Both serve the purpose of automating Meraki configurations, but they operate at different levels of abstraction.

### Meraki Terraform Provider

The CiscoDevNet/meraki Terraform Provider:

- [Terraform Registry](https://registry.terraform.io/providers/CiscoDevNet/meraki/latest)
- [Github Repository](https://github.com/CiscoDevNet/terraform-provider-meraki)

**What it is:**

A Terraform provider is a plugin that Terraform uses to interact with an API of a specific service or platform. The CiscoDevNet/meraki provider is the fundamental building block for managing Cisco Meraki configurations with Terraform. It directly exposes the underlying Meraki Dashboard APIs as Terraform resources.

**How it works:**

When you use this provider, you define individual Meraki components (like organizations, networks, etc.) as distinct Terraform resources. Each resource in your .tf files directly maps to an API call to the Meraki Dashboard. This approach gives you granular control over every aspect of your Meraki configuration.

**Use Case:**

This option is ideal for users who need fine-grained control, want to manage specific Meraki objects directly, or are integrating with existing automation workflows that require direct API interaction. It's also the foundation upon which higher-level modules are built.

### Meraki Terraform Module

The netascode/nac-meraki/meraki Terraform Module:

- [Terraform Registry](https://registry.terraform.io/modules/netascode/nac-meraki/meraki/latest)
- [Github Repository](https://github.com/netascode/terraform-meraki-nac-meraki)
- [Github - Pre-deployment validation tool](https://github.com/netascode/iac-validate)

**What it is:**

A Terraform module is a container for multiple resources that are used together. The netascode/nac-meraki/meraki module provides a higher level of abstraction over the CiscoDevNet/meraki provider. It's designed to simplify complex Meraki configurations by allowing you to define your desired state using YAML configuration files.

**How it works:**

Instead of defining each individual resource (e.g., an organization, then a network, etc.) separately in HCL (Terraform's language), this module allows you to describe your entire Meraki intent in a more human-readable YAML format. The module then takes this YAML input, translates it into the necessary CiscoDevNet/meraki provider resources, and provisions them on the Meraki Dashboard. This approach often reduces the amount of boilerplate HCL code you need to write.

**Use Case:**

This option is excellent for users who prefer a more declarative, "intent-based" approach to Meraki configuration. It's particularly useful for quickly deploying common Meraki patterns, managing configurations from a single YAML source, and simplifying the overall Terraform code for complex deployments. It abstracts away many of the underlying provider details, making it easier to manage the entire Meraki fabric.

## Folders

- `provider`: example leveraging CiscoDevNet/meraki Terraform Provider:
- `module`: example leveraging netascode/nac-meraki/meraki Terraform Module

## Terraform Module

Go to `module` folder.

Rename `config-example.yaml` to `config.yaml` and fill in parameters.

Initialize Terraform (this will download provider and module):

```shell
terraform init
```

Deploy devices configuration:

```shell
terraform init
terraform plan
terraform apply --auto-approve
```

Once finished, delete configuration:

```shell
terraform destroy --auto-approve
```

Note that this will only destroy configuration that was created by Terraform.

For more information and examples, visit: <https://netascode.cisco.com/docs/start/meraki/first_steps/>

## Terraform Provider

Go to `provider` folder.

Rename `config-example.yaml` to `config.yaml` and fill in parameters.

Initialize Terraform (this will download provider and module):

```shell
terraform init
```

Deploy devices configuration:

```shell
terraform init
terraform plan
terraform apply --auto-approve
```

Once finished, delete configuration:

```shell
terraform destroy --auto-approve
```

Note that this will only destroy configuration that was created by Terraform.

For more information and examples, visit: <https://registry.terraform.io/providers/CiscoDevNet/meraki/latest/docs>

## Upgrade Meraki Terraform provider

To upgrade the latest acceptable version of each provider, use:

```shell
terraform init --upgrade
```

## Debug

You need to specify those two commands before running TF:

```shell
export TF_LOG_PATH=file.log
export TF_LOG=TRACE
```

This will save logs to file.log in the folder where you run terraform.
