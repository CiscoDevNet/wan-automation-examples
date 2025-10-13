
# SERVICE PROFILE

resource "sdwan_service_feature_profile" "Service_Profile" {
  name        = "TFP_Service_Profile"
  description = "Terraform service feature profile"
}


# ASSOCIATED PARCELS

resource "sdwan_service_lan_vpn_feature" "Service_VPN_feature" {
  name                       = "TFP_Service_VPN"
  description                = "Terraform Service VPN feature"
  feature_profile_id         = sdwan_service_feature_profile.Service_Profile.id
  vpn                        = local.config.service.vpn_number
  config_description         = local.config.service.vpn_name
  omp_admin_distance_ipv4    = 1
  omp_admin_distance_ipv6    = 1
  enable_sdwan_remote_access = false
  primary_dns_address_ipv4   = local.config.service.primary_dns_address_ipv4
  secondary_dns_address_ipv4 = local.config.service.secondary_dns_address_ipv4
  ipv4_static_routes = [
    {
      network_address = "0.0.0.0"
      subnet_mask     = "0.0.0.0"
      gateway         = "nextHop"
      next_hops = [
        {
          address                 = "172.16.1.1"
          administrative_distance = 1
        }
      ]
    }
  ]
  # ipv6_static_routes = [
  #   {
  #     prefix  = "2001:0:0:1::0/12"
  #     gateway = "nextHop"
  #     next_hops = [
  #       {
  #         address                 = "2001:0:0:1::0"
  #         administrative_distance = 1
  #       }
  #     ]
  #   }
  # ]
}

resource "sdwan_service_lan_vpn_interface_ethernet_feature" "Service_VPN_Ethernet_Feature" {
  name                       = "TF_VPN_Interface"
  description                = "Terraform VPN Interface"
  feature_profile_id         = sdwan_service_feature_profile.Service_Profile.id
  service_lan_vpn_feature_id = sdwan_service_lan_vpn_feature.Service_VPN_feature.id
  shutdown                   = false
  interface_name             = local.config.service.interface_name
  interface_description      = "Loopback for service VPN"
  ipv4_address               = local.config.service.interface_ip_address
  ipv4_subnet_mask           = local.config.service.interface_ip_mask
  ipv4_nat                   = false
  ipv4_nat_type              = "pool"
  ipv4_nat_range_start       = "1.2.3.4"
  ipv4_nat_range_end         = "4.5.6.7"
  ipv4_nat_prefix_length     = 1
  ipv4_nat_overload          = true
  ipv4_nat_loopback          = "123"
  ipv4_nat_udp_timeout       = 123
  ipv4_nat_tcp_timeout       = 123
  static_nats = [
    {
      source_ip    = "1.2.3.4"
      translate_ip = "2.3.4.5"
      direction    = "inside"
      source_vpn   = 0
    }
  ]
  ipv6_nat = true
  nat64    = false

}
