remote_state {
  backend = "s3"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    bucket = "BUCKET-NAME"
    key = "terraform_state/${path_relative_to_include()}/terraform.tfstate"
    region         = "ap-south-1"
    profile        = "aws-profile"
    encrypt        = true
    dynamodb_table = "DYNAMODB-TABLE"
    disable_bucket_update = true
  }
}
generate "provider" {
  path = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents = <<EOF
provider "aws" {
  region = "${local.aws_region}"
  profile = "${local.profile}"
}
variable "aws_region" {
  description = "AWS region to create infrastructure in"
  type        = string
}

terraform {
  #required_version = ">= 0.13"
  required_providers {
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = ">= 1.7.0"
    }
    helm = {
      version = "<=2.4.0"
    }
  }
}
EOF
}
locals {

  # Automatically load region-level variables
  region_vars = read_terragrunt_config(find_in_parent_folders("regional.hcl"))
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  aws_region   = local.region_vars.locals.aws_region
  profile = local.environment_vars.locals.profile

}

#terraform {
#  extra_arguments "region_vars" {
#    commands = get_terraform_commands_that_need_vars()
#    optional_var_files = [
#      find_in_parent_folders("regional.tfvars"),
#      find_in_parent_folders("env.tfvars"),
#    ]
#  }
#}
inputs = merge(
  local.region_vars.locals,
  local.environment_vars.locals,
  local.project_vars.locals,
)

