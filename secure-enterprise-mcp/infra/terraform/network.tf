resource "aws_vpc" "mcp" {
  cidr_block           = "10.42.0.0/16"
  enable_dns_support   = true
  enable_dns_hostnames = true

  tags = {
    Name = "mcp-sandbox"
  }
}

resource "aws_subnet" "mcp_public" {
  vpc_id                  = aws_vpc.mcp.id
  cidr_block              = "10.42.1.0/24"
  availability_zone       = "us-east-1a"
  map_public_ip_on_launch = false

  tags = {
    Name = "mcp-sandbox-public"
  }
}

resource "aws_internet_gateway" "mcp" {
  vpc_id = aws_vpc.mcp.id

  tags = {
    Name = "mcp-sandbox"
  }
}

resource "aws_route_table" "mcp_public" {
  vpc_id = aws_vpc.mcp.id

  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.mcp.id
  }

  tags = {
    Name = "mcp-sandbox-public"
  }
}

resource "aws_route_table_association" "mcp_public" {
  subnet_id      = aws_subnet.mcp_public.id
  route_table_id = aws_route_table.mcp_public.id
}

resource "aws_security_group" "mcp_task" {
  name        = "mcp-sandbox-task"
  description = "MCP demo task: no inbound access"
  vpc_id      = aws_vpc.mcp.id

  tags = {
    Name = "mcp-sandbox-task"
  }
}

resource "aws_vpc_security_group_egress_rule" "mcp_https" {
  security_group_id = aws_security_group.mcp_task.id
  description       = "Outbound HTTPS for image pulls and logs"

  cidr_ipv4   = "0.0.0.0/0"
  ip_protocol = "tcp"
  from_port   = 443
  to_port     = 443
}