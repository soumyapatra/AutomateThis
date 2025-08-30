terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//r53"
}

locals {
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  regional_vars = read_terragrunt_config(find_in_parent_folders("regional.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project.hcl"))

  # Extract out common variables for reuse
  domain_name = local.environment_vars.locals.domain_name
  aws_region = local.regional_vars.locals.aws_region
}

dependency "db" {
  config_path = "../db"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    rds_dns_name = ["rds-dns-name.com"]
  }
}




dependency "vpc" {
  config_path = "../vpc"

  # Configure mock outputs for the `validate` command that are returned when there are no outputs available (e.g the
  # module hasn't been applied yet.
  mock_outputs_allowed_terraform_commands = ["validate","plan","init"]
  mock_outputs = {
    vpc_id = "vpc-70405979074"
  }
}



inputs = {
    sub_domain_name = "hyd-rds-urlshortener-sbox123"
    alias_domain_name = dependency.db.outputs.rds_dns_name[0]
    domain_name = local.domain_name
    vpc_region = local.aws_region
    vpc_id = dependency.vpc.outputs.vpc_id
}

