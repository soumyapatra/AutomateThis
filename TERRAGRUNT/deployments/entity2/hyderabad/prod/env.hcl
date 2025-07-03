locals {
  environment = "prod"
  create_vpc = true
  private_subnets = ["10.100.100.0/22", "10.100.104.0/22", "10.100.108.0/22", "10.100.112.0/22", "10.100.116.0/22"]
  public_subnets = ["10.100.4.0/22", "10.100.8.0/22", "10.100.12.0/22"]
  secondary_cidr = []
  cidr="10.100.0.0/16"
  vpc_id = ""
  create_igw = true
  igw_id = ""
  bastion_host = true
  ami_name = ""
  ami_owner_id = "self"
}
