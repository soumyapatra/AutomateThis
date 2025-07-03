variable alias_domain_name {
  type        = string
  description = "CNAME to set as record"
  default = "NA"
}

variable sub_domain_name {
  type        = string
  description = "sub-domain name used for CNAME"
  default = "NA"
}

variable domain_name {
  type        = string
  description = "Host Zone Name"
  default = "NA"
}

variable vpc_id {
  type        = string
  description = "VPC ID that needed to ne associated with r53"
  default = "NA"
}

variable vpc_region {
  type        = string
  description = "VPC region"
  default = "NA"
}

variable create_record {
  type = bool
  default = false
}

variable associate_vpc {
  type = bool
  default = false
}
