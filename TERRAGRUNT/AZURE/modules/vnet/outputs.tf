output "vnet_id" {
  value = azurerm_virtual_network.vnet.id
}

output "subnet_ids" {
  value = { for s in azurerm_subnet.subnets : s.name => s.id }
}