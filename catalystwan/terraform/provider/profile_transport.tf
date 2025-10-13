
# TRANSPORT PROFILE

resource "sdwan_transport_feature_profile" "Transport_Profile" {
  name        = "TFP_Transport_Profile"
  description = "Terraform transport feature profile 1"
}

# VPN0

resource "sdwan_transport_wan_vpn_feature" "VPN0_Feature" {
  name                       = "TFP_VPN0"
  description                = "VPN0"
  feature_profile_id         = sdwan_transport_feature_profile.Transport_Profile.id
  vpn                        = 0
  enhance_ecmp_keying        = true
  primary_dns_address_ipv4   = local.config.transport.primary_dns_address_ipv4
  secondary_dns_address_ipv4 = local.config.transport.secondary_dns_address_ipv4
  # primary_dns_address_ipv6   = "2001:0:0:1::0"
  # secondary_dns_address_ipv6 = "2001:0:0:2::0"
  new_host_mappings = [
    {
      host_name            = "gateway_inet"
      list_of_ip_addresses = [local.config.transport.gateway_inet]
    },
    {
      host_name            = "gateway_mpls"
      list_of_ip_addresses = [local.config.transport.gateway_mpls]
    }
  ]
  ipv4_static_routes = [
    {
      network_address = "0.0.0.0"
      subnet_mask     = "0.0.0.0"
      gateway         = "nextHop"
      next_hops = [
        {
          address                 = local.config.transport.gateway_inet
          administrative_distance = 1
        },
        {
          address                 = local.config.transport.gateway_mpls
          administrative_distance = 1
        }
      ]
    }
  ]
}

# INTERNET TRANSPORT
resource "sdwan_transport_wan_vpn_interface_ethernet_feature" "INET_Transport" {
  name                                           = "TFP_INET_Transport"
  description                                    = "Internet Transport Interface"
  feature_profile_id                             = sdwan_transport_feature_profile.Transport_Profile.id
  transport_wan_vpn_feature_id                   = sdwan_transport_wan_vpn_feature.VPN0_Feature.id
  shutdown                                       = false
  interface_name                                 = local.config.transport.interface_inet_name
  interface_description                          = "INET TRANSPORT"
  ipv4_configuration_type                        = "static"
  ipv4_address                                   = local.config.transport.interface_inet_ip
  ipv4_subnet_mask                               = "255.255.255.0"
  auto_detect_bandwidth                          = true
  tunnel_interface                               = true
  tunnel_interface_carrier                       = "default"
  tunnel_interface_color                         = "biz-internet"
  tunnel_interface_color_restrict                = true
  tunnel_interface_max_control_connections       = 4
  tunnel_interface_vmanage_connection_preference = 8

  tunnel_interface_encapsulations = [
    {
      encapsulation = "ipsec"
      preference    = 100
      weight        = 250
    }
  ]
  nat_ipv4        = true
  nat_type        = "interface"
  nat_udp_timeout = 1
  nat_tcp_timeout = 60
  nat_ipv6        = true
  nat64           = false
  nat66           = true

}

# MPLS TRANSPORT
resource "sdwan_transport_wan_vpn_interface_ethernet_feature" "MPLS_Transport" {
  name                                           = "TFP_MLS_Transport"
  description                                    = "MPLS Transport Interface"
  feature_profile_id                             = sdwan_transport_feature_profile.Transport_Profile.id
  transport_wan_vpn_feature_id                   = sdwan_transport_wan_vpn_feature.VPN0_Feature.id
  shutdown                                       = false
  interface_name                                 = local.config.transport.interface_mpls_name
  interface_description                          = "MPLS TRANSPORT"
  ipv4_configuration_type                        = "static"
  ipv4_address                                   = local.config.transport.interface_mpls_ip
  ipv4_subnet_mask                               = "255.255.255.0"
  auto_detect_bandwidth                          = true
  tunnel_interface                               = true
  tunnel_interface_carrier                       = "default"
  tunnel_interface_color                         = "mpls"
  tunnel_interface_color_restrict                = true
  tunnel_interface_max_control_connections       = 4
  tunnel_interface_vmanage_connection_preference = 8

  tunnel_interface_encapsulations = [
    {
      encapsulation = "ipsec"
      preference    = 200
      weight        = 250
    }
  ]

}
