#############################################
# Django service
#############################################
resource "kubernetes_service" "django_service" {
  metadata {
    name = "django"
  }
  spec {
    selector = {
      app = "django"
    }
    port {
      port        = 8000
      target_port = 8000
      protocol    = "TCP"
    }
  }

  depends_on = [
    kubectl_manifest.django_deployment,
  ]
}

#############################################
# Nginx service
#############################################
resource "kubernetes_service" "nginx_service" {
  metadata {
    name = "nginx"
  }
  spec {
    selector = {
      app = "nginx"
    }
    port {
      name        = "http"
      port        = 80
      target_port = 80
      protocol    = "TCP"
    }
    port {
      name        = "https"
      port        = 443
      target_port = 443
      protocol    = "TCP"
    }
    type = "LoadBalancer"
  }

  depends_on = [
    kubectl_manifest.nginx_deployment,
  ]
}

#############################################
# Postgres service
#############################################
resource "kubernetes_service" "postgres_service" {
  metadata {
    name = "postgres"
  }
  spec {
    selector = {
      app = "postgres"
    }
    port {
      port        = 5432
      target_port = 5432
      protocol    = "TCP"
    }
  }

  depends_on = [
    digitalocean_database_cluster.postgres_deployment,
  ]
}

#############################################
# Redis service
#############################################
resource "kubernetes_service" "redis_service" {
  metadata {
    name = "redis"
  }
  spec {
    selector = {
      app = "redis"
    }
    port {
      port        = 6379
      target_port = 6379
      protocol    = "TCP"
    }
  }

  depends_on = [
    kubectl_manifest.redis_deployment,
  ]
}
