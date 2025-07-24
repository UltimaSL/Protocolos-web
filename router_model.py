# C:\xampp\htdocs\PaginaWeb-Examen\router_model.py
from netmiko import ConnectHandler
import re # Para expresiones regulares, útil para parsing
import config # Importa la configuración del router

def get_cli_output(command):
    # --- Configuración del Dispositivo (obtenida de config.py) ---
    device = {
        "device_type": "cisco_ios", # Tipo de dispositivo para Netmiko
        "host": config.ROUTER_IP,
        "username": config.ROUTER_USERNAME,
        "password": config.ROUTER_PASSWORD,
        "port": config.ROUTER_PORT, # 22 para SSH, 23 para Telnet
        "secret": config.ROUTER_ENABLE_PASSWORD, # Contraseña de enable secret
        "global_delay_factor": 2 # Aumentar si hay problemas de timeout
    }

    try:
        net_connect = ConnectHandler(**device)
        net_connect.enable() # Entrar al modo enable
        output = net_connect.send_command(command, use_textfsm=False) # No usar textfsm por ahora
        net_connect.disconnect()
        return output
    except Exception as e:
        print(f"Error al conectar o ejecutar comando CLI: {e}")
        return f"Error al ejecutar comando: {command}. Error: {e}"

# --- Funciones de Parsing (EJEMPLOS BÁSICOS - NECESITAN MUCHO DETALLE Y PRUEBAS) ---
# El parsing de CLI es complejo y estas funciones son solo un punto de partida

def parse_eigrp_neighbors(output):
    neighbors = []
    # Ejemplo de patrón para 'show ip eigrp neighbors'
    # H   Address                 Interface              Hold Uptime   SRTT   RTO  Q  Seq
    # 0   10.1.1.2                GigabitEthernet1/0     10 00:01:30    1   500  0  5
    lines = output.splitlines()
    header_found = False
    for line in lines:
        if "H   Address" in line: # Identificar la línea del encabezado
            header_found = True
            continue
        if header_found and line.strip() and not line.startswith("IP-EIGRP"): # Asegurarse de que no sea el inicio de la salida o una línea vacía
            match = re.match(r"^\s*(\d+)\s+([\d.]+)\s+(\S+)\s+(\d+)\s+([\d:]+)\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)", line.strip())
            if match:
                neighbors.append({
                    "handle": match.group(1),
                    "address": match.group(2),
                    "interface": match.group(3),
                    "hold_time": match.group(4),
                    "uptime": match.group(5),
                    "srtt": match.group(6),
                    "rto": match.group(7),
                    "q_count": match.group(8),
                    "seq_num": match.group(9)
                })
            elif "EIGRP-IPv4 Neighbors for AS" in line: # Detener si llega al final de la tabla real
                break
    if not neighbors and "Error" in output: # Si el comando falló en el router
        return {"error": output}
    if not neighbors and "Invalid input detected" in output:
        return {"error": output} # Devuelve el error raw
    if not neighbors:
        return {"error": "No neighbors found or parsing failed. Raw output: " + output}
    return neighbors

def parse_eigrp_routes(output):
    routes = []
    # Este parsing es mucho más complejo y necesitará expresiones regulares sofisticadas
    # para extraer la dirección de red, métrica, via, etc.
    # Por ahora, para simplificar, devolveremos la salida raw si no se implementa un parsing complejo
    if "Error" in output or "Invalid input detected" in output:
        return {"error": output}
    if "D" not in output: # Si no hay rutas EIGRP, podría no ser un error
        return {"message": "No EIGRP routes found.", "raw_output": output}
    return {"raw_output": output, "message": "Parsing for routes not fully implemented. Displaying raw output."}


def parse_eigrp_protocols(output):
    protocols_info = {}
    # Este parsing también es complejo y necesitará expresiones regulares para cada campo
    # como AS number, advertised networks, administrative distance, etc.
    if "Error" in output or "Invalid input detected" in output:
        return {"error": output}
    
    # Ejemplos muy básicos de extracción
    as_match = re.search(r'Routing Protocol is "eigrp (\d+)"', output)
    if as_match:
        protocols_info['AS_Number'] = as_match.group(1)
    
    networks_match = re.search(r'Routing for Networks:\s*(.*?)(?:Routing Information Sources:|$)', output, re.DOTALL)
    if networks_match:
        networks_list = [net.strip() for net in networks_match.group(1).splitlines() if net.strip()]
        protocols_info['Advertised_Networks'] = networks_list

    admin_dist_match = re.search(r'Distance: internal (\d+) external (\d+)', output)
    if admin_dist_match:
        protocols_info['Admin_Distance_Internal'] = admin_dist_match.group(1)
        protocols_info['Admin_Distance_External'] = admin_dist_match.group(2)

    if not protocols_info:
        return {"raw_output": output, "message": "Parsing for protocols not fully implemented. Displaying raw output."}
    return protocols_info

# La tabla de topología es muy similar a la de rutas, puedes usar un parsing similar
def parse_eigrp_topology(output):
    if "Error" in output or "Invalid input detected" in output:
        return {"error": output}
    return {"raw_output": output, "message": "Parsing for topology not fully implemented. Displaying raw output."} # Placeholder