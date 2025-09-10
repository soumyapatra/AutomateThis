remote_state {
  backend = "azurerm"
  generate = {
    path      = "backend.tf"
    if_exists = "overwrite_terragrunt"
  }
  config = {
    resource_group_name  = "terraform_dev_rg"
    storage_account_name = "terraformdevtfstatestacc"
    container_name       = "terraformtfstatecontainer"
    key                  = "terraform_state/${path_relative_to_include()}/terraform.tfstate"

  }
}

# Generate provider.tf
generate "provider" {
  path      = "provider.tf"
  if_exists = "overwrite_terragrunt"
  contents  = <<EOF
provider "azurerm" {
  features {}

  # Optional: pin provider version
  # version = "=3.108.0"
}
terraform {
  required_providers {
    azurerm = {
      source  = "hashicorp/azurerm"
      version = ">= 3.0.0"
    }
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
  region_vars = read_terragrunt_config(find_in_parent_folders("regional_vars.hcl"))
  environment_vars = read_terragrunt_config(find_in_parent_folders("env_vars.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project_vars.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common_vars.hcl"))
}

inputs = merge(
  local.region_vars.locals,
  local.environment_vars.locals,
  local.project_vars.locals,
)
