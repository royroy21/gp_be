#############################################
# digital ocean spaces volume
#############################################
resource "digitalocean_spaces_bucket" "bucket" {
  name   = var.cluster_name
  region = var.region
}

resource "digitalocean_spaces_bucket_cors_configuration" "bucket" {
  bucket = digitalocean_spaces_bucket.bucket.name
  region = var.region

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["GET", "PUT", "POST", "DELETE"]
    allowed_origins = [
#      "https://${kubernetes_service.nginx_service.status[0].load_balancer[0].ingress[0].ip}",
#      "https://${kubernetes_service.django_service.spec[0].cluster_ip}",
      "https://${var.frontend_domain}",
      "https://${var.do_app_platform_domain}",
      "https://${var.backend_domain}"
    ]
    max_age_seconds = 3000
  }
}

resource "digitalocean_spaces_bucket_policy" "bucket" {
  bucket = digitalocean_spaces_bucket.bucket.name
  region = digitalocean_spaces_bucket.bucket.region

  policy = jsonencode({
    "Version": "2012-10-17",
    "Statement": [
      {
        "Effect": "Deny",
        "Principal": "*",
        "Action": "s3:*",
        "Resource": [
          "arn:aws:s3:::${digitalocean_spaces_bucket.bucket.name}/*"
        ],
        "Condition": {
          "StringNotLike": {
            "aws:Referer": [
              "https://${var.frontend_domain}/*",
              "https://${var.do_app_platform_domain}/*",
              "https://${var.backend_domain}/*"
            ]
          }
        }
      },
      {
        "Effect": "Allow",
        "Principal": "*",
        "Action": [
          "s3:GetObject",
          "s3:PutObject",
        ],
        "Resource": [
          "arn:aws:s3:::${digitalocean_spaces_bucket.bucket.name}/*"
        ],
        "Condition": {
          "StringLike": {
            "aws:Referer": [
              "https://${var.frontend_domain}/*",
              "https://${var.do_app_platform_domain}/*",
              "https://${var.backend_domain}/*"
            ]
          }
        }
      }
    ]
  })

  depends_on = [
    kubernetes_service.django_service,
    kubernetes_service.nginx_service,
  ]
}

#############################################
# redis volume
#############################################
resource "digitalocean_volume" "redis_volume" {
  name         = "redis"
  region       = var.region
  size         = 1
  description  = "Persistent volume for redis storage"
}

data "template_file" "redis_volume_yaml" {
  template = file("${path.module}/kubernetes/volumes/redis.yaml")

  vars = {
    volume_id = digitalocean_volume.redis_volume.id
  }
}

resource "kubectl_manifest" "redis_persistent_volume" {
  yaml_body = data.template_file.redis_volume_yaml.rendered
}

resource "kubectl_manifest" "redis_claim_volume" {
  yaml_body = file("${path.module}/kubernetes/volumes/redis_claim.yaml")

  depends_on = [
    kubectl_manifest.redis_persistent_volume,
  ]
}
