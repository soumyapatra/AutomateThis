# EKS currently documents this required userdata for EKS worker nodes to
# properly configure Kubernetes applications on the EC2 instance.
# We utilize a Terraform local here to simplify Base64 encoding this
# information into the AutoScaling Launch Configuration.
# More information: https://docs.aws.amazon.com/eks/latest/userguide/launch-workers.html
locals {
  worker-node-userdata = <<USERDATA
#!/bin/bash
set -o xtrace
/etc/eks/bootstrap.sh --apiserver-endpoint '${var.eks_endpoint}' --b64-cluster-ca '${var.cert_auth_data}' '${var.name}'
USERDATA
  eks_ami_name = "amazon-eks-node-${var.eks_version}-v*"
  ami_name = var.use_eks_default_image ? local.eks_ami_name : var.ami_name
  ami_owner_id = var.use_eks_default_image ? "602401143452" : var.ami_owner_id
}

data "aws_ami" "eks-worker" {
  filter {
    name   = "name"
    values = [local.ami_name]
  }
  most_recent = true
  owners      = [local.ami_owner_id] # Amazon EKS AMI Account ID
}

resource "aws_launch_configuration" "lc1" {
  associate_public_ip_address = false
  iam_instance_profile        = aws_iam_instance_profile.worker-node.name
  image_id                    = data.aws_ami.eks-worker.id
  instance_type               = var.instance_type
  name_prefix                 = "${var.name}_worker"
  security_groups             = var.worker_sg_ids
  user_data_base64            = base64encode(local.worker-node-userdata)
  key_name = "hyd-key-lp-sbox"
  root_block_device {
    encrypted   = true
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_autoscaling_group" "asg1" {
  desired_capacity     = var.desired_asg_size
  launch_configuration = aws_launch_configuration.lc1.id
  max_size             = var.max_asg_size
  min_size             = var.min_asg_size
  name                 = "${var.name}"
  vpc_zone_identifier  = var.subnets

  tag {
    key                 = "Name"
    value               = var.name
    propagate_at_launch = true
  }

  tag {
    key                 = "kubernetes.io/cluster/${var.eks_cluster_name}"
    value               = "owned"
    propagate_at_launch = true
  }

  tag {
    key                 = "k8s.io/cluster-autoscaler/enabled"
    value               = "true"
    propagate_at_launch = true
  }

  tag {
    key                 = "k8s.io/cluster-autoscaler/${var.eks_cluster_name}"
    value               = "owned"
    propagate_at_launch = true
  }

  tag {
    key                 = "eks:cluster-name"
    value               = "${var.eks_cluster_name}"
    propagate_at_launch = true
  }

}


#Worker IAM role

resource "aws_iam_role" "worker-node" {
  name = "${var.name}_worker_iam_role"

  assume_role_policy = <<POLICY
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
POLICY
}

#resource "aws_iam_policy" "autoscaler" {
#  name        = "${var.name}-autoscaler-policy"
#  description = "My test policy"
#
#  policy = <<EOT
#{
#    "Version": "2012-10-17",
#    "Statement": [
#        {
#            "Sid": "VisualEditor0",
#            "Effect": "Allow",
#            "Action": [
#                "autoscaling:SetDesiredCapacity",
#                "autoscaling:TerminateInstanceInAutoScalingGroup"
#            ],
#            "Resource": "*",
#            "Condition": {
#                "StringEquals": {
#                    "aws:ResourceTag/k8s.io/cluster-autoscaler/${var.name}": "owned"
#                }
#            }
#        },
#        {
#            "Sid": "VisualEditor1",
#            "Effect": "Allow",
#            "Action": [
#                "autoscaling:DescribeAutoScalingInstances",
#                "autoscaling:DescribeAutoScalingGroups",
#                "ec2:DescribeLaunchTemplateVersions",
#                "autoscaling:DescribeTags",
#                "autoscaling:DescribeLaunchConfigurations"
#            ],
#            "Resource": "*"
#        }
#    ]
#}
#EOT
#}

resource "aws_iam_role_policy_attachment" "worker-node-AmazonEKSWorkerNodePolicy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy"
  role       = aws_iam_role.worker-node.name
}

resource "aws_iam_role_policy_attachment" "worker-node-AmazonEKS_CNI_Policy" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy"
  role       = aws_iam_role.worker-node.name
}

resource "aws_iam_role_policy_attachment" "worker-node-AmazonEC2ContainerRegistryReadOnly" {
  policy_arn = "arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly"
  role       = aws_iam_role.worker-node.name
}

resource "aws_iam_instance_profile" "worker-node" {
  name = "${var.name}_instance_profile"
  role = aws_iam_role.worker-node.name
}
