variable "name" {
  description = "SG Name"
  type    = string
}

variable "instance_type" {
  description = "Instance type"
  type    = string
  default = "c5a.xlarge"
}

variable "eks_cluster_name" {
  description = "EKS Cluster Name"
  type    = string
}

variable "subnets" {
  description = "ASG Subnets"
  type    = list(string)
}

variable "eks_endpoint" {
  description = "EKS endpoint for Init script"
  type    = string
}

variable "cert_auth_data" {
  description = "EKS Auth Cert Data"
  type    = string
}

variable "worker_sg_ids" {
  description = "worker SG ID's list"
  type    = list(string)
}

variable "ami_name" {
  description = "AMI NAME"
  default = "amazon-eks-node-1.22-v*"
  type    = string
}

variable "eks_version" {
  description = "EKS Version"
  default = "1.22"
  type    = string
}

variable "ami_owner_id" {
  description = "AMI Owner Acct Id"
  type    = string
  default = "602401143452"
}

variable "desired_asg_size" {
  description = "Desired Asg Size"
  default = "3"
  type = string
}

variable "min_asg_size" {
  description = "Minimum Asg Size"
  default = "3"
  type = string
}

variable "max_asg_size" {
  description = "Maximum Asg Size"
  default = "6"
  type = string
}

variable "use_eks_default_image" {
  default = false
  type = bool
  description = "Use Amazon default EKS Image"
}
