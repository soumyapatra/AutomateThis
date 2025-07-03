variable name {
  type        = string
  description = "node group name"
}

variable eks_cluster_name {
  type        = string
  description = "EKS cluster name"
}

variable private_subnets {
  type        = list(string)
  description = "private subnets"
}

variable key_pair_name {
  type        = string
  description = "ec2 ssh key"
}

variable instance_type {
  type        = string
  default     = "m5a.large"
  description = "instance type for node group"
}

variable ng_role_arn {
  type        = string
  description = "Node Group Instance Role Arn"
}
