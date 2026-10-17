resource "aws_cloudwatch_log_group" "mcp" {
  name              = "/ecs/secure-enterprise-mcp"
  retention_in_days = 7
}