locals {
  environment = "prod"
  create_vpc = true
  profile = "sbox-role"
  private_subnets = ["10.120.100.0/22", "10.120.104.0/22", "10.120.108.0/22"]
  public_subnets = ["10.120.4.0/22", "10.120.8.0/22", "10.120.12.0/22"]
  db_subnets = ["10.120.16.0/22", "10.120.20.0/22", "10.120.24.0/22"]
  redis_subnets = ["10.120.28.0/22", "10.120.32.0/22", "10.120.36.0/22"]
  secondary_cidr = []
  cidr="10.120.0.0/16"
  vpc_id = ""
  create_igw = true
  igw_id = ""
  bastion_host = true
  ami_name = "amazon-eks-node-1.27-v20231201"
  ami_owner_id = "amazon"
  key_pair_name = "hyd-key-sbox"
  domain_name = "internal.xxxxxxx.io"
}
