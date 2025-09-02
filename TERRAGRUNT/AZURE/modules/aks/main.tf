resource "azurerm_kubernetes_cluster" "aks" {
  name                = var.aks_name
  location            = var.location
  resource_group_name = var.resource_group_name
  dns_prefix          = var.dns_prefix
  kubernetes_version  = var.kubernetes_version

  default_node_pool {
    name                = "system"
    vm_size             = var.vm_size
    node_count          = var.node_count
    vnet_subnet_id      = element(var.private_subnet_ids, 0) # put system pool in 1 private subnet
    orchestrator_version = var.kubernetes_version
  }

  identity {
    type = "SystemAssigned"
  }

  network_profile {
    network_plugin     = "azure"   # or "kubenet"
    network_policy     = "azure"
    outbound_type      = "userDefinedRouting" # since NAT Gateway is used
    load_balancer_sku  = "standard"
  }

  role_based_access_control_enabled = true

}