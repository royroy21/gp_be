resource "kubernetes_secret" "dockerhub" {
  metadata {
    name = "dockerhub-config"
  }

  data = {
    ".dockerconfigjson" = file(var.dockerhub_config)
  }

  type = "kubernetes.io/dockerconfigjson"
}

resource "kubernetes_secret" "cloudflare_api_token" {
  count = var.initial_deployment ? 0 : 1

  metadata {
    name = "cloudflare-api-token-secret"
  }

  data = {
    api-token = var.cloudflare_api_token
  }

  type = "Opaque"

  depends_on = [
    helm_release.cert_manager,
  ]
}
