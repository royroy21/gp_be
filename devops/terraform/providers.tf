terraform {
  required_providers {
    kubernetes = {
      source = "hashicorp/kubernetes"
      version = "2.30.0"
    }
    kubectl = {
      source  = "gavinbunney/kubectl"
      version = "1.14.0"
    }
    helm = {
      source  = "hashicorp/helm"
      version = "2.14.0"
    }
    template = {
      source = "hashicorp/template"
      version = "2.2.0"
    }
    digitalocean = {
      source = "digitalocean/digitalocean"
      version = "2.39.2"
    }
    cloudflare = {
      source = "cloudflare/cloudflare"
      version = "4.37.0"
    }
  }
}

provider "kubernetes" {
  host    = digitalocean_kubernetes_cluster.default_cluster.endpoint
  token   = digitalocean_kubernetes_cluster.default_cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(
    digitalocean_kubernetes_cluster.default_cluster.kube_config[0].cluster_ca_certificate
  )
}

provider "kubectl" {
  host    = digitalocean_kubernetes_cluster.default_cluster.endpoint
  token   = digitalocean_kubernetes_cluster.default_cluster.kube_config[0].token
  cluster_ca_certificate = base64decode(
    digitalocean_kubernetes_cluster.default_cluster.kube_config[0].cluster_ca_certificate
  )
}

provider "helm" {
  kubernetes {
    host  = digitalocean_kubernetes_cluster.default_cluster.endpoint
    token = digitalocean_kubernetes_cluster.default_cluster.kube_config[0].token
    cluster_ca_certificate = base64decode(
      digitalocean_kubernetes_cluster.default_cluster.kube_config[0].cluster_ca_certificate
    )
  }
}

provider "digitalocean" {
  token             = var.do_token
  spaces_access_id  = var.do_spaces_access_id
  spaces_secret_key = var.do_spaces_secret_key
}

provider "cloudflare" {
  api_token = var.cloudflare_api_token
}
