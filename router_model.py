# C:\xampp\htdocs\PaginaWeb-Examen\router_model.py
import requests
import json
import config # Importa la configuración del router (ROUTER_IP, ROUTER_PORT, credenciales)

# Suprimir advertencias SSL para entornos de lab con certificados auto-firmados
# (SOLO PARA LABS, NUNCA EN PRODUCCIÓN)
requests.packages.urllib3.disable_warnings()

# --- Función para obtener datos vía RESTCONF ---
def get_restconf_data(path_suffix):
    """
    Realiza una petición GET a la API RESTCONF del router.
    path_suffix: La parte de la ruta YANG que se añade a la URL base de RESTCONF.
    """
    router_ip = config.ROUTER_IP
    router_port = config.ROUTER_PORT
    username = config.ROUTER_USERNAME
    password = config.ROUTER_PASSWORD
    
    # Construye la URL completa del endpoint RESTCONF
    # Usamos HTTPS y el puerto 443 (que se reenvía desde el 8080 público)
    url = f"https://{router_ip}:{router_port}/restconf/data/{path_suffix}"

    headers = {
        "Accept": "application/yang-data+json",
        "Content-Type": "application/yang-data+json"
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            auth=(username, password),
            verify=False
        )
        response.raise_for_status()
        return {"status": "success", "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Error de conexión o RESTCONF: {e}"}
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Respuesta del router no es JSON válida: {e}. Respuesta: {response.text[:200]}..."}

# --- Funciones de Parsing de Salida RESTCONF (JSON) ---

def parse_eigrp_neighbors_restconf(data, as_num, afi):
    """
    Parsea los datos JSON de vecinos EIGRP y los formatea para mostrarlos.
    as_num: El número de AS para la instancia EIGRP (ej., 10 o 1).
    afi: El tipo de dirección a buscar (ej., 'eigrp-af-ipv4' o 'eigrp-af-ipv6').
    """
    if data["status"] != "success":
        return data

    neighbors_list = []
    try:
        instances = data["data"]["Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"]["eigrp-instance"]
        if instances:
            # Busca la instancia EIGRP correcta (IPv4 o IPv6)
            target_instance = next(
                (inst for inst in instances if inst["as-num"] == as_num and inst["afi"] == afi),
                None
            )
            if target_instance and "eigrp-interface" in target_instance:
                for interface in target_instance["eigrp-interface"]:
                    if "eigrp-nbr" in interface:
                        for neighbor in interface["eigrp-nbr"]:
                            neighbors_list.append({
                                "as_num": target_instance.get("as-num"),
                                "neighbor_address": neighbor.get("nbr-address"),
                                "interface_local": interface.get("name"),
                                "hold_time": interface.get("hold-timer")
                            })
    except (KeyError, TypeError):
        return {"message": "La estructura de los datos JSON no es la esperada."}
    
    return neighbors_list if neighbors_list else {"message": "No se encontraron vecinos EIGRP o los datos están vacíos."}


def parse_eigrp_routes_restconf(data, as_num, afi):
    """
    [ANOTACIÓN] Esta función se encarga de extraer la 'tabla de enrutamiento' (solo las mejores rutas).
    data: El objeto JSON completo con los datos de EIGRP.
    as_num: El número de AS para la instancia EIGRP.
    afi: El tipo de dirección a buscar.
    """
    if data["status"] != "success":
        return data

    routes_list = []
    try:
        instances = data["data"]["Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"]["eigrp-instance"]
        if instances:
            target_instance = next(
                (inst for inst in instances if inst["as-num"] == as_num and inst["afi"] == afi),
                None
            )
            if target_instance and "eigrp-topo" in target_instance and "topology-route" in target_instance["eigrp-topo"][0]:
                routes_list = target_instance["eigrp-topo"][0]["topology-route"]
    except (KeyError, TypeError):
        return {"message": "La estructura de los datos JSON no es la esperada para rutas."}
    
    return routes_list if routes_list else {"message": "No se encontraron rutas EIGRP."}


def parse_eigrp_topology_restconf(data, as_num, afi):
    """
    [ANOTACIÓN] Esta función se encarga de extraer la 'tabla de topología' completa.
    data: El objeto JSON completo con los datos de EIGRP.
    as_num: El número de AS para la instancia EIGRP.
    afi: El tipo de dirección a buscar.
    """
    if data["status"] != "success":
        return data

    try:
        instances = data["data"]["Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"]["eigrp-instance"]
        if instances:
            target_instance = next(
                (inst for inst in instances if inst["as-num"] == as_num and inst["afi"] == afi),
                None
            )
            if target_instance and "eigrp-topo" in target_instance:
                return target_instance["eigrp-topo"]
    except (KeyError, TypeError):
        return {"message": "La estructura de los datos JSON no es la esperada para la topología."}

    return {"message": "No se encontró la tabla de topología EIGRP."}


def parse_eigrp_protocols_restconf(data, as_num, afi):
    """
    Parsea los datos JSON de los parámetros de protocolo EIGRP.
    as_num: El número de AS para la instancia EIGRP.
    afi: El tipo de dirección a buscar.
    """
    if data["status"] != "success":
        return data

    try:
        instances = data["data"]["Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"]["eigrp-instance"]
        if instances:
            target_instance = next(
                (inst for inst in instances if inst["as-num"] == as_num and inst["afi"] == afi),
                None
            )
            if target_instance:
                # Convertir el router-id de entero a formato IP legible
                router_id_int = target_instance["router-id"]
                router_id_ip = f"{router_id_int // 16777216}.{(router_id_int >> 16) & 255}.{(router_id_int >> 8) & 255}.{router_id_int & 255}"
                
                protocol_info = {
                    "as_number": target_instance.get("as-num"),
                    "router_id": router_id_ip,
                    "protocol_name": target_instance.get("afi"),
                    "max_paths": target_instance.get("maximum-path"),
                    "admin_distance": {
                        "internal": 90,
                        "external": 170
                    }
                }
                return protocol_info
    except (KeyError, TypeError):
        return {"message": "No se encontraron parámetros de protocolo EIGRP o la estructura JSON no es la esperada."}

    return {"message": "No se encontraron parámetros de protocolo EIGRP."}


def parse_eigrp_full_state_restconf(data):
    """
    Devuelve el estado completo de EIGRP recibido via RESTCONF.
    """
    if data["status"] != "success":
        return data
    
    if data and "data" in data and data["data"]:
        return data["data"]
    else:
        return {"message": "No se encontraron datos completos de EIGRP."}