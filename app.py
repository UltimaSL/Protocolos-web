# C:\xampp\htdocs\PaginaWeb-Examen\app.py
from flask import Flask, render_template, jsonify, request

import router_model
import config

app = Flask(__name__, static_folder='public', template_folder='templates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/eigrp_neighbors_v4', methods=['GET'])
def api_eigrp_neighbors():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data/eigrp-instance/as-num=10/eigrp-interface"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_neighbors_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_routes_v4', methods=['GET'])
def api_eigrp_routes():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data/eigrp-instance/as-num=10/eigrp-topo"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_routes_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_protocols_v4', methods=['GET'])
def api_eigrp_protocols():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data/eigrp-instance/as-num=10"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_protocols_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

@app.route('/api/eigrp_full_state_v4', methods=['GET'])
def api_eigrp_full_state():
    path = "Cisco-IOS-XE-eigrp-oper:eigrp-oper-data"
    raw_data = router_model.get_restconf_data(path)
    parsed_data = router_model.parse_eigrp_full_state_restconf(raw_data)
    return jsonify({"status": raw_data["status"], "data": parsed_data, "message": raw_data.get("message")})

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5101)