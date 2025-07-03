variable "name" {
  description = "The name to use for all the cluster resources"
  type        = string
}

variable "vpc_id" {
  description = "VPC Id"
  type        = string
}

variable "bastion_public_ip_list" {
  description = "bastion server public ip list"
  type = list(string)
}

variable "bastion_sg_id" {
  description = "bastion security group id"
  type = string
}

#variable "eks_sg_id" {
#  description = "EKS security group id"
#  type = string
#}

variable "prod_sg_id" {
  description = "Allow internal vpc traffic from this sg id"
  type = string
  default = "sg-id"
}

variable "prod_sg" {
  description = "Prod SG allowed to connect kube api server?"
  default = false
}
