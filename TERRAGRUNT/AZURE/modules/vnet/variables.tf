variable "resource_group_name" {
  type        = string
  description = "Resource group name where VNet will be created"
}

variable "location" {
  type        = string
  description = "Azure region for the VNet"
}

variable "vnet_name" {
  type        = string
  description = "Name of the virtual network"
}

variable "address_space" {
  type        = list(string)
  description = "Address space for the VNet"
}

variable "subnets" {
  type = list(object({
    name          = string
    address_prefix = string
  }))
  description = "List of subnet objects with name and address prefix"
}