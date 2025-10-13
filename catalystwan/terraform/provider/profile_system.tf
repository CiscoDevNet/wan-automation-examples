
# SYSTEM PROFILE

resource "sdwan_system_feature_profile" "System_Profile" {
  name        = "TFP_system"
  description = "Terraform system feature profile 1"

}

# ASSOCIATED PARCELS

resource "sdwan_system_global_feature" "example" {
  name                 = "TFP_Global_Parcel"
  description          = "Terraform generated Global parcel"
  feature_profile_id   = sdwan_system_feature_profile.System_Profile.id
  http_server          = false
  https_server         = false
  ftp_passive          = false
  domain_lookup        = false
  arp_proxy            = false
  rsh_rcp              = false
  line_vty             = false
  cdp                  = true
  lldp                 = true
  source_interface     = "GigabitEthernet1"
  tcp_keepalives_in    = true
  tcp_keepalives_out   = true
  tcp_small_servers    = false
  udp_small_servers    = false
  console_logging      = true
  ip_source_routing    = false
  vty_line_logging     = false
  snmp_ifindex_persist = true
  ignore_bootp         = true
  nat64_udp_timeout    = 300
  nat64_tcp_timeout    = 3600
  http_authentication  = "aaa"
  ssh_version          = "2"
}

resource "sdwan_system_aaa_feature" "aaa_parcel" {
  name                 = "TFP_AAA_Parcel"
  description          = "Terraform AAA parcel example"
  feature_profile_id   = sdwan_system_feature_profile.System_Profile.id
  authentication_group = true
  accounting_group     = true
  server_auth_order    = ["local"]

  users = [
    {
      name      = "jmb"
      password  = "cisco123"
      privilege = "15"
      public_keys = [
        {
          key_string = "AAAAB3NzaC1yc2"
          key_type   = "ssh-rsa"
        }
      ]
    }
  ]
}

resource "sdwan_system_banner_feature" "banner_parcel" {
  name               = "TFP_Banner_Parcel"
  feature_profile_id = sdwan_system_feature_profile.System_Profile.id
  description        = "Terraform Banner parcel example"
  login              = "Welcome to the SD-WAN network. Authorized access only."
  motd               = "SD-WAN Lab"
}

resource "sdwan_system_basic_feature" "basic_parcel" {
  name                       = "TFP_Basic_Parcel"
  description                = "Terraform Basic parcel"
  feature_profile_id         = sdwan_system_feature_profile.System_Profile.id
  timezone                   = "UTC"
  config_description         = "example"
  location                   = local.config.system.location
  gps_longitude              = local.config.system.gps_longitude
  gps_latitude               = local.config.system.gps_latitude
  max_omp_sessions           = 24
  on_demand_enable           = true
  on_demand_idle_timeout     = 10
  affinity_group_number      = 1
  affinity_group_preferences = [1]
  affinity_preference_auto   = false
  affinity_per_vrfs = [
    {
      affinity_group_number = 1
      vrf_range             = "123-456"
    }
  ]
}

resource "sdwan_system_logging_feature" "logging_parcel" {
  name               = "TFP_Logging_Parcel"
  description        = "Terraform generated logging parcel"
  feature_profile_id = sdwan_system_feature_profile.System_Profile.id
  disk_enable        = true
  disk_file_size     = 9
  disk_file_rotate   = 10
  tls_profiles = [
    {
      profile       = "test"
      tls_version   = "TLSv1.1"
      cipher_suites = ["aes-128-cbc-sha"]
    }
  ]
  ipv4_servers = [
    {
      hostname_ip                   = "1.1.1.1"
      vpn                           = 0
      source_interface              = "GigabitEthernet1"
      priority                      = "informational"
      tls_enable                    = true
      tls_properties_custom_profile = true
      tls_properties_profile        = "test"
    }
  ]
}

resource "sdwan_system_omp_feature" "example" {
  name                        = "TFP_OMP_Parcel"
  description                 = "Terraform generated OMP Parcel"
  feature_profile_id          = sdwan_system_feature_profile.System_Profile.id
  graceful_restart            = true
  overlay_as                  = 10
  paths_advertised_per_prefix = 4
  ecmp_limit                  = 4
  shutdown                    = false
  omp_admin_distance_ipv4     = 10
  omp_admin_distance_ipv6     = 20
  advertisement_interval      = 1
  graceful_restart_timer      = 43200
  eor_timer                   = 300
  holdtime                    = 60
  advertise_ipv4_bgp          = false
  advertise_ipv4_ospf         = false
  advertise_ipv4_ospf_v3      = false
  advertise_ipv4_connected    = false
  advertise_ipv4_static       = false
  advertise_ipv4_eigrp        = false
  advertise_ipv4_lisp         = false
  advertise_ipv4_isis         = false
  advertise_ipv6_bgp          = true
  advertise_ipv6_ospf         = true
  advertise_ipv6_connected    = true
  advertise_ipv6_static       = true
  advertise_ipv6_eigrp        = true
  advertise_ipv6_lisp         = true
  advertise_ipv6_isis         = true
  ignore_region_path_length   = false
  transport_gateway           = "prefer"
  site_types                  = ["type-1"]
}

resource "sdwan_system_bfd_feature" "example" {
  name               = "TFP_BFD_Parcel"
  description        = "Terraform BFD Parcel"
  feature_profile_id = sdwan_system_feature_profile.System_Profile.id
  multiplier         = 3
  poll_interval      = 100
  default_dscp       = 8
  colors = [
    {
      color          = "3g"
      hello_interval = 200
      multiplier     = 3
      pmtu_discovery = true
      dscp           = 16
    }
  ]
}

# resource "sdwan_system_mrf_feature" "mrf_parcel" {
#   name                    = "TFP_MRF_Parcel"
#   description             = "Terraform MRF parcel example"
#   feature_profile_id      = sdwan_system_feature_profile.System_Profile.id
#   region_id               = local.config.mrf.region_id
#   role                    = local.config.mrf.role
#   enable_migration_to_mrf = "enabled"
#   migration_bgp_community = 100
# }
