variable "db_subnets" {
  type        = list(string)
  description = "DB Subnet List"
}

variable name {
  type        = string
  description = "cluster name"
}

variable db_sg_id {
  type        = string
  description = "DB Security Group"
}

variable eks_sg_id {
  type        = string
  description = "EKS Cluster Security Group"
}
variable service_vars {
  type        = map(any)
  description = "Service vars"
}
variable service_list {
  type        = list(string)
  description = "Service List"
}
variable "vpc_region" {
  type = string
}
variable "domain_name" {
  type = string
}
variable "vpc_id" {
  type = string
}
