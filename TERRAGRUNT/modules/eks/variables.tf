variable "name" {
  description = "The name to use for all the cluster resources"
  type        = string
}
variable "sg_id" {
  description = "EKS master security grp id"
  type    = list(string)
}
variable "subnets" {
  description = "EKS master subnet IDS list"
  type    = list(string)
}

variable "allow_ui_ip" {
  type = list(string)
  default = ["0.0.0.0/0"]
  description = "IP list to be allowed for K8s UI"
}

variable "eks_version" {
  type = string
  description = "EKS version"
  default = "1.22"
}
