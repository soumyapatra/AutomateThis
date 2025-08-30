terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//db"
}

locals {
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  regional_vars = read_terragrunt_config(find_in_parent_folders("regional.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project.hcl"))
  service_vars = yamldecode(file(find_in_parent_folders("service_vars.yml")))

  # Extract out common variables for reuse
  aws_region = local.regional_vars.locals.aws_region
  region_prefix_map = local.common_vars.locals.region_prefix_map
  region_prefix = local.region_prefix_map[local.aws_region]
  project_name = local.project_vars.locals.project_name
  project_prefix = local.common_vars.locals.project_prefix_map[local.project_name]
  env = local.environment_vars.locals.environment
  component = "rds"
  name = join("-", compact([local.region_prefix, local.component, local.project_prefix, local.env]))
  service_list = try(local.environment_vars.locals.enabled_services, [])
  domain_name = local.environment_vars.locals.domain_name
}
dependency "vpc" {
  config_path = "../vpc"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    db_subnets = ["fake-subnet-1","fake-subnet-2"]
    vpc_id = "vpc-70405979074"
  }
}

dependency "sg" {
  config_path = "../sg"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    rds_sg_id = "fake-sg-id"
  }
}

dependency "eks" {
  config_path = "../eks"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    eks_sg_id = "sg-fakeid"
  }
}

inputs = {
    service_vars = "${local.service_vars}"
    service_list = "${local.service_list}"
    name = "${local.name}"
    db_subnets = dependency.vpc.outputs.db_subnets
    db_sg_id = dependency.sg.outputs.rds_sg_id
    eks_sg_id = dependency.eks.outputs.eks_sg_id
    domain_name = local.domain_name
    vpc_region = local.aws_region
    vpc_id = dependency.vpc.outputs.vpc_id
}

