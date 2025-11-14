terraform {
  required_providers {
    meraki = {
      source = "CiscoDevNet/meraki"
    }
  }
}

provider "meraki" {
}

module "meraki" {
  # source = "netascode/nac-sdwan/sdwan"
  source = "git::https://github.com/netascode/terraform-meraki-nac-meraki.git?ref=main"
  # version = "0.5.0"

  yaml_directories = ["data/"]

  write_default_values_file = "defaults.yaml"

}
