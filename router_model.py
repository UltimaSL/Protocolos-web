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
        "Accept": "application/yang-data+json",  # Solicita respuesta en formato JSON
        "Content-Type": "application/yang-data+json" # Especifica que el contenido es JSON
    }

    try:
        response = requests.get(
            url,
            headers=headers,
            auth=(username, password),
            verify=False  # Deshabilita la verificación de certificado SSL (¡SOLO PARA LABS!)
        )
        response.raise_for_status() # Lanza una excepción para errores HTTP (4xx o 5xx)
        return {"status": "success", "data": response.json()}
    except requests.exceptions.RequestException as e:
        return {"status": "error", "message": f"Error de conexión o RESTCONF: {e}"}
    except json.JSONDecodeError as e:
        return {"status": "error", "message": f"Respuesta del router no es JSON válida: {e}. Respuesta: {response.text[:200]}..."}

# --- Funciones de Parsing de Salida RESTCONF (JSON) ---

def parse_eigrp_neighbors_restconf(data):
    """
    Parsea los datos JSON de vecinos EIGRP y los formatea para mostrarlos.
    """
    if data["status"] != "success":
        return data

    neighbors_list = []
    try:
        # Navega por la estructura JSON para encontrar la lista de interfaces y vecinos
        instances = data["data"]["Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"]["eigrp-instance"]
        if instances:
            for instance in instances:
                if "eigrp-interface" in instance:
                    for interface in instance["eigrp-interface"]:
                        if "eigrp-nbr" in interface:
                            for neighbor in interface["eigrp-nbr"]:
                                neighbors_list.append({
                                    "afi": neighbor["afi"],
                                    "neighbor_address": neighbor["nbr-address"],
                                    "interface_local": interface["name"]
                                })
            return neighbors_list if neighbors_list else {"message": "No se encontraron vecinos EIGRP."}
    except KeyError:
        return {"message": "La estructura de los datos JSON no es la esperada."}
    
    return {"message": "No se encontraron vecinos EIGRP o los datos están vacíos."}


def parse_eigrp_routes_restconf(data):
    """
    Parsea los datos JSON de la tabla de topología/rutas EIGRP.
    """
    if data["status"] != "success":
        return data

    routes_list = []
    try:
        instances = data["data"]["Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"]["eigrp-instance"]
        if instances:
            for instance in instances:
                if "eigrp-topo" in instance:
                    for topo in instance["eigrp-topo"]:
                        # La tabla de topología a veces está anidada
                        # Esta parte necesitaría ser ajustada a la estructura exacta de la respuesta
                        # Por ahora, devolvemos el JSON de topología completo
                        routes_list.append(topo)
    except KeyError:
        return {"message": "La estructura de los datos JSON no es la esperada."}

    return routes_list if routes_list else {"message": "No se encontraron rutas EIGRP."}


def parse_eigrp_protocols_restconf(data):
    """
    Parsea los datos JSON de los parámetros de protocolo EIGRP.
    """
    if data["status"] != "success":
        return data

    try:
        instances = data["data"]["Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"]["eigrp-instance"]
        if instances:
            # Asumimos que solo hay una instancia de EIGRP por AS
            instance_data = instances[0]
            protocol_info = {
                "as_number": instance_data["as-num"],
                "router_id": f"{instance_data['router-id'] // 16777216}.{(instance_data['router-id'] >> 16) & 255}.{(instance_data['router-id'] >> 8) & 255}.{instance_data['router-id'] & 255}",
                "protocol_name": instance_data["afi"]
            }
            return protocol_info
    except KeyError:
        return {"message": "La estructura de los datos JSON no es la esperada."}

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