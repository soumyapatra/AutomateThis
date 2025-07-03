variable "eks_name" {
}
variable "eks_endpoint" {
}
variable "eks_cert_auth_data" {
}
variable service_vars {
  type        = map(any)
  description = "Service vars"
}
variable service_list {
  type        = list(string)
  description = "Service List"
}
variable "env" {
}
variable "region" {
}

