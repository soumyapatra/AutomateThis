terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//cluster-autoscaler"
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
}

dependency "eks" {
  config_path = "../eks"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    eks_endpoint = "fake-eks-endpoint"
    name = "fake-name"
    cert_auth_data = "fake-cert_auth_data"
    helmconfig = {
    host  = "fake-host"
    token = "fake-token"
    ca    = "SGVsbG8gV29ybGQ="
  }
    oidc = {
      url = "fake-url"
      arn = "fake-urn"
    }
  }
}

dependency "asg" {
  config_path = "../asg"
  skip_outputs = true
}

dependency "auth_config" {
  config_path = "../auth_config"
  skip_outputs = true
}


inputs = {
  eks_name = dependency.eks.outputs.name
  cluster_name = "${local.name}"
  oidc         = dependency.eks.outputs.oidc
  tags         = { env = "${local.env}" }
  eks_host     = dependency.eks.outputs.helmconfig.host
  eks_token    = dependency.eks.outputs.helmconfig.token
  eks_ca       = dependency.eks.outputs.helmconfig.ca
}
