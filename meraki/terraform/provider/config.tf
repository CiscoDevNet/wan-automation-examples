# PARAMETERS

variable "config_file" {
  default = "config.yaml"
}

locals {
  yaml_content = file(var.config_file)
  config       = yamldecode(local.yaml_content)
}
