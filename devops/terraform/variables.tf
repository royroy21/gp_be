#############################################
# Deployment
#############################################
variable "initial_deployment" {
  description = "Indicates whether this is the first deployment"
  type        = bool
}

#############################################
# Email
#############################################
variable "email" {
  description = "Email used for things like SLL and cloudflare"
  type        = string
}

variable email_host {
  description = "Email host used for sending emails from backend"
  type        = string
}

variable email_port {
  description = "Email port used for sending emails from backend"
  type        = number
}

variable email_user {
  description = "Email user used for sending emails from backend"
  type        = string
}

variable email_password {
  description = "Email password used for sending emails from backend"
  type        = string
}

variable email_default_from {
  description = "Email default from used for sending emails from backend"
  type        = string
}

variable email_default_subject {
  description = "Email default subject used for sending emails from backend"
  type        = string
}

#############################################
# Domains
#############################################
variable "frontend_domain" {
  description = "Frontend domain"
  type        = string
}

variable "do_app_platform_domain" {
  description = "DigitalOcean App Platform domain"
  type        = string
}

variable "backend_domain" {
  description = "Backend domain"
  type        = string
}

#############################################
# Digital Ocean
#############################################
variable "do_token" {
  description = "DigitalOcean API token"
  type        = string
}

variable "do_spaces_access_id" {
  description = "DigitalOcean Spaces access id"
  type        = string
}

variable "do_spaces_secret_key" {
  description = "DigitalOcean Spaces secret key"
  type        = string
}

#############################################
# Cloudflare
#############################################
variable "cloudflare_api_token" {
  description = "cloudflare API token"
  type        = string
}

variable "cloudflare_zone_id" {
  description = "cloudflare zone id"
  type        = string
}

#############################################
# Docker Hub
#############################################
variable "dockerhub_config" {
  description = "Full path to the dockerhub config file used to download images from private registry"
  type        = string
}

#############################################
# Cluster
#############################################
variable cluster_name {
  description = "The name of the kubernetes cluster to create"
  type        = string
}

variable region {
  description = "The digital ocean region slug for where to create resources"
  type        = string
  default     = "ams3"  # Amsterdam
}

variable min_nodes {
  description = "The minimum number of nodes in the default pool"
  type        = number
  default     = 5
}

variable max_nodes {
  description = "The maximum number of nodes in the default pool"
  type        = number
  default     = 10
}

variable default_node_size {
  description = "The default digital ocean node slug for each node in the default pool"
  type        = string
  default     = "s-1vcpu-2gb"
}

#############################################
# Django
#############################################
variable django_image {
  description = "The image used for Django and worker deployments"
  type        = string
}

variable django_secret {
  description = "The secret key used for Django and worker deployments"
  type        = string
}

#############################################
# Sentry
#############################################

variable sentry_key {
  description = "Sentry key"
  type        = string
}

variable sentry_org {
  description = "Sentry org"
  type        = string
}

variable sentry_project {
  description = "Sentry project"
  type        = string
}
