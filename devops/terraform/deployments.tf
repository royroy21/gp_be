#############################################
# Postgres deployment
#############################################
resource "digitalocean_database_cluster" "postgres_deployment" {
  name                 = var.cluster_name
  engine               = "pg"
  version              = "15"
  size                 = "db-s-1vcpu-1gb"
  region               = var.region
  private_network_uuid = data.digitalocean_vpc.existing_vpc.id
  node_count           = 1
}

resource "null_resource" "postgres_setup_gis" {
  count = var.initial_deployment ? 1 : 0

  provisioner "local-exec" {
    command = <<EOT
      export PGPASSWORD='${digitalocean_database_cluster.postgres_deployment.password}'
      psql -h ${digitalocean_database_cluster.postgres_deployment.host} \
           -p ${digitalocean_database_cluster.postgres_deployment.port} \
           -U ${digitalocean_database_cluster.postgres_deployment.user} \
           -d ${digitalocean_database_cluster.postgres_deployment.database} \
           -c "DO \$\$ BEGIN IF NOT EXISTS (SELECT 1 FROM pg_extension WHERE extname = 'postgis') THEN CREATE EXTENSION postgis; END IF; END \$\$;"
    EOT
    environment = {
      PGPASSWORD = digitalocean_database_cluster.postgres_deployment.password
    }
  }

  depends_on = [digitalocean_database_cluster.postgres_deployment]
}

resource "null_resource" "postgres_setup_make_private" {
  count = var.initial_deployment ? 1 : 0

  provisioner "local-exec" {
    command = <<EOT
      sleep 30
      curl -X PATCH -H "Content-Type: application/json" \
           -H "Authorization: Bearer ${ var.do_token }" \
           -d '{"public":false}' \
           "https://api.digitalocean.com/v2/databases/${ digitalocean_database_cluster.postgres_deployment.id }/firewall"
    EOT
  }

  depends_on = [null_resource.postgres_setup_gis]
}

#############################################
# Redis deployment
#############################################
resource "kubectl_manifest" "redis_deployment" {
  yaml_body = file("${path.module}/kubernetes/deployments/redis.yaml")
}

#############################################
# Django deployment
#############################################
data "template_file" "django_deployment_yaml" {
  template = file("${path.module}/kubernetes/deployments/django.yaml")

  vars = {
    db_name                 = digitalocean_database_cluster.postgres_deployment.database
    db_user                 = digitalocean_database_cluster.postgres_deployment.user
    db_password             = digitalocean_database_cluster.postgres_deployment.password
    db_host                 = digitalocean_database_cluster.postgres_deployment.private_host
    db_port                 = tostring(digitalocean_database_cluster.postgres_deployment.port)
    aws_access_key_id       = var.do_spaces_access_id
    aws_secret_access_key   = var.do_spaces_secret_key
    aws_storage_bucket_name = digitalocean_spaces_bucket.bucket.name
    aws_bucket_domain_name  = digitalocean_spaces_bucket.bucket.bucket_domain_name
    aws_s3_region_name      = digitalocean_spaces_bucket.bucket.region
    django_image            = var.django_image
    django_secret           = var.django_secret
    frontend_domain         = var.frontend_domain
    backend_domain          = var.backend_domain
    email_host              = var.email_host
    email_port              = tostring(var.email_port)
    email_user              = var.email_user
    email_password          = var.email_password
    email_default_from      = var.email_default_from
    email_default_subject   = var.email_default_subject
    sentry_key              = var.sentry_key
    sentry_org              = var.sentry_org
    sentry_project          = var.sentry_project
  }
}

resource "kubectl_manifest" "django_deployment" {
  yaml_body = data.template_file.django_deployment_yaml.rendered
  sensitive_fields = [
      "spec.template.spec.containers.env"
  ]

  depends_on = [
    digitalocean_database_cluster.postgres_deployment,
    kubectl_manifest.redis_deployment,
    digitalocean_spaces_bucket.bucket,
    kubernetes_secret.dockerhub,
  ]
}

#############################################
# Nginx deployment
#############################################
data "template_file" "nginx_config_yaml" {
  template = var.initial_deployment ? file("${path.module}/kubernetes/configmaps/nginx_no_ssl.yaml") : file("${path.module}/kubernetes/configmaps/nginx.yaml")

  vars = {
    aws_bucket_domain_name = digitalocean_spaces_bucket.bucket.bucket_domain_name
    backend_domain         = var.backend_domain
  }
}

resource "kubectl_manifest" "nginx_config" {
  yaml_body = data.template_file.nginx_config_yaml.rendered
}

resource "kubectl_manifest" "nginx_initial_deployment" {
  count     = var.initial_deployment ? 1 : 0
  yaml_body = file("${path.module}/kubernetes/deployments/nginx_no_ssl.yaml")

  depends_on = [
    kubectl_manifest.django_deployment,
  ]
}

resource "kubectl_manifest" "nginx_deployment" {
  count     = var.initial_deployment ? 0 : 1
  yaml_body = file("${path.module}/kubernetes/deployments/nginx.yaml")

  depends_on = [
    kubectl_manifest.certificate,
  ]
}

#############################################
# Worker deployment
#############################################
data "template_file" "worker_deployment_yaml" {
  template = file("${path.module}/kubernetes/deployments/worker.yaml")

  vars = {
    db_name                 = digitalocean_database_cluster.postgres_deployment.database
    db_user                 = digitalocean_database_cluster.postgres_deployment.user
    db_password             = digitalocean_database_cluster.postgres_deployment.password
    db_host                 = digitalocean_database_cluster.postgres_deployment.private_host
    db_port                 = tostring(digitalocean_database_cluster.postgres_deployment.port)
    aws_access_key_id       = var.do_spaces_access_id
    aws_secret_access_key   = var.do_spaces_secret_key
    aws_storage_bucket_name = digitalocean_spaces_bucket.bucket.name
    aws_bucket_domain_name  = digitalocean_spaces_bucket.bucket.bucket_domain_name
    aws_s3_region_name      = digitalocean_spaces_bucket.bucket.region
    django_image            = var.django_image
    django_secret           = var.django_secret
    frontend_domain         = var.frontend_domain
    backend_domain          = var.backend_domain
    email_host              = var.email_host
    email_port              = tostring(var.email_port)
    email_user              = var.email_user
    email_password          = var.email_password
    email_default_from      = var.email_default_from
    email_default_subject   = var.email_default_subject
    sentry_key              = var.sentry_key
    sentry_org              = var.sentry_org
    sentry_project          = var.sentry_project
  }
}

resource "kubectl_manifest" "worker_deployment" {
  yaml_body = data.template_file.worker_deployment_yaml.rendered
  sensitive_fields = [
      "spec.template.spec.containers.env"
  ]

  depends_on = [
    kubectl_manifest.django_deployment,
  ]
}
