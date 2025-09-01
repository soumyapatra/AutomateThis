variable "resource_group_name" {
  type        = string
  description = "Resource group for the AKS cluster"
}

variable "location" {
  type        = string
  description = "Azure region"
}

variable "aks_name" {
  type        = string
  description = "AKS cluster name"
}

variable "dns_prefix" {
  type        = string
  description = "DNS prefix for AKS API server"
}

variable "private_subnet_ids" {
  type        = list(string)
  description = "List of private subnet IDs where AKS nodes should run"
}

variable "kubernetes_version" {
  type        = string
  default     = "1.29.0"
}

variable "node_count" {
  type    = number
  default = 3
}

variable "vm_size" {
  type    = string
  default = "Standard_DS2_v2"
}

