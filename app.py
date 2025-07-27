# C:\xampp\htdocs\PaginaWeb-Examen\app.py
from flask import Flask, render_template, jsonify, request
# No necesitamos Flask-CORS si Flask sirve la página y la API desde el mismo origen
# from flask_cors import CORS # Si la página web se sirviera desde un origen diferente (ej. XAMPP)

import router_model
import config # Todavía necesitamos config.py para las credenciales

app = Flask(__name__, static_folder='public', template_folder='templates') # Configura Flask para servir desde 'public'

# Si la página web se sirve desde un origen diferente (ej. XAMPP Apache)
# entonces sí necesitas CORS:
# CORS(app) 

# --- Rutas de API para el frontend ---

@app.route('/')
def index():
    return render_template('index.html') # Sirve index.html desde la carpeta 'public'

@app.route('/api/eigrp_neighbors_v4', methods=['GET'])
def api_eigrp_neighbors():
    # Path YANG para obtener vecinos EIGRPv4
    # ¡CRÍTICO! Ajusta instance-id y process-id si no son 1/1
    # Recuerda que tu AS en el router es 100, así que instance-id=100
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-state/eigrp-instance/instance-id=100/process-id=1/eigrp-neighbors"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_neighbors_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_routes_v4', methods=['GET'])
def api_eigrp_routes():
    # Path YANG para obtener tabla de topología (rutas) EIGRPv4
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-state/eigrp-instance/instance-id=100/process-id=1/topology-table"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_routes_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_protocols_v4', methods=['GET'])
def api_eigrp_protocols():
    # Path YANG para obtener parámetros de protocolo EIGRPv4
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-state/eigrp-instance/instance-id=100/process-id=1/eigrp-protocol"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_protocols_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_full_state_v4', methods=['GET'])
def api_eigrp_full_state():
    # Path YANG para obtener estado completo de EIGRP
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-state"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_full_state_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000) # Flask correrá en puerto 5000