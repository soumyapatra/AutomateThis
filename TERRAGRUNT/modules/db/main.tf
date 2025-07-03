locals {
  service_params = {
    for service_name in var.service_list :
    service_name => try(var.service_vars["services"][service_name]["rds"], null)
  }
}

module associate_vpc {
  source = "../r53"
  associate_vpc = true
  vpc_region = var.vpc_region
  vpc_id = var.vpc_id
  domain_name = var.domain_name
}

module rds {
  source = "../rds"
  for_each = { for k, v in local.service_params : k => v if v != null }
  db_subnet_group = aws_db_subnet_group.db_subnet.name
  db_instance_identifier = each.value["db_instance_identifier"]
  instance_type = each.value["instance_class"]
  db_sg_id = "${var.db_sg_id}"
  sub_domain_name = each.value["subdomain"]
  domain_name = var.domain_name
  depends_on = [
    aws_db_subnet_group.db_subnet, module.associate_vpc
  ]
}

resource "aws_db_subnet_group" "db_subnet" { 
  name       = "${var.name}_db_subnet_group" 
  subnet_ids = "${var.db_subnets}"
}


resource "aws_security_group_rule" "eks-cluster-ingress-rds" {
  description              = "Allow DB to receive traffic from EKS Cluster"
  from_port                = 3306
  protocol                 = "tcp"
  security_group_id        = var.db_sg_id
  source_security_group_id = var.eks_sg_id
  to_port                  = 3306
  type                     = "ingress"
}
