# Terraform configuration for llm-eval-guardrails-platform

provider "aws" {
  region = var.aws_region
}

# VPC
resource "aws_vpc" "llm_eval" {
  cidr_block           = "10.0.0.0/16"
  enable_dns_hostnames = true
  enable_dns_support   = true

  tags = {
    Name = "llm-eval-vpc"
  }
}

# Subnets
resource "aws_subnet" "public" {
  count                   = 2
  vpc_id                  = aws_vpc.llm_eval.id
  cidr_block              = "10.0.${count.index}.0/24"
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name = "llm-eval-public-${count.index}"
  }
}

resource "aws_subnet" "private" {
  count             = 2
  vpc_id            = aws_vpc.llm_eval.id
  cidr_block        = "10.0.${count.index + 2}.0/24"
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name = "llm-eval-private-${count.index}"
  }
}

# EKS Cluster
resource "aws_eks_cluster" "llm_eval" {
  name     = "llm-eval-cluster"
  role_arn = aws_iam_role.eks_cluster.arn
  vpc_config {
    subnet_ids = concat(aws_subnet.public[*].id, aws_subnet.private[*].id)
  }

  depends_on = [
    aws_iam_role_policy_attachment.eks_cluster_policy
  ]
}

# EKS Node Group
resource "aws_eks_node_group" "llm_eval" {
  cluster_name    = aws_eks_cluster.llm_eval.name
  node_group_name = "llm-eval-nodes"
  node_role_arn   = aws_iam_role.eks_nodes.arn
  subnet_ids      = aws_subnet.private[*].id

  scaling_config {
    desired_size = 3
    max_size     = 5
    min_size     = 1
  }

  instance_types = ["t3.large"]

  depends_on = [
    aws_iam_role_policy_attachment.eks_nodes_policy
  ]
}

# ElastiCache Redis
resource "aws_elasticache_subnet_group" "llm_eval" {
  name       = "llm-eval-subnet-group"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_elasticache_replication_group" "llm_eval" {
  replication_group_id          = "llm-eval-redis"
  replication_group_description = "Redis for LLM Eval Platform"
  node_type                     = "cache.t3.medium"
  number_cache_clusters         = 1
  subnet_group_name             = aws_elasticache_subnet_group.llm_eval.name
  security_group_ids            = [aws_security_group.redis.id]
}

# RDS PostgreSQL with pgvector
resource "aws_db_subnet_group" "llm_eval" {
  name       = "llm-eval-db-subnet"
  subnet_ids = aws_subnet.private[*].id
}

resource "aws_security_group" "database" {
  name_prefix = "llm-eval-db"
  vpc_id      = aws_vpc.llm_eval.id

  ingress {
    from_port   = 5432
    to_port     = 5432
    protocol    = "tcp"
    cidr_blocks = ["10.0.0.0/16"]
  }
}

resource "aws_rds_cluster" "llm_eval" {
  cluster_identifier      = "llm-eval-db"
  engine                  = "aurora-postgresql"
  engine_version          = "15.4"
  database_name           = "llm_eval"
  master_username         = "admin"
  master_password         = var.db_password
  db_subnet_group_name    = aws_db_subnet_group.llm_eval.name
  vpc_security_group_ids  = [aws_security_group.database.id]
  skip_final_snapshot     = true
  apply_immediately       = true
}

# ClickHouse on EC2
resource "aws_instance" "clickhouse" {
  ami           = var.clickhouse_ami
  instance_type = "r5.large"
  subnet_id     = aws_subnet.private[0].id
  vpc_security_group_ids = [aws_security_group.clickhouse.id]

  tags = {
    Name = "llm-eval-clickhouse"
  }
}
