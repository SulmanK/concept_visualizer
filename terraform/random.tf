/**
 * Random suffix for IAM resources to prevent name conflicts
 */
resource "random_string" "pool_suffix" {
  length  = 4
  special = false
  upper   = false
}
