from flask import Flask, jsonify, send_from_directory

app = Flask(__name__, static_folder='dist', static_url_path="/vue")

@app.route('/api/data')
def get_data():
    return jsonify({"message": "Hello from Flask!"})

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def static_proxy(path):
    return send_from_directory(app.static_folder, 'index.html')

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=9880)

