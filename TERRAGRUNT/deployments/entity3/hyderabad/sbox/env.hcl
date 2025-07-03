locals {
  environment = "sbox"
  create_vpc = true
  profile = "sbox-role"
  private_subnets = ["10.122.100.0/22", "10.122.104.0/22", "10.122.108.0/22"]
  public_subnets = ["10.122.4.0/22", "10.122.8.0/22", "10.122.12.0/22"]
  db_subnets = ["10.122.16.0/22", "10.122.20.0/22", "10.122.24.0/22"]
  redis_subnets = ["10.122.28.0/22", "10.122.32.0/22", "10.122.36.0/22"]
  secondary_cidr = []
  cidr="10.122.0.0/16"
  vpc_id = ""
  create_igw = true
  igw_id = ""
  bastion_host = true
  ami_name = "amazon-eks-node-1.27-v20231221"
  ami_owner_id = "amazon"
  key_pair_name = "hyd-key-sbox"
  domain_name = "internal.xxxxxxxxxxx.io"
  enabled_services = ["urlshortener"]
}
