terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//network"
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
  rg_name = join("-", compact([local.project_name, local.region, local.env, "RG"]))
  vnet_name = join("-", compact([local.project_name, local.region, local.env, "VNET"]))
  network_cidr = local.env_vars.locals.network_cidr
  public_subnet_count = local.common_vars.locals.public_subnet_count
  private_subnet_count = local.common_vars.locals.private_subnet_count

}

inputs = {
    rg_name = local.rg_name
    location = local.region
    vnet_name = local.vnet_name
    network_cidr = local.network_cidr
    public_subnet_count = local.public_subnet_count
    private_subnet_count = local.private_subnet_count
}
