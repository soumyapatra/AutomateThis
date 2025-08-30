variable instance_type {
  type        = string
  default     = "db.m5.xlarge"
  description = "RDS Instance type"
}
variable db_subnet_group {
  type        = string
  description = "RDS Subnet Group"
}
variable db_instance_identifier {
  type        = string
  description = "RDS Instance Identifier for Picking up Snaphots"
}

variable db_sg_id {
  type        = string
  description = "RDS Security Group"
}

variable "sub_domain_name" {
  type = string
}

variable "domain_name" {
  type = string
}
