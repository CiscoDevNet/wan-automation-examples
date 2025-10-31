# Organization Level

resource "meraki_organization" "Meraki_Organization" {
  name = local.config.organization.name
  management_details = []
}