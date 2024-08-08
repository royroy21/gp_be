resource "cloudflare_record" "nginx_dns" {
  zone_id = var.cloudflare_zone_id
  name    = var.backend_domain
  value   = kubernetes_service.nginx_service.status[0].load_balancer[0].ingress[0].ip
  type    = "A"
  ttl     = 300

  depends_on = [
    kubernetes_service.nginx_service,
  ]
}
