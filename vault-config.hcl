# Vault Configuration for E-commerce Microservices

# HTTP listener
listener "tcp" {
  address = "0.0.0.0:8200"
  tls_disable = 0
  tls_cert_file = "/vault/certs/vault.crt"
  tls_key_file = "/vault/certs/vault.key"
}

# API listener for cluster communication
listener "tcp" {
  address = "0.0.0.0:8201"
  tls_disable = 0
  tls_cert_file = "/vault/certs/vault.crt"
  tls_key_file = "/vault/certs/vault.key"
}

# Storage backend
storage "file" {
  path = "/vault/data"
}

# UI configuration
ui = true

# API address
api_addr = "https://vault:8200"
cluster_addr = "https://vault:8201"

# Logging
log_level = "info"
log_file = "/vault/logs/vault.log"

# Disable mlock if needed for development
# disable_mlock = true
