import api
from flask import request
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="dist", static_url_path="/protein_turnover")


@app.route("/api/host_informations")
def get_data():
    return jsonify(api.api_host_informations())


@app.route("/api/test_clickhouse_connection", methods=["POST"])
def test_clickhouse_connection():
    data: dict = request.get_json()
    host = data.get("host")
    port = data.get("port")
    username = data.get("username")
    password = data.get("password")
    return jsonify(api.test_clickhouse_connection(host, port, username, password))


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9880)
