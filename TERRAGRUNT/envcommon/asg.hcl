terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//asg"
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
  component = "asg"
  name = join("-", compact([local.region_prefix, local.component, local.project_prefix, local.env]))
  eks_cluster_name = join("-", compact([local.region_prefix, "eks", local.project_prefix, local.env]))

  # Extract out common variables for reuse
  eks_version = try(local.environment_vars.locals.eks_version, local.common_vars.locals.eks_version)
  instance_type = local.common_vars.locals.instance_type
  desired_asg_size = try(local.environment_vars.locals.desired_asg_size, length(local.regional_vars.locals.azs)+1)
  max_asg_size = try(local.environment_vars.locals.max_asg_size, 2*length(local.regional_vars.locals.azs))
  min_asg_size = try(local.environment_vars.locals.min_asg_size, length(local.regional_vars.locals.azs))
  ami_name = try(local.environment_vars.locals.ami_name, local.common_vars.locals.ami_name)
  ami_owner_id = try(local.environment_vars.locals.ami_owner_id, local.common_vars.locals.ami_owner_id)
}
dependency "vpc" {
  config_path = "../vpc"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    private_subnets = ["fake-subnet-1","fake-subnet-2"]
  }
}
dependency "sg" {
  config_path = "../sg"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    worker_sg_id = "fake-sg-id"
  }
}
dependency "eks" {
  config_path = "../eks"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    endpoint = "fake-eks-endpoint"
    cert_auth_data = "fake-cert_auth_data"
  }
}

inputs = {
    name = "${local.name}"
    eks_cluster_name = "${local.eks_cluster_name}"
    worker_sg_ids = ["${dependency.sg.outputs.worker_sg_id}"]
    subnets = dependency.vpc.outputs.private_subnets
    eks_version = local.eks_version
    instance_type = local.instance_type
    eks_endpoint = dependency.eks.outputs.endpoint
    cert_auth_data = dependency.eks.outputs.cert_auth_data
    desired_asg_size = local.desired_asg_size
    max_asg_size = local.max_asg_size
    min_asg_size = local.min_asg_size
    ami_name = local.ami_name
    ami_owner_id = local.ami_owner_id
}
