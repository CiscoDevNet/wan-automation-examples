terraform {
  required_providers {
    meraki = {
      source  = "ciscodevnet/meraki"
     }
  }
}

provider "meraki" {
  # api_key = local.config.meraki.management.api_key
}