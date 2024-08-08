# Terraform

## Initial deployment
NOTE! Remember to run with once with `intial_deployment` set to `true` then again with `false` on initial deployment. 
Further deployments need to have `intial_deployment` set to `false`

This is for a number of reasons such as SSL having to be set up after the initial deployment 
(servers need to exist before SSL can be applied).
