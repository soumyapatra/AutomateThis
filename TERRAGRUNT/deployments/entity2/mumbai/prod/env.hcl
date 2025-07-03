locals {
  environment = "prod"
  create_vpc = true
  private_subnets = ["10.101.100.0/22", "10.101.104.0/22", "10.101.108.0/22", "10.101.112.0/22", "10.101.116.0/22"]
  public_subnets = ["10.101.4.0/22", "10.101.8.0/22", "10.101.12.0/22"]
  secondary_cidr = []
  cidr="10.101.0.0/16"
  vpc_id = ""
  create_igw = true
  igw_id = ""
  bastion_host = true
  ami_name = ""
  ami_owner_id = "self"
}
