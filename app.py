import api
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="dist", static_url_path="/protein_turnover")


@app.route("/api/host_informations")
def get_data():
    return jsonify(api.api_host_informations())


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, "index.html")


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9880)
