#-----------------Instance Node--------------------#

resource "aws_eks_node_group" "node" {
  cluster_name    = "${var.eks_cluster_name}"
  node_group_name = "${var.name}"
  node_role_arn   = "${var.ng_role_arn}"
  subnet_ids      = "${var.private_subnets}"
  instance_types  = ["m5.xlarge"]
  tags = {
    Name = "${var.name}"
  }
  remote_access {
  	ec2_ssh_key = "${var.key_pair_name}"
	}	 
  scaling_config {
    desired_size = 2
    max_size     = 3
    min_size     = 1
  }

  # Ensure that IAM Role permissions are created before and deleted after EKS Node Group handling.
  # Otherwise, EKS will not be able to properly delete EC2 Instances and Elastic Network Interfaces.
}


