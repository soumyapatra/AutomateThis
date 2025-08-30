terraform {
  source = "${get_parent_terragrunt_dir()}/../modules//vpc"
}


locals {
  # Automatically load environment-level variables
  environment_vars = read_terragrunt_config(find_in_parent_folders("env.hcl"))
  regional_vars = read_terragrunt_config(find_in_parent_folders("regional.hcl"))
  common_vars = read_terragrunt_config(find_in_parent_folders("common.hcl"))
  project_vars = read_terragrunt_config(find_in_parent_folders("project.hcl"))


  aws_region = local.regional_vars.locals.aws_region
  region_prefix_map = local.common_vars.locals.region_prefix_map
  region_prefix = local.region_prefix_map[local.aws_region]
  project_name = local.project_vars.locals.project_name
  project_prefix = local.common_vars.locals.project_prefix_map[local.project_name]
  env = local.environment_vars.locals.environment
  component = "vpc"
  service_name = local.common_vars.locals.service_name
  name = join("-", compact([local.region_prefix, local.component, local.project_prefix, local.env]))
  eks_cluster_name = join("-", compact([local.region_prefix, "eks", local.project_prefix, local.env]))
  key_pair_name = local.environment_vars.locals.key_pair_name

  # Extract out common variables for reuse
  create_vpc = local.environment_vars.locals.create_vpc
  vpc_id = local.environment_vars.locals.vpc_id
  azs = local.regional_vars.locals.azs
  cidr = local.environment_vars.locals.cidr
  owner = local.common_vars.locals.owner
  sec_cidr = local.environment_vars.locals.secondary_cidr
  create_igw = local.environment_vars.locals.create_igw
  igw_id = local.environment_vars.locals.igw_id
  bastion_host = try(local.environment_vars.locals.bastion_host, local.common_vars.locals.bastion_host)
  enable_dns_hostnames = try(local.environment_vars.locals.enable_dns_hostnames, local.common_vars.locals.enable_dns_hostnames)
}

inputs = {
  name = "${local.name}"
  cidr = local.cidr
  secondary_cidr_blocks = local.sec_cidr
  one_nat_gateway_per_az = true
  enable_nat_gateway = true
  create_igw = local.create_igw
  igw_id = local.igw_id
  private_subnet_tags = {
    "kubernetes.io/cluster/${local.eks_cluster_name}" = "shared",
    "kubernetes.io/role/internal-elb" = "1"
  }
  azs = local.azs
  public_subnet_tags = {
    "kubernetes.io/cluster/${local.eks_cluster_name}" = "shared",
    "kubernetes.io/role/elb" = "1"
  }
  create_vpc = local.create_vpc
  vpc_id = local.vpc_id
  key_pair_name = local.key_pair_name

  tags = {
    Owner       = local.owner
    Environment = local.env
  }

  vpc_tags = {
    Name = "${local.name}"
    "kubernetes.io/cluster/${local.name}" = "shared"
  }
  bastion_host = local.bastion_host
  enable_dns_hostnames = local.enable_dns_hostnames
  aws_region_code = local.aws_region
  eks_cluster_name = local.eks_cluster_name
}
