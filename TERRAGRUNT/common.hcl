locals {
    eks_version = "1.27"
    instance_type = "m5.xlarge"
    ami_name = "amazon-eks-node-1.27-v20231201"
    ami_owner_id = "602401143452"
    bastion_host = false
    bastion_public_ip_list = ["3.7.168.159/32"]
    enable_dns_hostnames = true
    prod_sg = false
    prod_sg_id = "sg-placeholder"
    service_name = "eksnode"
    component = "ec"
    owner = "devops"
    key_pair_name = "hyd-key"
    project_prefix_map = {
        entity1 = "ent1"
        entity3 = "ent2"
        entity3 = "ent3"
      }
    region_prefix_map = {
        ap-south-1 = "mu"
        ap-south-2 = "hyd"
      }
}
