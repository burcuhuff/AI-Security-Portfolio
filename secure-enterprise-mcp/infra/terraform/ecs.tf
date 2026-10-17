resource "aws_ecs_cluster" "mcp" {
  name = "mcp-sandbox"

  setting {
    name  = "containerInsights"
    value = "disabled"
  }
}

resource "aws_ecs_task_definition" "mcp" {
  family                   = "secure-enterprise-mcp"
  requires_compatibilities = ["FARGATE"]
  network_mode             = "awsvpc"
  cpu                      = "256"
  memory                   = "512"
  execution_role_arn       = aws_iam_role.mcp_execution.arn

  runtime_platform {
    operating_system_family = "LINUX"
    cpu_architecture        = "X86_64"
  }

  container_definitions = jsonencode([
    {
      name      = "mcp"
      image     = "${aws_ecr_repository.mcp.repository_url}@sha256:c1bfaa8bf3c659d56e06a141b291a4e03e1a2526d39f889b77fc58f7845a596c"
      essential = true
      user      = "10001:10001"

      environment = [
        {
          name  = "DEMO_USER"
          value = "restricted_user"
        }
      ]

      logConfiguration = {
        logDriver = "awslogs"
        options = {
          "awslogs-group"         = aws_cloudwatch_log_group.mcp.name
          "awslogs-region"        = "us-east-1"
          "awslogs-stream-prefix" = "mcp"
          "mode"                  = "blocking"
        }
      }
    }
  ])

  depends_on = [aws_iam_role_policy.mcp_execution]
}