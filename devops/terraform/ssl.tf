#############################################
# Install cert-manager
#############################################
resource "helm_release" "cert_manager" {
  count      = var.initial_deployment ? 0 : 1
  name       = "cert-manager"
  repository = "https://charts.jetstack.io"
  chart      = "cert-manager"
  version    = "v1.15.1"
  namespace  = "default"

  create_namespace = true

  set {
    name  = "installCRDs"
    value = "true"
  }
}

#############################################
# Create an Issuer for Let's Encrypt
#############################################
data "template_file" "cert_manager_yaml" {
  template = file("${path.module}/kubernetes/ssl/cert_manager.yaml")

  vars = {
    email = var.email
  }
}

resource "kubectl_manifest" "cert_manager" {
  count     = var.initial_deployment ? 0 : 1
  yaml_body = data.template_file.cert_manager_yaml.rendered
  sensitive_fields = [
      "spec.acme.solvers.dns01.cloudflare.apiTokenSecretRef"
  ]

  depends_on = [
    helm_release.cert_manager,
    kubernetes_secret.cloudflare_api_token,
  ]
}

#############################################
# Create a Certificate Resource
#############################################
data "template_file" "certificate_yaml" {
  template = file("${path.module}/kubernetes/ssl/certificate.yaml")

  vars = {
    frontend_domain = var.frontend_domain
    backend_domain  = var.backend_domain
  }
}

resource "kubectl_manifest" "certificate" {
  count     = var.initial_deployment ? 0 : 1
  yaml_body = data.template_file.certificate_yaml.rendered

  depends_on = [
    kubectl_manifest.cert_manager,
  ]
}

#############################################
# Configure Ingress to Use the Certificate
#############################################
data "template_file" "ingress_yaml" {
  template = file("${path.module}/kubernetes/ssl/ingress.yaml")

  vars = {
    backend_domain  = var.backend_domain
  }
}

resource "kubectl_manifest" "ingress" {
  count     = var.initial_deployment ? 0 : 1
  yaml_body = data.template_file.ingress_yaml.rendered

  depends_on = [
    kubectl_manifest.cert_manager,
  ]
}
