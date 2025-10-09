# SD-WAN Terraform Examples

This folder provides Terraform examples for interacting with Cisco Catalyst SD-WAN Manager APIs,
using the SD-WAN Terraform Provider as well as the SD-WAN Terraform modules for even better abstraction.

Please note these examples are for demonstration purposes only and not production-ready.

## Overview

When working with Cisco Catalyst SD-WAN Manager APIs using Terraform, you have two primary approaches: directly leveraging the CiscoDevNet/sdwan provider or utilizing the higher-level netascode/nac-sdwan/sdwan module. Both serve the purpose of automating SD-WAN configurations, but they operate at different levels of abstraction.

### SD-WAN Terraform Provider

The CiscoDevNet/sdwan Terraform Provider:

- [Terraform Registry](https://registry.terraform.io/providers/CiscoDevNet/sdwan/latest)
- [Github Repository](https://github.com/CiscoDevNet/terraform-provider-sdwan)

**What it is:**

A Terraform provider is a plugin that Terraform uses to interact with an API of a specific service or platform. The CiscoDevNet/sdwan provider is the fundamental building block for managing Cisco Catalyst SD-WAN configurations with Terraform. It directly exposes the underlying Catalyst SD-WAN Manager (vManage) APIs as Terraform resources.

**How it works:**

When you use this provider, you define individual SD-WAN components (like VPNs, policies, templates, devices) as distinct Terraform resources. Each resource in your .tf files directly maps to an API call to SD-WAN Manager. This approach gives you granular control over every aspect of your SD-WAN configuration.

**Use Case:**

This option is ideal for users who need fine-grained control, want to manage specific SD-WAN objects directly, or are integrating with existing automation workflows that require direct API interaction. It's also the foundation upon which higher-level modules are built.

### SD-WAN Terraform Module

The netascode/nac-sdwan/sdwan Terraform Module:

- [Terraform Registry](https://registry.terraform.io/modules/netascode/nac-sdwan/sdwan/latest)
- [Github Repository](https://github.com/netascode/terraform-sdwan-nac-sdwan)
- [Github - Pre-deployment validation tool](https://github.com/netascode/iac-validate)

**What it is:**

A Terraform module is a container for multiple resources that are used together. The netascode/nac-sdwan/sdwan module provides a higher level of abstraction over the CiscoDevNet/sdwan provider. It's designed to simplify complex SD-WAN configurations by allowing you to define your desired state using YAML configuration files.

**How it works:**

Instead of defining each individual resource (e.g., a VPN, then an interface, then a policy attachment) separately in HCL (Terraform's language), this module allows you to describe your entire SD-WAN intent in a more human-readable YAML format. The module then takes this YAML input, translates it into the necessary CiscoDevNet/sdwan provider resources, and provisions them on SD-WAN Manager. This approach often reduces the amount of boilerplate HCL code you need to write.

**Use Case:**

This option is excellent for users who prefer a more declarative, "intent-based" approach to SD-WAN configuration. It's particularly useful for quickly deploying common SD-WAN patterns, managing configurations from a single YAML source, and simplifying the overall Terraform code for complex deployments. It abstracts away many of the underlying provider details, making it easier to manage the entire SD-WAN fabric.

## Folders

- `provider`: example leveraging CiscoDevNet/sdwan Terraform Provider:
- `model`: example leveraging netascode/nac-sdwan/sdwan Terraform Module

## Terraform Model

Go to `model` folder.

Copy `config-example.yaml` to `config.yaml` and fill in parameters.

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

## Terraform Provider

Go to `provider` folder.

Copy `config-example.yaml` to `config.yaml` and fill in parameters.

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

## Upgrade sdwan provider

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

## Resources




