# C:\xampp\htdocs\PaginaWeb-Examen\app.py
from flask import Flask, render_template, jsonify, request

import router_model
import config

app = Flask(__name__, static_folder='public', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

# --- [ANOTACIÓN] Endpoints consolidados para ambos protocolos ---
# Estos endpoints traen la información de IPv4 e IPv6 con una sola llamada.

@app.route('/api/eigrp_neighbors_all', methods=['GET'])
def api_eigrp_neighbors_all():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
    raw_data = router_model.get_restconf_data(path)

    # Llamar a las funciones de parsing para IPv4 e IPv6 por separado
    ipv4_data = router_model.parse_eigrp_neighbors_restconf(raw_data, as_num=10, afi="eigrp-af-ipv4")
    ipv6_data = router_model.parse_eigrp_neighbors_restconf(raw_data, as_num=1, afi="eigrp-af-ipv6")

    # Unir los resultados en un solo JSON para el frontend
    combined_data = {
        "ipv4": ipv4_data,
        "ipv6": ipv6_data
    }

    return jsonify({"status": raw_data["status"], "data": combined_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_routes_all', methods=['GET'])
def api_eigrp_routes_all():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
    raw_data = router_model.get_restconf_data(path)

    ipv4_data = router_model.parse_eigrp_routes_restconf(raw_data, as_num=10, afi="eigrp-af-ipv4")
    ipv6_data = router_model.parse_eigrp_routes_restconf(raw_data, as_num=1, afi="eigrp-af-ipv6")

    combined_data = {
        "ipv4": ipv4_data,
        "ipv6": ipv6_data
    }

    return jsonify({"status": raw_data["status"], "data": combined_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_protocols_all', methods=['GET'])
def api_eigrp_protocols_all():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
    raw_data = router_model.get_restconf_data(path)
    
    ipv4_data = router_model.parse_eigrp_protocols_restconf(raw_data, as_num=10, afi="eigrp-af-ipv4")
    ipv6_data = router_model.parse_eigrp_protocols_restconf(raw_data, as_num=1, afi="eigrp-af-ipv6")

    combined_data = {
        "ipv4": ipv4_data,
        "ipv6": ipv6_data
    }

    return jsonify({"status": raw_data["status"], "data": combined_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_topology_all', methods=['GET'])
def api_eigrp_topology_all():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
    raw_data = router_model.get_restconf_data(path)

    ipv4_data = router_model.parse_eigrp_topology_restconf(raw_data, as_num=10, afi="eigrp-af-ipv4")
    ipv6_data = router_model.parse_eigrp_topology_restconf(raw_data, as_num=1, afi="eigrp-af-ipv6")

    combined_data = {
        "ipv4": ipv4_data,
        "ipv6": ipv6_data
    }
    
    return jsonify({"status": raw_data["status"], "data": combined_data, "message": raw_data.get("message")})

# --- [ANOTACIÓN] Endpoint para el estado completo de EIGRP ---
# Este endpoint seguirá trayendo todo el estado sin distinción de protocolo
@app.route('/api/eigrp_full_state', methods=['GET'])
def api_eigrp_full_state():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_full_state_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5101)