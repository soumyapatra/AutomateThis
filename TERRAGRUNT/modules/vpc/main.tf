locals {
  max_subnet_length = max(
    length(var.private_subnets),
    length(var.public_subnets)
  )
  nat_gateway_count = var.single_nat_gateway ? 1 : var.one_nat_gateway_per_az ? length(var.azs) : local.max_subnet_length
  # Use `local.vpc_id` to give a hint to Terraform that subnets should be deleted before secondary CIDR blocks can be free!
  vpc_id = try(aws_vpc.this[0].id, var.vpc_id)
  igw_id = try(aws_internet_gateway.this[0].id, var.igw_id)
  time_wait_sec = length(var.secondary_cidr_blocks) == 0 ? "0s" : "60s"
  create_vpc = var.create_vpc
  bastion_required = var.bastion_host
}

#Bastion SG

resource "aws_security_group" "bastion" {
  name        = "${var.name}-bastion"
  description = "SG for bastion node"
  vpc_id      = local.vpc_id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = var.name
  }
}

resource "aws_security_group_rule" "bastion-ingress-ssh" {
  cidr_blocks       = ["3.7.168.159/32"]
  description       = "Allow SSH"
  from_port         = 22
  protocol          = "tcp"
  security_group_id = aws_security_group.bastion.id
  to_port           = 22
  type              = "ingress"
}

#Bastion AMI

#data "aws_ami" "bastion" {
#  most_recent = true
#  filter {
#    name   = "name"
#    values = ["bastion02-AMI"]
#  }
#
#  owners = ["self"]
#}

data "aws_ami" "bastion" {
  filter {
    name   = "name"
    values = ["amazon-eks-node-1.27-v20231201"]
  }
  most_recent = true
#  owners      = ["602401143452"] # Amazon EKS AMI Account ID
  owners      = ["amazon"] # Amazon EKS AMI Account ID for Hyderabad region
}

#Bastion Instance

resource "aws_iam_policy" "policy1" {
  name        = "${var.name}-bastion-eks-policy"
  path        = "/"
  description = "Policy to provide EKS permission to EC2"
  policy = jsonencode(
{
	"Version": "2012-10-17",
	"Statement": [
		{
			"Sid": "VisualEditor0",
			"Effect": "Allow",
			"Action": [
				"eks:UpdateClusterVersion",
				"eks:ListEksAnywhereSubscriptions",
				"eks:DescribeFargateProfile",
				"eks:CreatePodIdentityAssociation",
				"eks:ListTagsForResource",
				"eks:DescribeInsight",
				"eks:ListAccessEntries",
				"eks:ListAddons",
				"eks:UpdateClusterConfig",
				"eks:DescribeEksAnywhereSubscription",
				"eks:DescribeAddon",
				"eks:UpdateNodegroupVersion",
				"eks:ListAssociatedAccessPolicies",
				"eks:DescribeNodegroup",
				"eks:ListUpdates",
				"eks:DescribeAddonVersions",
				"eks:DeletePodIdentityAssociation",
				"eks:ListIdentityProviderConfigs",
				"eks:CreateCluster",
				"eks:ListNodegroups",
				"eks:DescribeAddonConfiguration",
				"eks:UntagResource",
				"eks:UpdateAccessEntry",
				"eks:DescribeAccessEntry",
				"eks:RegisterCluster",
				"eks:DeregisterCluster",
				"eks:DescribePodIdentityAssociation",
				"eks:DeleteCluster",
				"eks:ListInsights",
				"eks:ListPodIdentityAssociations",
				"eks:ListFargateProfiles",
				"eks:DescribeIdentityProviderConfig",
				"eks:DeleteAddon",
				"eks:DeleteNodegroup",
				"eks:DescribeUpdate",
				"eks:DisassociateAccessPolicy",
				"eks:TagResource",
				"eks:AccessKubernetesApi",
				"eks:UpdateNodegroupConfig",
				"eks:DescribeCluster",
				"eks:ListClusters",
				"eks:ListAccessPolicies"
			],
			"Resource": "*"
		}
	]
}
)
}

resource "aws_iam_role" "bastion_role" {
  name = "${var.name}_bastion_iam_role"

  assume_role_policy = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Principal": {
        "Service": "ec2.amazonaws.com"
      },
      "Action": "sts:AssumeRole"
    }
  ]
}
EOF
}

resource "aws_iam_role_policy_attachment" "attachment1" {
  role       = aws_iam_role.bastion_role.name
  policy_arn = aws_iam_policy.policy1.arn
}

resource "aws_iam_instance_profile" "ec2_profile" {
  name = "${var.name}_bastion_instance_profile"
  role = aws_iam_role.bastion_role.name
}



resource "aws_instance" "bastion" {
  count = local.bastion_required ? 1 : 0
  ami           = data.aws_ami.bastion.id
  instance_type = "t3.medium"
  subnet_id = aws_subnet.public[0].id
  associate_public_ip_address = true
  iam_instance_profile = aws_iam_instance_profile.ec2_profile.name
  user_data = <<-EOT
#!/bin/bash
curl -O https://s3.us-west-2.amazonaws.com/amazon-eks/1.27.7/2023-11-14/bin/linux/amd64/kubectl
chmod +x kubectl
sudo mv kubectl /usr/local/bin/
sudo yum install telnet bind-utils bash-completion vim -y
echo 'source <(kubectl completion bash)' >>~/.bashrc
echo 'alias k=kubectl' >>~/.bashrc
echo 'complete -o default -F __start_kubectl k' >>~/.bashrc
  EOT
  key_name = "${var.key_pair_name}"
  tags = {
    Name = "${var.name}_bastion"
  }
  root_block_device {
    encrypted   = true
  }
  vpc_security_group_ids = [aws_security_group.bastion.id]
#  iam_instance_profile = ""
}


resource "aws_vpc" "this" {
  count = local.create_vpc ? 1 : 0

  cidr_block                       = var.cidr
  enable_dns_hostnames             = var.enable_dns_hostnames
  enable_dns_support               = var.enable_dns_support
  tags = merge(
    { "Name" = var.name },
    var.tags,
    var.vpc_tags,
  )
}

resource "aws_vpc_ipv4_cidr_block_association" "this" {
  count = length(var.secondary_cidr_blocks) > 0 ? length(var.secondary_cidr_blocks) : 0

  # Do not turn this into `local.vpc_id`
  vpc_id = local.vpc_id

  cidr_block = element(var.secondary_cidr_blocks, count.index)
}

resource "time_sleep" "wait_for_cidr_association" {
  create_duration = local.time_wait_sec
  depends_on = [aws_vpc_ipv4_cidr_block_association.this]
}

resource "aws_subnet" "private" {
  count = length(var.private_subnets) > 0 ? length(var.private_subnets) : 0

  vpc_id                          = local.vpc_id
  cidr_block                      = var.private_subnets[count.index]
  availability_zone               = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  tags = merge(
    {
      "Name" = format(
        "${var.name}-${var.private_subnet_suffix}-%s",
        element(var.azs, count.index),
      )
    },
    var.tags,
    var.private_subnet_tags,
  )
  depends_on = [time_sleep.wait_for_cidr_association]
}

resource "aws_subnet" "public" {
  count = length(var.public_subnets) > 0 ? length(var.public_subnets) : 0

  vpc_id                          = local.vpc_id
  cidr_block                      = var.public_subnets[count.index]
  availability_zone               = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  tags = merge(
    {
      "Name" = format(
        "${var.name}-${var.public_subnet_suffix}-%s",
        element(var.azs, count.index),
      )
    },
    var.tags,
    var.public_subnet_tags,
  )
  depends_on = [time_sleep.wait_for_cidr_association]
}

resource "aws_subnet" "db" {
  count = length(var.db_subnets) > 0 ? length(var.db_subnets) : 0

  vpc_id                          = local.vpc_id
  cidr_block                      = var.db_subnets[count.index]
  availability_zone               = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  tags = merge(
    {
      "Name" = format(
        "${var.name}-${var.db_subnet_suffix}-%s",
        element(var.azs, count.index),
      )
    },
    var.tags,
    var.db_subnet_tags,
  )
  depends_on = [time_sleep.wait_for_cidr_association]
}

resource "aws_subnet" "redis" {
  count = length(var.redis_subnets) > 0 ? length(var.redis_subnets) : 0

  vpc_id                          = local.vpc_id
  cidr_block                      = var.redis_subnets[count.index]
  availability_zone               = length(regexall("^[a-z]{2}-", element(var.azs, count.index))) > 0 ? element(var.azs, count.index) : null
  tags = merge(
    {
      "Name" = format(
        "${var.name}-${var.redis_subnet_suffix}-%s",
        element(var.azs, count.index),
      )
    },
    var.tags,
    var.redis_subnet_tags,
  )
  depends_on = [time_sleep.wait_for_cidr_association]
}

################################################################################
# Internet Gateway
################################################################################

resource "aws_internet_gateway" "this" {
  count = var.create_igw && length(var.public_subnets) > 0 ? 1 : 0

  vpc_id = local.vpc_id

  tags = merge(
    { "Name" = var.name },
    var.tags,
    var.igw_tags,
  )
}


################################################################################
# Route table association
################################################################################

resource "aws_route_table_association" "public" {
  count = length(var.public_subnets) > 0 ? length(var.public_subnets) : 0

  subnet_id      = element(aws_subnet.public[*].id, count.index)
  route_table_id = aws_route_table.public[0].id
}

resource "aws_route_table_association" "private" {
  count = length(var.private_subnets) > 0 ? length(var.private_subnets) : 0

  subnet_id = element(aws_subnet.private[*].id, count.index)
  route_table_id = element(
    aws_route_table.private[*].id,
    var.single_nat_gateway ? 0 : count.index,
  )
}

################################################################################
# Publiс routes
################################################################################

resource "aws_route_table" "public" {
  count = length(var.public_subnets) > 0 ? 1 : 0

  vpc_id = local.vpc_id

  tags = merge(
    { "Name" = "${var.name}-${var.public_subnet_suffix}" },
    var.tags,
    var.public_route_table_tags,
  )
}

resource "aws_route" "public_internet_gateway" {
  count = length(var.public_subnets) > 0 ? 1 : 0

  route_table_id         = aws_route_table.public[0].id
  destination_cidr_block = "0.0.0.0/0"
  gateway_id             = local.igw_id

  timeouts {
    create = "5m"
  }
}

################################################################################
# Private routes
# There are as many routing tables as the number of NAT gateways
################################################################################

resource "aws_route_table" "private" {
  count = local.max_subnet_length > 0 ? local.nat_gateway_count : 0

  vpc_id = local.vpc_id

  tags = merge(
    {
      "Name" = var.single_nat_gateway ? "${var.name}-${var.private_subnet_suffix}" : format(
        "${var.name}-${var.private_subnet_suffix}-%s",
        element(var.azs, count.index),
      )
    },
    var.tags,
    var.private_route_table_tags,
  )
}

################################################################################
# NAT Gateway
################################################################################

locals {
  nat_gateway_ips = var.reuse_nat_ips ? var.external_nat_ip_ids : try(aws_eip.nat[*].id, [])
}

resource "aws_eip" "nat" {
  count = var.enable_nat_gateway && false == var.reuse_nat_ips ? local.nat_gateway_count : 0

  #vpc = true
  domain = "vpc"

  tags = merge(
    {
      "Name" = format(
        "${var.name}-%s",
        element(var.azs, var.single_nat_gateway ? 0 : count.index),
      )
    },
    var.tags,
    var.nat_eip_tags,
  )
}

resource "aws_nat_gateway" "this" {
  count = var.enable_nat_gateway ? local.nat_gateway_count : 0

  allocation_id = element(
    local.nat_gateway_ips,
    var.single_nat_gateway ? 0 : count.index,
  )
  subnet_id = element(
    aws_subnet.public[*].id,
    var.single_nat_gateway ? 0 : count.index,
  )

  tags = merge(
    {
      "Name" = format(
        "${var.name}-%s",
        element(var.azs, var.single_nat_gateway ? 0 : count.index),
      )
    },
    var.tags,
    var.nat_gateway_tags,
  )

  depends_on = [aws_internet_gateway.this]
}

resource "aws_route" "private_nat_gateway" {
  count = var.enable_nat_gateway ? local.nat_gateway_count : 0

  route_table_id         = element(aws_route_table.private[*].id, count.index)
  destination_cidr_block = var.nat_gateway_destination_cidr_block
  nat_gateway_id         = element(aws_nat_gateway.this[*].id, count.index)

  timeouts {
    create = "5m"
  }
}


