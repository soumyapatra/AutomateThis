terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//node-group"
}

locals {
      # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  regional_vars = read_terragrunt_config(find_in_parent_folders("regional.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project.hcl"))

  # Extract out common variables for reuse
  key_pair_name = local.environment_vars.locals.key_pair_name
  instance_type = local.common_vars.locals.instance_type
  aws_region = local.regional_vars.locals.aws_region
  region_prefix_map = local.common_vars.locals.region_prefix_map
  region_prefix = local.region_prefix_map[local.aws_region]
  project_name = local.project_vars.locals.project_name
  project_prefix = local.common_vars.locals.project_prefix_map[local.project_name]
  env = local.environment_vars.locals.environment
  component = "ng"
  name = join("-", compact([local.region_prefix, local.component, local.project_prefix, local.env]))
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

dependency "eks" {
  config_path = "../eks"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    endpoint = "fake-eks-endpoint"
    cert_auth_data = "SGVsbG8gV29ybGQ="
    name = "fake-name"
  }
}

dependency "auth_config" {
  config_path = "../auth_config"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    ng_role_arn = "ng-role-arn"
  }
}

inputs = {
  name = "${local.name}"
  eks_cluster_name = dependency.eks.outputs.name
  private_subnets = dependency.vpc.outputs.private_subnets
  key_pair_name = "${local.key_pair_name}"
  instance_type = "${local.instance_type}"
  ng_role_arn = dependency.auth_config.outputs.ng_role_arn
}

