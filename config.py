# /home/gns3user/monitoreo_web_gns3/config.py
# --- Configuración del Router CSR1000v ---
# ¡IMPORTANTE! Reemplaza con los valores reales de tu router CSR1000v y VM de Azure

ROUTER_IP = "192.168.31.130" # ¡IP PÚBLICA REAL DE TU VM DE AZURE! (Ej. 20.84.60.5)
ROUTER_USERNAME = "cisco" # Usuario RESTCONF configurado en el router CSR1000v
ROUTER_PASSWORD = "cisco" # Contraseña RESTCONF configurada en el router CSR1000v
ROUTER_ENABLE_PASSWORD = "" # Contraseña de enable secret del router CSR1000v (si se usara Netmiko)
ROUTER_PORT = 443 # Puerto público en la VM de Azure que reenvía a RESTCONF (80 en el router)
