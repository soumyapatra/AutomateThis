variable service_vars {
  type        = map(any)
  description = "Service vars"
}
variable service_list {
  type        = list(string)
  description = "Service List"
}

variable "ingress_name" {
  type = string
}

variable "namespace" {
  type = string
  default = "default"
}

