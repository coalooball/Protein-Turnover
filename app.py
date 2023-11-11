from flask import Flask, jsonify, send_from_directory

app = Flask(__name__)

app = Flask(__name__, static_folder='static')

@app.route('/api/data')
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/')
def index():
    return send_from_directory(app.static_folder, 'index.html')

@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, path)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9880)

