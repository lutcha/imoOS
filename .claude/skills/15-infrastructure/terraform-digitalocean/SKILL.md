---
name: terraform-digitalocean
description: Recursos Terraform: do_app (App Platform), do_database_cluster (Postgres), do_spaces_bucket (S3), do_redis_cluster, variáveis de ambiente como variáveis TF.
argument-hint: "[environment]"
allowed-tools: Read, Edit, Bash, Glob, Grep
---

## Purpose

Gerir a infraestrutura do ImoOS na DigitalOcean como código com Terraform. A separação por ambiente (staging/prod) e o uso de variáveis TF para segredos garante configurações reprodutíveis e auditáveis.

## Code Pattern

```hcl
# terraform/main.tf
terraform {
  required_providers {
    digitalocean = {
      source  = "digitalocean/digitalocean"
      version = "~> 2.0"
    }
  }
  backend "s3" {
    endpoint = "https://fra1.digitaloceanspaces.com"
    bucket   = "imoos-terraform-state"
    key      = "imoos/${var.environment}/terraform.tfstate"
    region   = "us-east-1"  # placeholder — DO Spaces usa endpoint personalizado
    skip_credentials_validation = true
    skip_metadata_api_check     = true
  }
}

variable "environment" { default = "staging" }
variable "do_token" { sensitive = true }
variable "db_password" { sensitive = true }
variable "django_secret_key" { sensitive = true }
variable "stripe_secret_key" { sensitive = true }

provider "digitalocean" { token = var.do_token }
```

```hcl
# terraform/database.tf
resource "digitalocean_database_cluster" "postgres" {
  name       = "imoos-${var.environment}-db"
  engine     = "pg"
  version    = "15"
  size       = var.environment == "prod" ? "db-s-2vcpu-4gb" : "db-s-1vcpu-1gb"
  region     = "fra1"
  node_count = var.environment == "prod" ? 2 : 1

  maintenance_window {
    day  = "sunday"
    hour = "02:00:00"
  }
}

resource "digitalocean_database_db" "imoos" {
  cluster_id = digitalocean_database_cluster.postgres.id
  name       = "imoos"
}
```

```hcl
# terraform/storage.tf
resource "digitalocean_spaces_bucket" "media" {
  name   = "imoos-${var.environment}-media"
  region = "fra1"
  acl    = "private"

  lifecycle_rule {
    enabled = true
    expiration { days = var.environment == "prod" ? 0 : 30 }
  }
}

resource "digitalocean_spaces_bucket" "backups" {
  name   = "imoos-${var.environment}-backups"
  region = "fra1"
  acl    = "private"
}
```

```hcl
# terraform/redis.tf
resource "digitalocean_database_cluster" "redis" {
  name       = "imoos-${var.environment}-redis"
  engine     = "redis"
  version    = "7"
  size       = var.environment == "prod" ? "db-s-1vcpu-2gb" : "db-s-1vcpu-1gb"
  region     = "fra1"
  node_count = 1
}
```

```hcl
# terraform/app.tf
resource "digitalocean_app" "imoos" {
  spec {
    name   = "imoos-${var.environment}"
    region = "fra"

    service {
      name               = "web"
      instance_count     = var.environment == "prod" ? 2 : 1
      instance_size_slug = "professional-xs"
      http_port          = 8000

      env {
        key   = "DATABASE_URL"
        value = digitalocean_database_cluster.postgres.uri
        type  = "SECRET"
      }
      env {
        key   = "REDIS_URL"
        value = digitalocean_database_cluster.redis.uri
        type  = "SECRET"
      }
      env {
        key   = "DJANGO_SECRET_KEY"
        value = var.django_secret_key
        type  = "SECRET"
      }
    }
  }
}
```

```bash
# Comandos de gestão de infraestrutura
terraform init -backend-config="access_key=$SPACES_KEY" -backend-config="secret_key=$SPACES_SECRET"
terraform plan -var="environment=staging" -var="do_token=$DO_TOKEN"
terraform apply -var="environment=staging" -auto-approve
```

## Key Rules

- Guardar o estado Terraform em DO Spaces (não localmente) para trabalho em equipa.
- Usar `sensitive = true` em todas as variáveis de segredos — nunca aparecem nos logs do plan.
- Dimensionar para produção com `node_count = 2` no Postgres (alta disponibilidade).
- Nunca passar segredos como argumentos de linha de comando — usar ficheiro `terraform.tfvars` ou variáveis de ambiente.

## Anti-Pattern

```hcl
# ERRADO: hardcoded de segredos no ficheiro Terraform
resource "digitalocean_app" "imoos" {
  spec {
    env { key = "DJANGO_SECRET_KEY", value = "minha-chave-secreta-123" }  # commited no git!
  }
}
```
