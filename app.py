import api
from flask import request, Response, stream_with_context
from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder="dist", static_url_path="/protein_turnover")
api.initialize_sqlite_db()

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

@app.route("/api/get_clickhouse_connection_info")
def get_clickhouse_connection_info():
    return jsonify(api.get_clickhouse_connection_info())

@app.route("/api/bool_check_clickhouse_connection")
def bool_check_clickhouse_connection():
    return jsonify(api.bool_check_clickhouse_connection())

@app.route("/api/find_all_mzML_pepxml_files_in_dir", methods=["POST"])
def find_all_mzML_pepxml_files_in_dir():
    data: dict = request.get_json()
    dir = data.get("dir")
    return jsonify(api.find_all_mzML_pepxml_files_in_dir(dir))

@app.route("/api/create_clickhouse_information", methods=["POST"])
def create_clickhouse_information():
    data: dict = request.get_json()
    values = data.get("data")
    return jsonify(api.create_clickhouse_information(values))

@app.route("/api/read_all_clickhouse_information")
def read_all_clickhouse_information():
    return jsonify(api.read_all_clickhouse_information())

@app.route("/api/delete_clickhouse_information", methods=["POST"])
def delete_clickhouse_information():
    data: dict = request.get_json()
    id = data.get("data")
    return jsonify(api.delete_clickhouse_information(id))

@app.route("/api/get_all_names_of_clickhouse_information")
def get_all_names_of_clickhouse_information():
    return jsonify(api.get_all_names_of_clickhouse_information())

@app.route("/api/get_clickhouse_information_by_name", methods=["POST"])
def get_clickhouse_information_by_name():
    data: dict = request.get_json()
    name = data.get("data")
    return jsonify(api.get_clickhouse_information_by_name(name))

@app.route('/api/load_files_sse')
def load_files_sse():
    file_paths = request.args.getlist('filePath')
    return Response(stream_with_context(api.load_files_sse(file_paths)), content_type='text/event-stream')

@app.route("/api/get_all_pepxml_table_names")
def get_all_pepxml_table_names():
    return jsonify(api.get_all_pepxml_table_names())

@app.route("/api/get_all_mzml_table_names")
def get_all_mzml_table_names():
    return jsonify(api.get_all_mzml_table_names())

@app.route("/api/get_history_dirs")
def get_history_dirs():
    return jsonify(api.get_history_dirs())

@app.route("/", defaults={"path": ""})
@app.route("/<path:path>")
def static_proxy(path):
    return send_from_directory(app.static_folder, "index.html")

if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0", port=9880)
