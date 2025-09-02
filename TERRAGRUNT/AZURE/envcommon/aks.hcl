terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//aks"
}

locals {
  # Automatically load environment-level variables
  env_vars = read_terragrunt_config(find_in_parent_folders("env_vars.hcl"))
  regional_vars = read_terragrunt_config(find_in_parent_folders("regional_vars.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common_vars.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project_vars.hcl"))

  project_name = local.project_vars.locals.project_name
  region = local.regional_vars.locals.region_code
  env = local.env_vars.locals.env_name
  aks_name = join("-", compact([local.project_name, local.region, local.env, "AKS"]))
  dns_prefix = join("-", compact([local.project_name, local.region, local.env]))
  network_cidr = local.env_vars.locals.network_cidr
  kubernetes_version = local.common_vars.locals.kubernetes_version
  node_count = local.common_vars.locals.node_count
  vm_size = local.common_vars.locals.vm_size

}
dependency "network" {
  config_path = "../network"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    vpc_id = "fake-vpc-id"
    bastion_sg_id = "fake-sg-id"
  }
}

#dependency "eks" {
#  config_path = "../eks"
#
#  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
#  # module hasn't been applied yet.
#  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
#  mock_outputs = {
#    eks_sg_id = "sg-fakeid"
#  }
#}

inputs = {
  resource_group_name = dependency.network.outputs.rg_name
  location = dependency.network.outputs.location
  private_subnet_ids = dependency.network.private_subnet_ids
  dns_prefix = local.dns_prefix
  aks_name = local.aks_name
  kubernetes_version = local.kubernetes_version
  node_count = local.node_count
  vm_size = local.vm_size
}
