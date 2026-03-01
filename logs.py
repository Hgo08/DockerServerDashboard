from flask import Flask, jsonify, send_from_directory
import os

app = Flask(__name__)

LOG_FILE = "logs/app.log"  # Ruta a tu archivo de logs

# Sirve tu HTML
@app.route("/")
def index():
    return send_from_directory(".", "index.html")

# Endpoint que devuelve los logs
@app.route("/api/logs")
def get_logs():
    if not os.path.exists(LOG_FILE):
        return jsonify({"error": "Archivo de log no encontrado"}), 404

    with open(LOG_FILE, "r") as f:
        lines = f.readlines()

    # Devuelve las últimas 100 líneas
    logs = [line.strip() for line in lines[-100:] if line.strip()]
    return jsonify({"logs": logs})

# Endpoint para limpiar logs (opcional)
@app.route("/api/logs/clear", methods=["POST"])
def clear_logs():
    open(LOG_FILE, "w").close()
    return jsonify({"message": "Logs limpiados"})

if __name__ == "__main__":
    app.run(debug=True, port=5000)