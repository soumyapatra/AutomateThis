

########################################
# Locals - Subnet Calculation
########################################

locals {
  # Public subnets start from index 0
  public_subnets = [
    for i in range(var.public_subnet_count) : {
      name           = "${var.var.vnet_name}-public-subnet-${i + 1}"
      address_prefix = cidrsubnet(var.vnet_cidr, 4, i) # /24 each
      type           = "public"
    }
  ]

  # Private subnets continue after public
  private_subnets = [
    for i in range(var.private_subnet_count) : {
      name           = "${var.var.vnet_name}-private-subnet-${i + 1}"
      address_prefix = cidrsubnet(var.vnet_cidr, 4, i + var.public_subnet_count)
      type           = "private"
    }
  ]

  all_subnets = concat(local.public_subnets, local.private_subnets)
}


########################################
# Networking Resources
########################################

# Virtual Network
resource "azurerm_virtual_network" "vnet" {
  name                = var.vnet_name
  resource_group_name = var.resource_group_name
  location            = var.location
  address_space       = [var.vnet_cidr]
}

# Subnets
resource "azurerm_subnet" "subnets" {
  for_each = { for subnet in local.all_subnets : subnet.name => subnet }

  name                 = each.value.name
  resource_group_name  = var.resource_group_name
  virtual_network_name = azurerm_virtual_network.vnet.name
  address_prefixes     = [each.value.address_prefix]
}

########################################
# Public Subnet Routing
########################################

# Route table for public subnets (internet-facing)
resource "azurerm_route_table" "public" {
  name                = "${var.vnet_name}-public-rt"
  location            = var.location
  resource_group_name = var.resource_group_name
}

# Default route to Internet
resource "azurerm_route" "public_internet" {
  name                   = "public-internet-route"
  resource_group_name    = var.resource_group_name
  route_table_name       = azurerm_route_table.public.name
  address_prefix         = "0.0.0.0/0"
  next_hop_type          = "Internet"
}

# Associate route table with each public subnet
resource "azurerm_subnet_route_table_association" "public" {
  for_each = { for s in local.public_subnets : s.name => s }

  subnet_id      = azurerm_subnet.subnets[each.key].id
  route_table_id = azurerm_route_table.public.id
}


########################################
# Private Subnet Routing via NAT
########################################

# Public IP for NAT Gateway
resource "azurerm_public_ip" "nat" {
  name                = "${var.vnet_name}-nat-ip"
  resource_group_name = var.resource_group_name
  location            = var.location
  allocation_method   = "Static"
  sku                 = "Standard"
}

# NAT Gateway
resource "azurerm_nat_gateway" "nat" {
  name                = "${var.vnet_name}-natgw"
  resource_group_name = var.resource_group_name
  location            = var.location
  sku_name            = "Standard"
#For production AKS or mission-critical workloads:
#Always use zones = ["1", "2", "3"] for zone-redundant NAT Gateway.
#For dev/test or cost-saving scenarios:
#zones = ["1"] is fine, even if workloads are spread across zones. Azure networking handles it.
  zones                   = [1]
}

# Associate NAT Gateway with private subnets
resource "azurerm_subnet_nat_gateway_association" "private" {
  for_each = { for s in local.private_subnets : s.name => s }

  subnet_id      = azurerm_subnet.subnets[each.key].id
  nat_gateway_id = azurerm_nat_gateway.nat.id
}

