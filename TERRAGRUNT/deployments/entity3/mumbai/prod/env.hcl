locals {
  environment = "prod"
  create_vpc = true
  private_subnets = ["10.121.100.0/22", "10.121.104.0/22", "10.121.108.0/22", "10.121.112.0/22", "10.121.116.0/22"]
  public_subnets = ["10.121.4.0/22", "10.121.8.0/22", "10.121.12.0/22"]
  redis_subnets = ["10.121.16.0/22", "10.121.20.0/22"]
  db_subnets = ["10.121.24.0/22", "10.121.28.0/22"]
  secondary_cidr = []
  cidr="10.121.0.0/16"
  vpc_id = ""
  create_igw = true
  igw_id = ""
  bastion_host = true
  ami_name = ""
  ami_owner_id = "self"
}
