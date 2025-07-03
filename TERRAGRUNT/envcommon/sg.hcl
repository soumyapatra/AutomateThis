terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//sg"
}

locals {
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  regional_vars = read_terragrunt_config(find_in_parent_folders("regional.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project.hcl"))

  # Extract out common variables for reuse
  env = local.environment_vars.locals.environment
  aws_region = local.regional_vars.locals.aws_region
  region_prefix_map = local.common_vars.locals.region_prefix_map
  region_prefix = local.region_prefix_map[local.aws_region]
  project_name = local.project_vars.locals.project_name
  project_prefix = local.common_vars.locals.project_prefix_map[local.project_name]
  component = "sg"
  service_name = local.common_vars.locals.service_name
  name = join("-", compact([local.region_prefix, local.component, local.project_prefix, local.env]))
  bastion_public_ip_list = local.common_vars.locals.bastion_public_ip_list
  prod_sg_id = try(local.environment_vars.locals.prod_sg_id, local.common_vars.locals.prod_sg_id)
  prod_sg = try(local.environment_vars.locals.prod_sg, local.common_vars.locals.prod_sg)
}
dependency "vpc" {
  config_path = "../vpc"

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
    vpc_id = dependency.vpc.outputs.vpc_id
    bastion_sg_id = dependency.vpc.outputs.bastion_sg_id
    name = "${local.name}"
    bastion_public_ip_list = local.bastion_public_ip_list
    prod_sg_id = local.prod_sg_id
    prod_sg = local.prod_sg
#    eks_sg_id = local.eks_sg_id
}
