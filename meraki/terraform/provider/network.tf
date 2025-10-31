# Network Level

resource "meraki_network" "Meraki_Network" {
  organization_id = meraki_organization.Meraki_Organization.id
  name            = local.config.organization.network.name
  time_zone       = local.config.organization.network.time_zone
  product_types   = local.config.organization.network.product_types
}