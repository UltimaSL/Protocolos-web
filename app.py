# C:\xampp\htdocs\PaginaWeb-Examen\app.py
from flask import Flask, render_template, jsonify, request
# No necesitamos Flask-CORS si Flask sirve la página y la API desde el mismo origen
# from flask_cors import CORS # Si la página web se sirviera desde un origen diferente (ej. XAMPP)

import router_model
import config

app = Flask(__name__, static_folder='public', template_folder='public') # Configura Flask para servir desde 'public'

# CORS(app) # Descomentar si aún tienes problemas de CORS y si el frontend se sirve por separado

# --- Rutas de API para el frontend ---

@app.route('/')
def index():
    return render_template('index.html') # Sirve index.html desde la carpeta 'public'

@app.route('/api/eigrp_neighbors_v4', methods=['GET'])
def api_eigrp_neighbors():
    # Obtener la salida CLI de 'show ip eigrp neighbors'
    command = "show ip eigrp neighbors"
    output = router_model.get_cli_output(command)
    
    # Parsear la salida
    parsed_data = router_model.parse_eigrp_neighbors(output)
    return jsonify({"status": "success", "data": parsed_data})

@app.route('/api/eigrp_routes_v4', methods=['GET'])
def api_eigrp_routes():
    command = "show ip route eigrp"
    output = router_model.get_cli_output(command)
    parsed_data = router_model.parse_eigrp_routes(output)
    return jsonify({"status": "success", "data": parsed_data})

@app.route('/api/eigrp_protocols_v4', methods=['GET'])
def api_eigrp_protocols():
    command = "show ip protocols"
    output = router_model.get_cli_output(command)
    parsed_data = router_model.parse_eigrp_protocols(output)
    return jsonify({"status": "success", "data": parsed_data})

# Puedes añadir más rutas de API aquí (ej. para topology)

if __name__ == '__main__':
    # Asegúrate de que las credenciales del router en config.py sean correctas
    app.run(debug=True, host='0.0.0.0', port=5000) # Flask correrá en puerto 5000, accesible desde localhost