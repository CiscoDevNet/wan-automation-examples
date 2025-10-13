terraform {
  required_providers {
    sdwan = {
      source = "CiscoDevNet/sdwan"
    }
  }
}

provider "sdwan" {
  username = local.config.manager.username
  password = local.config.manager.password
  url      = local.config.manager.url
}
