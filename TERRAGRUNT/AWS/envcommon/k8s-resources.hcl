terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//k8s-resources"
}

locals {
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  env = local.environment_vars.locals.environment
  service_list = try(local.environment_vars.locals.enabled_services, [])
  service_vars = yamldecode(file(find_in_parent_folders("service_vars.yml")))
  regional_vars = read_terragrunt_config(find_in_parent_folders("regional.hcl"))
  aws_region = local.regional_vars.locals.aws_region
}

dependency "eks" {
  config_path = "../eks"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    endpoint = "https://6563D5158CB7725499868.gr7.ap-south-2.eks.amazonaws.com"
    cert_auth_data = "LS0tLS1CRUdJTiBDRVJUSUZJQ0FURS0tLS0tCk1JSURCVENDQWUyZ0F3SUJBZ0lJZG1ZOWF5VkpjN1l3RFFZSktvWklodmNOQVFFTEJRQXdGVEVUTUJFR0ExVUUKQXhNS2EzVmlaWEp1WlhSbGN6QWVGdzB5TkRBeE1EUXlNREEwTWpGYUZ3MHpOREF4TURFeU1EQTVNakZhTUJVeApFekFSQmdOVkJBTVRDbXQxWW1WeWJtVjBaWE13Z2dFaU1BMEdDU3FHU0liM0RRRUJBUVVBQTRJQkR3QXdnZ0VLCkFvSUJBUUM2S3VyTFMxUTZkckxDRVdOSVZ3YWhkU3Rac0dlTmkvVGdzcmRQNC9wVDM0M3UyTVVYS0JtV0dxdkoKdlZMbkhNb0NqYUhSdGpZdVFYQjA4SVU5b1NDUFFDZ0Y1Z0NwQWNFSlAyWVorM2I4RE00QzNUREVQL3k3dVFDbApiRVp6aHRDZndCVWJVeUg1b1ozVml2a1FFMkdSUGp4eFhzTXdHTjM3c3BEMkZuNUVHb3RnUzVzYzUyTG45S2dUCjhRQ1Z3VFFYMFhqR1ZyTHpEMG1Zb2t5Y2d5WHhQeWZGRkdXclYrR0hkNUlHcEs0aDNOTTVkYWRMTzNVVXdBbUMKb0x0WkpZRWthZE5nbkJ1eGFOc2ZudTlWSE9WZVVQU2JZUm9iKzB5SzRqT095bXg3aVdWd0Rna3pCYU1mZm1FdApGNnBSS25ESXNEZ0ExT1g2N1YwZkZQbldFMWV6QWdNQkFBR2pXVEJYTUE0R0ExVWREd0VCL3dRRUF3SUNwREFQCkJnTlZIUk1CQWY4RUJUQURBUUgvTUIwR0ExVWREZ1FXQkJSVCtoMlFBOE5FZEFYZXMwVnpzc1VQeFgvalN6QVYKQmdOVkhSRUVEakFNZ2dwcmRXSmxjbTVsZEdWek1BMEdDU3FHU0liM0RRRUJDd1VBQTRJQkFRQmRIaE4wOWFGegovMFhKMktKZ0d3dXZ3bFRhYlpjM2tvczJJSFdOZWlYdlAvUm51NlVialhjR3A0ZGR6Z1JjWmorNzNRaUo3eFFKCmhVV2RSZ1lmd1NUTUtWVDFCbjQxV01XM1k4YnA4bEtOOC9BV2hhU0VTRjNKT0J6UElzcnJ1ZFVGNUNjSy9HZUUKYW9uaXhKN3Y2NXd6dzJZWkd2cEVlOXgrSElOTW9SUnlCaTR1MldzTVpiQUhmOXR4Lyt5Q1BCK1VtaWlhYzU3cQpiUVNNeUpnMWJLNHVBaVdIQ1I0TWs5VkpVanpZSTNFdWJvTVpkNWdOWG1CSGw4dER1bEo3TVU5RWdMMU1yYzZrCkJ2Q1c5SWx4SEJ1ZFJnMElMUEUwM28wM0wvaG94YTJ4bWFEZGdUbTlRMWgwRlA1SmZMMGhwR0FHT2R6Skc2VisKVlVIS2FqaXptc1F0Ci0tLS0tRU5EIENFUlRJRklDQVRFLS0tLS0K"
    name = "fake-name"
  }
}

inputs = {
  eks_name = dependency.eks.outputs.name
  eks_endpoint = dependency.eks.outputs.endpoint
  eks_cert_auth_data = dependency.eks.outputs.cert_auth_data
  service_list = "${local.service_list}"
  service_vars = "${local.service_vars}"
  env = "${local.env}"
  region = "${local.aws_region}"
}
