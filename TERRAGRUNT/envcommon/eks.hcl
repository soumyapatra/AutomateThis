terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//eks"
}

locals {
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  regional_vars = read_terragrunt_config(find_in_parent_folders("regional.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project.hcl"))

  # Extract out common variables for reuse
  aws_region = local.regional_vars.locals.aws_region
  region_prefix_map = local.common_vars.locals.region_prefix_map
  region_prefix = local.region_prefix_map[local.aws_region]
  project_name = local.project_vars.locals.project_name
  project_prefix = local.common_vars.locals.project_prefix_map[local.project_name]
  env = local.environment_vars.locals.environment
  component = "eks"
  name = join("-", compact([local.region_prefix, local.component, local.project_prefix, local.env]))
  eks_version = local.common_vars.locals.eks_version
}
dependency "vpc" {
  config_path = "../vpc"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    vpc_id = "fake-vpc-id"
    private_subnets = ["fake-subnet-1","fake-subnet-2"]
  }
}
dependency "sg" {
  config_path = "../sg"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    master_sg_id = "fake-sg-id"
  }
}

inputs = {
    name = "${local.name}"
    sg_id = ["${dependency.sg.outputs.master_sg_id}"]
    subnets = dependency.vpc.outputs.private_subnets
    eks_version = local.eks_version
}
