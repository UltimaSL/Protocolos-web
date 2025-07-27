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
    # Usamos HTTP aquí porque el puerto 8080 en Azure VM se reenvía a HTTP puerto 80 en el router
    url = f"http://{router_ip}:{router_port}/restconf/data/{path_suffix}"

    headers = {
        "Accept": "application/yang-data+json",  # Solicita respuesta en formato JSON
        "Content-Type": "application/yang-data+json" # Especifica que el contenido es JSON (aunque sea GET)
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
        print(f"Error al conectar con RESTCONF para path '{path_suffix}': {e}")
        return {"status": "error", "message": f"Error de conexión o RESTCONF: {e}"}
    except json.JSONDecodeError as e:
        # Captura si la respuesta no es un JSON válido (ej., si hay un error en el router)
        print(f"Error al decodificar JSON de la respuesta para path '{path_suffix}': {e}. Respuesta RAW: {response.text}")
        return {"status": "error", "message": f"Respuesta del router no es JSON válida: {e}. Respuesta: {response.text[:200]}..."}


# --- Funciones de Parsing de Salida RESTCONF (JSON) ---
# Estas funciones procesarán los datos JSON recibidos de RESTCONF.
# Inicialmente, simplemente devolverán los datos JSON completos para que los veas.
# Un paso posterior sería extraer y formatear campos específicos.

def parse_eigrp_neighbors_restconf(data):
    """
    Parsea los datos JSON de vecinos EIGRP recibidos via RESTCONF.
    data: El objeto JSON con los datos de vecinos.
    """
    if "error" in data:
        return data # Devuelve el error directamente
    
    # Aquí iría la lógica para extraer campos específicos de los vecinos del JSON
    # Por ahora, devolvemos el JSON de datos completo o un mensaje si está vacío
    if data and "data" in data and data["data"]:
        return data["data"]
    else:
        return {"message": "No se encontraron vecinos EIGRP o los datos están vacíos."}

def parse_eigrp_routes_restconf(data):
    """
    Parsea los datos JSON de la tabla de topología/rutas EIGRP recibidos via RESTCONF.
    data: El objeto JSON con los datos de topología.
    """
    if "error" in data:
        return data
    
    if data and "data" in data and data["data"]:
        return data["data"]
    else:
        return {"message": "No se encontraron rutas EIGRP o los datos están vacíos."}

def parse_eigrp_protocols_restconf(data):
    """
    Parsea los datos JSON de los parámetros de protocolo EIGRP recibidos via RESTCONF.
    data: El objeto JSON con los datos de protocolo.
    """
    if "error" in data:
        return data

    if data and "data" in data and data["data"]:
        return data["data"]
    else:
        return {"message": "No se encontraron parámetros de protocolo EIGRP o los datos están vacíos."}

# La función para obtener el estado completo también devolverá el JSON completo
def parse_eigrp_full_state_restconf(data):
    """
    Devuelve el estado completo de EIGRP recibido via RESTCONF.
    data: El objeto JSON con el estado completo.
    """
    if "error" in data:
        return data
    
    if data and "data" in data and data["data"]:
        return data["data"]
    else:
        return {"message": "No se encontraron datos completos de EIGRP."}